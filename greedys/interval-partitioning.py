
from collections import namedtuple, defaultdict

job = namedtuple('job', ['start_time', 'duration', 'deadline', 'name']) # `name` in last position to use `<` on tuples for ordering.

def finish_time(jb):
    return jb.start_time + jb.duration

jobs = [ # some overlapping jobs...
    job(0, 3, 3, 'A'),
    job(0, 7, 7, 'B'),
    job(0, 3, 3, 'C'),
    job(4, 3, 10, 'D'),
    job(4, 6.5, 13.5, 'E'),
    job(9, 3, 12, 'F'),
    job(9, 3, 12, 'G'),
    job(11.5, 4.5, 16, 'H'),
    job(13, 3, 16, 'I'),
    job(13, 3, 16, 'J'),
] # every job ends at time 16.

label = {J.name: {'M₀', 'M₁', 'M₂', 'M₃', 'M₄'} for J in jobs} # each job can be assigned to any machine, initially.
label['A'] = {'M₃'} # job 'E' can be performed on the first machine only.
label['E'] = {'M₀'} # job 'E' can be performed on the first machine only.
label['D'] = {'M₁', 'M₂'} # job 'E' can be performed on the first machine only.

ordering = list(enumerate(sorted(jobs)))

busy = defaultdict(list)
busy.update({
    'M₀': [job(2, 3, None, 'cleaning'), job(14, 1, None, 'sunday')],
    'M₁': [job(5, 2, None, 'maintenance')],
})

def overlaps(I, J):
    return finish_time(I) > J.start_time # taking advantage of ordering

def ontime(J):
    return finish_time(J) <= J.deadline

def run(prefix, jobs, machine, label):

    if jobs: # still jobs to allocate.

        (j, J), *Js = jobs # unpacking.
        L = label[J.name].copy()

        for i, I in prefix: # O(n^2) complexity because of the last job; btw, preprocess of overlappings may help to check only those ones, getting a linear time.
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
                yield from run([(j, J_delayed)] + prefix, Js, machine.copy(), label)

        label[J.name] = L
    else:
        assert len(machine) == len(prefix)
        yield (machine, prefix)

def sol_handler(sol):
    
    machine, prefix = sol
    M = {m: [] for m in set(machine.values())}
    for j, J in prefix:
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

