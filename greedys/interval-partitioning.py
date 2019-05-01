
from collections import namedtuple, defaultdict
import heapq

def dag(jobs):

    D = defaultdict(set)

    for j in jobs:
        for p in j.deps:
            D[p].add(j.name) # revert the connections

    return D

def topological_sort(jobs):

    forward_deps = dag(jobs)

    q = [] # the priority queue

    for job in jobs:
        heapq.heappush(q, (len(job.deps), job))

    while q:

        _, job = heapq.heappop(q)

        yield job

        dependents = forward_deps[job.name]

        if not dependents: continue

        for i in range(len(q)):
            priority, J = q[i]
            if J.name in dependents:
                q[i] = (priority - 1, J) 
        heapq.heapify(q) 

job = namedtuple('job', ['start_time', 'duration', 'deadline', 'name', 'deps']) # `name` in last position to use `<` on tuples for ordering.

def finish_time(jb):
    return jb.start_time + jb.duration

jobs = [ # some overlapping jobs...
    job(0, 3, 3, 'A', []),
    job(0, 7, 7, 'B', []),
    job(0, 3, 3, 'C', ['A']),
    job(4, 3, 10, 'D', ['B', 'C']),
    job(4, 6.5, 13.5, 'E', ['A']),
    job(9, 3, 12, 'F', ['C']),
    job(9, 3, 12, 'G', ['D']),
    job(11.5, 4.5, 16, 'H', ['C', 'G']),
    job(13, 3, 16, 'I', ['F', 'G']),
    job(13, 3, 16, 'J', ['H']),
] # every job ends at time 16.

print(list(topological_sort(jobs)))

label = {J.name: {'M₀', 'M₁', 'M₂', 'M₃', 'M₄'} for J in jobs} # each job can be assigned to any machine, initially.
label['A'] = {'M₃'} # job 'E' can be performed on the first machine only.
label['E'] = {'M₀'} # job 'E' can be performed on the first machine only.
label['D'] = {'M₁', 'M₂'} # job 'E' can be performed on the first machine only.

ordering = list(topological_sort(jobs))

busy = defaultdict(list)
busy.update({
    'M₀': [job(2, 3, None, 'cleaning', []), job(14, 1, None, 'sunday', [])],
    'M₁': [job(5, 2, None, 'maintenance', [])],
})

def overlaps(I, J):
    return finish_time(I) > J.start_time # taking advantage of ordering

def ontime(J):
    return finish_time(J) <= J.deadline

def run(prefix, jobs, machine, label):

    if jobs: # still jobs to allocate.

        J, *Js = jobs # unpacking.
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
                yield from run([J_delayed] + prefix, Js, machine.copy(), label)

        label[J.name] = L
    else:
        assert len(machine) == len(prefix)
        yield (machine, prefix)

def sol_handler(sol):
    
    machine, prefix = sol
    M = {m: [] for m in set(machine.values())}
    for J in prefix:
        M[machine[J.name]].append(J)
    for k, v in M.items():
        v.sort()
    return M

sols = sorted(run([], ordering, {}, label.copy()), 
              key=len, reverse=True) # execute for side effects on the list `sols`.

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
for sol in map(sol_handler, sols):
    print(sol, '\n')

