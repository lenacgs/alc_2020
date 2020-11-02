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

    for literal in literals:
        print(literal)
    print("")
    
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

    top_id = total_number_fragments * max_deadline
    #Constraints to ensure that each fragment is executed at most once
    for task in tasks:
        for fragment in range(task.number_fragments):
            frag_literals = []
            for i in range(max_deadline):
                frag_literals.append(literals[i][task.task_number - 1][fragment])

            # enc = CardEnc.atmost(lits=frag_literals, bound=1, encoding=EncType.pairwise)
            #print(frag_literals, "Time:", task.fragments[fragment])
            enc = CardEnc.atmost(lits=frag_literals, bound=task.fragments[fragment], top_id=top_id, encoding=EncType.seqcounter)
            for clause in enc.clauses:
                max_id = max_id_in_clause(clause)
                if max_id > top_id:
                    top_id = max_id
                solver.add_clause(clause)

    #Constraints to deal with tasks' dependencies
    for i in range(max_deadline):
        for task in tasks:
            for dep in task.dependencies:
                clause = []
                for j in range(i):
                    clause.append(literals[j][dep - 1][-1])
                clause.append(-literals[i][task.task_number - 1][0])
                solver.add_clause(clause)


    for task in tasks:
        for time in range(task.release_time, task.deadline_time):
            for index, fragment_duration in enumerate(task.fragments):
                # Constraints to ensure that fragments are fragments with size > 1 are executed sequentialy
                # If the first fragment of task 1 (Tx00) has a duration = 2 then
                # for every time where this fragment can be executed we need to make sure that if it
                # is executed, in the next time step it will be executed as well. To achieve this we can
                # use the cause (T000 and T100) => T200 <=> If the fragment is executed at time 1 (T100) then
                # it must be executed at time 2 (T200) as well
                if time + (fragment_duration - 1) < max_deadline and fragment_duration > 1:
                    # print("Time", time, "Task", task.task_number, "Fragment", index, "Duration", fragment_duration)
                    clause = []
                    if time > 0:
                        clause.append(literals[time - 1][task.task_number - 1][index])
                    clause.append(-literals[time][task.task_number - 1][index])
                    for time_offset in range(1, fragment_duration):
                        clause.append(literals[time + time_offset][task.task_number - 1][index])
                        solver.add_clause(clause)
                        clause.pop()
                elif fragment_duration > 1:
                    # This prevents a fragment that excedes the max_deadline from being executed
                    # Eg: If max_deadline = 9 then a fragment that takes 2 time units to complete can not be executed at time 8
                    # print("Time", time, "Task", task.task_number, "Fragment", index, "Duration", fragment_duration)
                    solver.add_clause([-literals[time][task.task_number - 1][index]])
                

                # Constraints to ensure that fragments are executed in order
                # Eg: T301 => (T200 or T100 or T000) <=> (-T301 or T200 or T100 or T000)
                if index != 0: # First task does not need previous tasks to be executed before
                    # print("Time", time, "Task", task.task_number, "Fragment", index, "Duration", fragment_duration)
                    c = [-literals[time][task.task_number - 1][index]]
                    for previous_time in range(task.release_time, time):
                        c.append(literals[previous_time][task.task_number - 1][index - 1])
                    solver.add_clause(c)


    # Soft clauses
    # Should to be altered to last fragment of every task
    for i in range(max_deadline):
        for t in tasks:
            for item in range(t.number_fragments):
                solver.add_clause([literals[i][t.task_number - 1][item]], weight=1)
        
    # Print the output
    # Has to be altered to print only once fragments that take more than 1 time step
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
            