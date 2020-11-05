import sys
import time as tm

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


def max_id_in_clause(clause):
    max_id = max(clause)
    min_id = min(clause)

    if abs(max_id) > abs(min_id):
        return max_id
    else:
        return min_id


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

    # for literal in literals:
    #     print(literal)
    # print("")





    # Constraints to ensure that fragments > 1 are executed sequentialy
    for task in tasks:
        for index, duration in enumerate(task.fragments):
            for time in range(task.release_time, task.deadline_time):
                c = []
                if duration > 1:
                    c.append(-literals[time][task.task_number - 1][index])
                    
                    if time > 0:
                        c.append(literals[time - 1][task.task_number - 1][index])
                    
                    if time + (duration - 1) < max_deadline:
                        for t in range(time + 1, time + duration):
                            c.append(literals[t][task.task_number - 1][index])
                            #print(c)
                            solver.add_clause(c)
                            c = c[:-1]
                    else:
                        #print(c)
                        solver.add_clause(c)


    # Constraints to ensure that fragments are executed in order
    for task in tasks:
        for index, duration in enumerate(task.fragments):
            for time in range(task.release_time, task.deadline_time):
                c = []
                if index != 0:
                    c.append(-literals[time][task.task_number - 1][index])
                    for prev_time in range(task.release_time, time):
                        c.append(literals[prev_time][task.task_number - 1][index - 1])
                    solver.add_clause(c)
                    #print(c)
              
    
    # Constraints to ensure that tasks are executed completely
    for task in tasks:
        for time in range(task.release_time, task.deadline_time):
            c = []
            c.append(-literals[time][task.task_number - 1][0])
            for next_time in range(time, task.deadline_time):
                c.append(literals[next_time][task.task_number - 1][-1])
            #print(c)
            solver.add_clause(c)

    

    # Constraints to ensure that tasks can only be executed after their release time or after the deadline
    for task in tasks:
        for time in range(task.release_time):
            for fragment in range(task.number_fragments):
                solver.add_clause([-literals[time][task.task_number - 1][fragment]])

        for time in range(task.deadline_time, max_deadline):
            for fragment in range(task.number_fragments):
                solver.add_clause([-literals[time][task.task_number - 1][fragment]])

    
    # Constraints to ensure that a task is only executed after its dependencies
    for i in range(max_deadline):
        for task in tasks:
            for dep in task.dependencies:
                clause = []
                for j in range(i):
                    clause.append(literals[j][dep - 1][-1])
                clause.append(-literals[i][task.task_number - 1][0])
                #print(clause)
                solver.add_clause(clause)


    # Constraints to ensure that only one fragment is executed at a time
    #top_id = total_number_fragments * max_deadline + len(tasks)
    for i in range(max_deadline):
        time_literals = []    
        for task in tasks:
            if i >= task.release_time and i < task.deadline_time:
                time_literals.extend(literals[i][task.task_number - 1])

        #enc = CardEnc.atmost(lits=time_literals, bound=1, top_id=top_id, encoding=EncType.pairwise)
        enc = CardEnc.atmost(lits=time_literals, bound=1, encoding=EncType.pairwise)
        for clause in enc.clauses:
            #max_id = max_id_in_clause(clause)
            #if max_id > top_id:
            #    top_id = max_id
            solver.add_clause(clause)





    # Soft clauses
    val = total_number_fragments * max_deadline + 1
    task_finished = []
    for task in tasks:
        task_finished.append(val)
        val += 1
    #print(task_finished)
    
    for task in tasks:
        clause = []
        clause.append(-task_finished[task.task_number - 1])

        for time in range(task.release_time, task.deadline_time):
            clause.append(literals[time][task.task_number - 1][task.number_fragments - 1])
        #print(clause)
        solver.add_clause(clause)
    
    
    #soft clause antiga
    for task_f in task_finished:
        solver.add_clause([task_f], weight=1)
    
    start = tm.time()
    # Print the output
    solution = solver.compute()
    end = tm.time()
    #print("Model:", solution, "\n")
       
    output = []
    for i in range(len(tasks)):
        output.append([])

    task_offset = 0
    for task in tasks:
        for fragment in range(task.number_fragments):
            for time in range(max_deadline):
                if solution[time * total_number_fragments + task_offset] > 0:
                    output[task.task_number - 1].append(str(time))
                    break
            task_offset += 1

    print(len(output) - output.count([]))
    for index, task_times in enumerate(output):
        if not task_times:
            continue
        print(index + 1, " ".join(task_times))
    
    print("Execution time", end - start)
    #print("Cost:", solver.cost)
            