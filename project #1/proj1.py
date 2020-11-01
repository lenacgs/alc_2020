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
        l = [int(x) for x in line[:-1].split()]
        tasks.append(Task(line_number + 1, l[0], l[1], l[2], l[3], l[4:], []))
        if line_number + 1 == number_of_tasks:
            break

    for line_number, line in enumerate(lines):
        d_line = [int(x) for x in line[:-1].split()]
        for dependency_id in d_line[1:]:
            #tasks[line_number].dependencies.append(tasks[dependency_id - 1]) # To put the hole object in the dependencies list
            tasks[line_number].dependencies.append(dependency_id) # To put the task id in the dependencies list

    return tasks


def max_deadline_time(tasks):
    max_deadline = 0
    for task in tasks:
        if task.deadline_time > max_deadline:
            max_deadline = task.deadline_time

    return max_deadline


def count_total_fragments(tasks):
    total = 0

    for task in tasks:
        total += task.number_fragments

    return total


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
    
    # Txyz
    # x = time
    # y = task
    # z = fragment
    max_deadline = max_deadline_time(tasks)
    literals = create_literals_data_structure(tasks, max_deadline)
    total_number_fragments =  count_total_fragments(tasks)

    solver = RC2(WCNF())
    
    for task in tasks:
        # Constraints to ensure that tasks can only be executed after their release time
        for time in range(task.release_time):
            for fragment in range(task.number_fragments):
                solver.add_clause([-literals[time][task.task_number - 1][fragment]])

        # Constraints to ensure that tasks can't be executed after their deadline
        for time in range(task.deadline_time, max_deadline):
            for fragment in range(task.number_fragments):
                solver.add_clause([-literals[time][task.task_number - 1][fragment]])


    # Constraints to ensure that only one fragment is executed at a time
    for i in range(max_deadline):
        time_literals = []
        for task in tasks:
            time_literals.extend(literals[i][task.task_number - 1])

        # Use EncType.bitwise for performance optimization
        enc = CardEnc.atmost(lits=time_literals, bound=1, encoding=EncType.pairwise)
        for clause in enc.clauses:
            solver.add_clause(clause)

    #Constraints to deal with tasks' dependencies
    for i in range(max_deadline):
        for task in tasks:
            for dep in task.dependencies:
                clause = []
                for j in range(i):
                    clause.append(literals[j][dep - 1][-1])
                clause.append(-literals[i][task.task_number - 1][0])
                #the task in the current time can only execute if the dependency executed before
                solver.add_clause(clause)

    # Soft clauses
    # Should to be altered to last fragment of every task
    for i in range(max_deadline):
        for t in tasks:
            for item in range(t.number_fragments):
                solver.add_clause([literals[i][t.task_number - 1][item]], weight=1)
        
    # Print the output
    solution = solver.compute()
    print("Model:", solution, "\n")
        
    output = []
    for i in range(len(tasks)):
        output.append([])

    task_offset = 0
    for time in range(max_deadline):
        for task in tasks:
            for fragment in range(task.number_fragments):
                if solution[time * total_number_fragments + task_offset] > 0:
                    output[task.task_number - 1].append(str(time))
                task_offset += 1
        task_offset = 0
    
    print(len(output) - output.count([]))
    for index, task_times in enumerate(output):
        if not task_times:
            continue
        print(index + 1, " ".join(task_times))

    #print("Cost:", solver.cost)
            