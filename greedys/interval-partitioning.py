
from collections import namedtuple

job = namedtuple('job', ['start_time', 'finish_time', 'name']) # `name` in last position to use `<` on tuples for ordering.

jobs = [ # some overlapping jobs...
    job(0, 3, 'A'),
    job(0, 7, 'B'),
    job(0, 3, 'C'),
    job(4, 7, 'D'),
    job(4, 10.5, 'E'),
    job(9, 12, 'F'),
    job(9, 12, 'G'),
    job(11.5, 16, 'H'),
    job(13, 16, 'I'),
    job(13, 16, 'J'),
] # everything ends at time 16.

ordering = sorted(jobs)
#print(ordering)

label = {J: {'M₀', 'M₁', 'M₂', 'M₃', 'M₄'} for J in jobs} # each job can be assigned to any machine.

machine = {} # answers.

def overlaps(I, J):
    return I.finish_time > J.start_time # taking advantage of ordering

for j, J in enumerate(ordering): # a greedy algorithm because the ordering is fixed and just one pass over it.
    for i, I in enumerate(ordering[:j]): # O(n^2) complexity because of the last job; btw, preprocess of overlappings may help to check only those ones, getting a linear time.
        if overlaps(I, J):
            label[J] -= {machine[I]} # remove the machine on which job `I` is allocated for possibilities about job `J`.
    machine[J] = label[J].pop() # let `pop` raises an exception if there is not an available label.

print(machine) # show results.

