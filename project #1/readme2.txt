Project #2 - Single Machine Scheduling

André Lopes 98675
Madalena Santos 97085

Our program uses the Z3 theorem prover, which is a cross-platform satisfiability modulo theories solver. Z3 supports arithmetic, fixed-size bit-vectors, extensional arrays, datatypes, uninterpreted functions and quantifiers. 

To install Z3, run the command:
$pip3 install z3-solver

To execute the project use:
$./proj2 < inputfile > outputfile

Python3 should be located under the directory /usr/bin

Our program starts by reading the tasks from the input file, and loads them into a list of objects of class Task.

The literals for the solver are saved in a list of lists, where each literal considers a task and a fragment of that task. The value in each slot of the list of lists represents the time slot where that fragment will be executed. Each literal has a name that associates it with the corresponding task number and fragment number, and it can be accessed through "variables[task_number][fragment_number]". Another list of literals is used, tasks_finished, which helps us verify if a task was able to finish (by executing all of its fragments).

The constraints added to the solver are:

- To ensure that each task is only executed after its release time and before its deadline time

- To ensure that fragments are executed in order, which means that the 3rd fragment of a certain task can only be executed after the 2nd fragment has been executed.

- To ensure that only one fragment is executed at each time slot

- To ensure that a task only executes after its dependecies, which means that the literal corresponding to the first fragment of a certain task must have a value that is higher than the one corresponding to the last fragment of each of its dependencies (the execution time of the last fragments has to be considered). The constraint that directly implies the dependency between the tasks is also added, using the tasks_finished list.

Since the goal of this project is to maximize the number of tasks that can be scheduled, the solver uses the Optimize context. We then express this maximization using the statement "solver.maximize(Sum(tasks_finished))"