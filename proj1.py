import sys

from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.card import CardEnc, EncType

class Task:
    
    def __init__(self, task_number, release_time, processing_time, deadline_time, number_fragments, fragments, dependencies):
        self.task_number = task_number
        self.release_time = release_time
        self.processing_time = processing_time
        self.deadline_time = deadline_time
        self.number_fragments = number_fragments
        self.fragments = fragments
        self.dependencies = dependencies

    def __str__(self):
        return "TN = {0}, RT = {1}, PT = {2}, DT = {3}, NF = {4}, FPT = {5}, D = {6}".format(self.task_number, self.release_time, self.processing_time, self.deadline_time, self.number_fragments, self.fragments, self.dependencies)

# job.sms mus have a new line at the end
def load_tasks(lines):
    tasks = []
    number_of_tasks = int(lines.readline())

    for line_number, line in enumerate(lines):
        l = [int(x) for x in line[:-1].split(" ")]
        
        tasks.append(Task(line_number + 1, l[0], l[1], l[2], l[3], l[4:], []))

        if line_number + 1 == number_of_tasks:
            break

    for line_number, line in enumerate(lines):
        d_line = [int(x) for x in line[:-1].split(" ")]
        
        for dependency_id in d_line[1:]:
            #tasks[line_number].dependencies.append(tasks[dependency_id - 1]) # To put the hole object in the dependencies list
            tasks[line_number].dependencies.append(dependency_id) # To put the task id in the dependencies list

    return tasks


def max_deadline_time(tasks):
    max_deadline = -1
    for task in tasks:
        if task.deadline_time > max_deadline:
            max_deadline = task.deadline_time

    return max_deadline


def create_literals_data_structure(tasks, max_deadline):
    literals = []
    counter = 0

    for i in range(max_deadline):
        literals.append([])

        for idx, task in enumerate(tasks):
            literals[i].append([])

            for f in task.fragments:
                counter += 1
                literals[i][idx].append(counter)

    return literals


if __name__ == "__main__":
    tasks = load_tasks(sys.stdin)
    for task in tasks:
        print(task)
    
    # txyz
    # x = time
    # y = task
    # z = fragment
    literals = create_literals_data_structure(tasks, max_deadline_time(tasks))
    for time in literals:
        print(time)