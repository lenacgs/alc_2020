include "proj3.dzn";
% --------------- model parameters ---------------

int: number_tasks;
int: max_number_fragments;
int: max_number_dependencies;
int: max_deadline;

array[1..number_tasks, 1..5] of int: tasks; % tasks[i] contains the release, processing and deadline times and the number of fragments and dependencies for task i
array[1..number_tasks, 1..max_number_fragments] of int: fragments; % fragments[i, j] is the processing time for fragment j of task i
array[1..number_tasks, 1..max_number_dependencies] of 0..number_tasks: dependencies; % dependencies[i] are the dependencies of task i

% --------------- model variables ----------------

% scheduled_fragments[i,j] is the starting time of fragment j of task i, if it was able to be scheduled
array[1..number_tasks, 1..max_number_fragments] of var 0..max_deadline: scheduled_fragments; %= array2d(1..number_tasks, 1..max_number_fragments, [0 | i in 1..number_tasks, j in 1..max_number_fragments]);
array[1..number_tasks] of var bool: task_finished; % = array1d(1..number_tasks, [false | i in 1..number_tasks]); % if task_finished[i] is true, then task #1 was able to finish


% ------------------- functions -------------------

function int: number_fragments(int: task_id) = tasks[task_id, 4];

function int: number_dependencies(int: task_id) = tasks[task_id, 5];

function int: deadline(int: task_id) = tasks[task_id, 3];

function int: release_time(int: task_id) = tasks[task_id, 1];

function int: duration(int: task_id) = tasks[task_id, 2];

% ------------------ constraints ------------------

% each task's starting time can only happen after its release time
constraint
  forall (task in 1..number_tasks) (
    scheduled_fragments[task, 1] >= release_time(task)
  );

% each task can only execute before its deadline
constraint
  forall (task in 1..number_tasks) (
    scheduled_fragments[task, number_fragments(task)] + fragments[task, number_fragments(task)] <= deadline(task)
  );
  
% ensure that fragments do not overlap
constraint
  forall (task1 in 1..number_tasks, fragment1 in 1..number_fragments(task1)) (
    forall (task2 in 1..number_tasks, fragment2 in 1..number_fragments(task2)) (
      (task1 == task2 /\ fragment1 == fragment2) \/
      scheduled_fragments[task1, fragment1] + fragments[task1, fragment1] <= scheduled_fragments[task2, fragment2] \/
      scheduled_fragments[task2, fragment2] + fragments[task2, fragment2] <= scheduled_fragments[task1, fragment1]
    )
  );
  
% if the last fragment executed, then the task has finished
constraint
  forall(task in 1..number_tasks) (
    scheduled_fragments[task, number_fragments(task)] != 0 -> task_finished[task] == true
  );

solve maximize sum(task_finished);



output [show(sum(task_finished)), "\n"] ++
       [show(if task_finished[task] then show(scheduled_fragments[task, frag])
             else "" endif) | task in 1..number_tasks, frag in 1..number_fragments(task)]