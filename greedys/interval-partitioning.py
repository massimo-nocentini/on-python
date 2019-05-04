
from collections import namedtuple, defaultdict
from operator import attrgetter
import heapq, random

random.seed(1 << 10)

# ________________________________________________________________________________
# Definitions

job = namedtuple('job', ['start_time', 'duration', 'deadline', 'name', 'deps']) # `name` in last position to use `<` on tuples for ordering.

def children_repr(graph):

    D = defaultdict(set)

    for node, parents in graph.items():
        for parent in parents:
            D[parent].add(node) # revert the connections

    return D

def topological_sort(graph):
    """Topological sort.

    >>> G = {
    ...     'v₁': set(),
    ...     'v₂': set(),
    ...     'v₃': {'v₂'},
    ...     'v₄': {'v₁','v₃'},
    ...     'v₅': {'v₁','v₂','v₃','v₄'},
    ...     'v₆': {'v₂','v₅'},
    ...     'v₇': {'v₁','v₅','v₆'}
    ... }
    >>> list(topological_sort(G))
    ['v₁', 'v₂', 'v₃', 'v₄', 'v₅', 'v₆', 'v₇']

    """

    rev_graph = children_repr(graph)

    q = [] # the priority queue

    for node, parents in graph.items():
        tiebreak = random.random()
        priority = len(parents), tiebreak
        heapq.heappush(q, (priority, node))

    while q:

        _, node = heapq.heappop(q)

        yield node

        children = rev_graph[node]

        if not children: continue

        for i in range(len(q)):
            (length, tiebreak), child = q[i]
            if child in children:
                q[i] = ((length - 1, tiebreak), child)

        heapq.heapify(q)

def by(jobs, prop_name):
    return dict(zip(map(attrgetter(prop_name), jobs), jobs))

def finish_time(jb):
    return jb.start_time + jb.duration

def overlaps(I, J):
    return finish_time(I) > J.start_time # taking advantage of ordering

def ontime(J):
    return finish_time(J) <= J.deadline

def ordering(jobs):
    jobs_by_name = by(jobs, 'name')
    deps_graph = {J.name: set(J.deps) for J in jobs}
    DAG = topological_sort(deps_graph)
    return [jobs_by_name[job_name] for job_name in DAG]

def run(prefix, jobs, machine, label, busy=defaultdict(list)):

    if jobs: # still jobs to allocate.

        J_clean, *Js = jobs # unpacking.
        prefix_by_name = by(prefix, 'name')

        def ready_time(name):
            J = prefix_by_name[name]
            assert J.start_time is not None
            return finish_time(J)

        at_least = max(map(ready_time, J_clean.deps), default=0)
        for st in range(at_least, J_clean.deadline - J_clean.duration + 1):

            J = J_clean._replace(start_time=st)
            #print('attempt to start job {} at {}'.format(J.name, J.start_time))

            L = label[J.name].copy()

            for I in prefix: # O(n^2) complexity because of the last job; btw, preprocess of overlappings may help to check only those ones, getting a linear time.
                if overlaps(I, J):
                    label[J.name] -= {machine[I.name]} # remove the machine on which job `I` is allocated for possibilities about job `J`.

            for l in label[J.name]:

                J_delayed = J
                for B in busy[l]:
                    if overlaps(J_delayed, B):
                        J_delayed = J_delayed._replace(duration=J_delayed.duration + B.duration)
                    else:
                        break # assuming busy jobs are ordered too.

                if ontime(J_delayed):
                    machine[J.name] = l # an attempt to allocate job `J` on machine `l`.
                    yield from run([J_delayed] + prefix, Js, machine.copy(), label, busy)

            label[J.name] = L
    else:
        assert len(machine) == len(prefix)
        assert all(map(lambda J: J.start_time is not None, prefix))
        yield (machine, prefix)


# ________________________________________________________________________________
# Problem instance

jobs = [ # some overlapping jobs...
    job(None, 3, 3, 'A', []),
    job(None, 7, 7, 'B', []),
    job(None, 3, 3, 'C', []),
    job(None, 3, 10, 'D', []),
    job(None, 6, 13, 'E', []),
    job(None, 3, 12, 'F', []),
    job(None, 3, 12, 'G', []),
    job(None, 4, 16, 'H', []),
    job(None, 3, 16, 'I', []),
    job(None, 3, 16, 'J', []),
] # every job ends at time 16.

print('Topological sort of jobs:\n', ordering(jobs))

label = {J.name: {'M₀', 'M₁', 'M₂', 'M₃', 'M₄'} for J in jobs} # each job can be assigned to any machine, initially.
label['A'] = {'M₃'} # job 'E' can be performed on the first machine only.
label['E'] = {'M₀'} # job 'E' can be performed on the first machine only.
label['D'] = {'M₁', 'M₂'} # job 'E' can be performed on the first machine only.

busy = defaultdict(list)
busy.update({
    'M₀': [job(2, 3, None, 'cleaning', []), job(14, 1, None, 'sunday', [])],
    'M₁': [job(5, 2, None, 'maintenance', [])],
})

#sols = sorted(run([], ordering, {}, label.copy(), busy),
              #key=len, reverse=True) # execute for side effects on the list `sols`.

sols = run([], ordering(jobs), {}, label.copy(), busy)

"""
print(
    list(zip(sorted(map(lambda sol: (len(set(sol.values())), sol), sols),
                    key=lambda p: p[0]),
             range(10)))) # show results.
"""

"""
for sol in reversed(list(sorted(map(lambda sol: (len(set(sol.values())), sol), sols),
                    key=lambda p: p[0]))): # show results.
    print(sol)
"""

def sol_handler(sol):

    machine, prefix = sol
    M = {m: [] for m in set(machine.values())}
    for J in prefix:
        M[machine[J.name]].append(J)
    for k, v in M.items():
        v.sort()
    return M

for i, sol in zip(range(0), map(sol_handler, sols)):
    print(sol, '\n')

def simple_test():
    """

    >>> jobs = [job(None, 3, 3, 'A', [])]
    >>> sols = run([], ordering(jobs), {}, {'A':['M₀']})
    >>> list(map(sol_handler, sols))
    [{'M₀': [job(start_time=0, duration=3, deadline=3, name='A', deps=[])]}]

    >>> jobs = [job(None, 3, 6, 'A', [])]
    >>> sols = run([], ordering(jobs), {}, {'A':['M₀']})
    >>> list(map(sol_handler, sols))
    [{'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])]}, {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[])]}, {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[])]}, {'M₀': [job(start_time=3, duration=3, deadline=6, name='A', deps=[])]}]

    >>> jobs.append(job(None, 3, 10, 'B', ['A']))
    >>> sols = run([], ordering(jobs), {}, {'A':['M₀'], 'B':['M₀', 'M₁']})
    >>> list(sorted(map(sol_handler, sols), key=len)) # doctest: +NORMALIZE_WHITESPACE
    [{'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[]), job(start_time=3, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[]), job(start_time=4, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[]), job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[]), job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[]), job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[]), job(start_time=4, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[]), job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[]), job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[]), job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[]), job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[]), job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[]), job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A', deps=[]), job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A', deps=[]), job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=3, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=4, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=0, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=4, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=5, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=6, duration=3, deadline=10, name='B', deps=['A'])]},
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A', deps=[])], 'M₁': [job(start_time=7, duration=3, deadline=10, name='B', deps=['A'])]}]

    """
    pass

