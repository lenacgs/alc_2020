Project #1 - Single Machine Scheduling

André Lopes
Madalena Santos 97085

Our program uses the RC2 MaxSAT solver (PySAT on python3), which is an implementation of the RC2 algorithm for solving maximum satisfiability. RC2 stands for relaxable cardinality constraints. This solver allows the implementation of soft clauses.
To execute it, use:

$./proj1 < inputfile > outputfile

Python3 should be located under the directory /usr/bin

Our program starts by reading the tasks from the input file, and loads them into an array of objects of class Task.
The literals for the solver are saved in an array of arrays of arrays (3D matrix). Each literal considers a moment in time, a task and a fragment of that task. Literals can be accessed through "literals[time_slot][task_id][fragment_id]".

The constraints added to the solver are:

- To ensure that each task is only executed after its release time: to do this, we negate the literals that represent a certain fragment from a certain task being executed at a point in time before to its release time

- To ensure that each task is only executed before its deadline: to do this, we negate the literals that represent a certain fragment from a certain task being executed at a point in time after its deadline time

- To ensure that only one fragment executes in each time slot: we make use of a cardinality encoding to guarantee that at most one fragment executes at a certain point in time

- To ensure that fragments that occupy more than 1 time slot are executed in adjacent time slots: we consider that there is an implication between the first fragment of a task at the current time slot and the other fragments in the following adjacent time slots

- To ensure that fragments are executed in order (fragment 1 executes before fragment 2 and so on): we consider that if a certain fragment of a certain task is being executed at a certain point in time, then the previous fragments of the same task must have executed before. There is an implication between each fragment at the current time and all the other previous fragments in previous points in time

- To ensure that tasks are executed completely (either all fragments are executed or none are): to do this, we create an implication between the first fragment of a task at a point in time and the last fragment of the same task in the following time slots

- To ensure that tasks are only executed after its dependencies: we create an implication between the first fragment of a task at a certain point in time and the last fragment of each of this tasks' dependencies in the previous time slots

Soft clause: the goal of the solution is to execute as many tasks as possible. We create an array that represents the execution of each task. If task[0] was able to execute, then task_finished[0] will be true. Then, we use the task_finished array to build our soft clause, where we state that each position on this array should be true.