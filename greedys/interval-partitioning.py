
from collections import namedtuple, defaultdict
from operator import attrgetter
import heapq, random, functools

random.seed(1 << 10)

# ________________________________________________________________________________
# Definitions

class OrderableBunch(object):

    def __init__(self, **kwds):
        if 'key' not in kwds:
            raise ValueError("The *key* parameter is mandatory for ordering")
        
        self.__dict__.update(kwds)

    def __lt__(self, other):
        key = self.key
        return key(self) < key(other)

job = namedtuple('job', ['start_time', 'duration', 'deadline', 'name']) 
dep = namedtuple('dep', ['name', 'jitter'])

def topological_sort(graph, key=len):
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

    q = [] # the priority queue

    G = defaultdict(set) 
    for node, parents in graph.items():
        v = OrderableBunch(priority=key(parents), value=node, 
                           key=attrgetter('priority'))
        heapq.heappush(q, v)
        for parent in parents:
            G[parent].add(v)

    while q:

        v = heapq.heappop(q) # some assertions on `priority`?

        node = v.value
        yield node

        children = G[node]

        if not children: continue

        for child in children:
            child.priority -= 1 # no need to use `heapindex` because we reference children directly.

        heapq.heapify(q)


def heapindex(q, item):
    """A generator of positions in which `item` occurs in `q`, in O(log n) time where n is `len(q)`.

    >>> import heapq
    >>> q = list(reversed(range(10)))
    >>> q
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> heapq.heapify(q)
    >>> q
    [0, 1, 3, 2, 5, 4, 7, 9, 6, 8]
    >>> list(heapindex(q, 4))
    [5]
    >>> list(map(lambda item: min(heapindex(q, item)), q))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> q = [1,3,3,3,10,10,2,2,4]
    >>> heapq.heapify(q)
    >>> q
    [1, 2, 2, 3, 10, 10, 3, 3, 4]
    >>> list(map(lambda item: list(heapindex(q, item)), [1,2,3,10,4]))
    [[0], [1, 2], [3, 7, 6], [4, 5], [8]]

    """

    L = len(q)
    stack = [0]

    while stack:
        k = stack.pop()
        
        if k >= L or q[k] > item:
            continue
        
        if q[k] == item:
            yield k

        stack.append(2*k+2)
        stack.append(2*k+1)

def by(jobs, prop_name):
    return dict(zip(map(attrgetter(prop_name), jobs), jobs))

def finish_time(jb):
    return jb.start_time + jb.duration

def overlaps(I, J):
    return finish_time(I) > J.start_time # taking advantage of ordering

def ontime(J):
    return finish_time(J) <= J.deadline

def ordering(jobs, deps):
    deps_graph = {J.name: [d.name for d in deps[J.name]] for J in jobs}
    DAG = topological_sort(deps_graph)
    jobs_by_name = by(jobs, 'name')
    return [jobs_by_name[job_name] for job_name in DAG]

def run(prefix, graph, machine, label, busy=defaultdict(list)):

    jobs, deps = graph # unpacking.

    if jobs: # still jobs to allocate.

        J_clean, *Js = jobs # unpacking.
        prefix_by_name = by(prefix, 'name')

        def ready_time(dp): # `dp` stands for `dependency`.
            D = prefix_by_name[dp.name]
            assert D.start_time is not None and D.name == dp.name
            return finish_time(D) if dp.jitter is None else (dp.jitter > 0 and D.start_time + dp.jitter)

        at_least = max(map(ready_time, deps[J_clean.name]), default=0)
        for st in range(max(at_least, J_clean.start_time or 0), 
                        J_clean.deadline - J_clean.duration + 1):

            J = J_clean._replace(start_time=st)

            L = label[J.name].copy()

            for I in filter(functools.partial(overlaps, J=J), prefix): # O(n^2) complexity because of the last job; btw, preprocess of overlappings may help to check only those ones, getting a linear time.
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
                    yield from run([J_delayed] + prefix, (Js, deps), machine.copy(), label, busy)

            label[J.name] = L
    else:
        assert len(machine) == len(prefix)
        assert all(map(lambda J: J.start_time is not None, prefix))
        yield (machine, prefix)

def sol_handler(sol):

    machine, prefix = sol
    M = {m: [] for m in set(machine.values())}
    for J in prefix:
        M[machine[J.name]].append(J)
    for k, v in M.items():
        v.sort()
    return M

# ________________________________________________________________________________
# Problem instance

def liviotti():
    jobs = [ # some overlapping jobs...
        job(None, 3, 3, 'A' ),
        job(None, 7, 7, 'B' ),
        job(None, 3, 3, 'C' ),
        job(None, 3, 10, 'D'),
        job(None, 6, 13, 'E'),
        job(None, 3, 12, 'F'),
        job(None, 3, 12, 'G'),
        job(None, 4, 16, 'H'),
        job(None, 3, 16, 'I'),
        job(None, 3, 16, 'J'),
    ] # every job ends at time 16.

    deps = defaultdict(list)

    print('Topological sort of jobs:\n', ordering(jobs, deps))

    label = {J.name: {'M₀', 'M₁', 'M₂', 'M₃', 'M₄'} for J in jobs} # each job can be assigned to any machine, initially.
    label['A'] = {'M₃'} # job 'E' can be performed on the first machine only.
    label['E'] = {'M₀'} # job 'E' can be performed on the first machine only.
    label['D'] = {'M₁', 'M₂'} # job 'E' can be performed on the first machine only.

    busy = defaultdict(list)
    busy.update({
        'M₀': [job(2, 3, None, 'cleaning'), 
               job(14, 1, None, 'sunday')],
        'M₁': [job(5, 2, None, 'maintenance')],
    })

    sols = run([], (ordering(jobs, deps), deps), {}, label.copy(), busy)

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


    for i, sol in zip(range(0), map(sol_handler, sols)):
        print(sol, '\n')



def simple_test():
    """

    >>> jobs = [job(None, 3, 3, 'A')]
    >>> deps = defaultdict(list)
    >>> sols = run([], (ordering(jobs, deps), deps), {}, {'A':{'M₀'}})
    >>> list(map(sol_handler, sols))
    [{'M₀': [job(start_time=0, duration=3, deadline=3, name='A')]}]

    >>> jobs = [job(1, 3, 6, 'A')]
    >>> sols = run([], (ordering(jobs, deps), deps), {}, {'A':{'M₀'}})
    >>> list(map(sol_handler, sols)) # doctest: +NORMALIZE_WHITESPACE
    [{'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}]

    >>> jobs.append(job(None, 3, 10, 'B'))
    >>> deps['B'] = [dep(name='A', jitter=None)]
    >>> sols = run([], (ordering(jobs, deps), deps), {}, {'A':{'M₀'}, 'B':{'M₀', 'M₁'}})
    >>> list(sorted(map(sol_handler, sols), key=len)) # doctest: +NORMALIZE_WHITESPACE
    [{'M₀': [job(start_time=1, duration=3, deadline=6, name='A'), 
             job(start_time=4, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A'), 
             job(start_time=5, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A'), 
             job(start_time=6, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=1, duration=3, deadline=6, name='A'), 
             job(start_time=7, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A'), 
             job(start_time=5, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A'), 
             job(start_time=6, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=2, duration=3, deadline=6, name='A'), 
             job(start_time=7, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A'), 
             job(start_time=6, duration=3, deadline=10, name='B')]}, 
     {'M₀': [job(start_time=3, duration=3, deadline=6, name='A'), 
             job(start_time=7, duration=3, deadline=10, name='B')]}, 
     {'M₁': [job(start_time=4, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=5, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=5, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}]
    >>> deps['B'] = [dep(name='A', jitter=1)]
    >>> sols = run([], (ordering(jobs, deps), deps), {}, {'A':{'M₀'}, 'B':{'M₁'}})
    >>> list(sorted(map(sol_handler, sols), key=len)) # doctest: +NORMALIZE_WHITESPACE
    [{'M₁': [job(start_time=2, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=3, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=4, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=5, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=1, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=3, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=4, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=5, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=2, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=4, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=5, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=6, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}, 
     {'M₁': [job(start_time=7, duration=3, deadline=10, name='B')], 
      'M₀': [job(start_time=3, duration=3, deadline=6, name='A')]}]

    """
    pass

