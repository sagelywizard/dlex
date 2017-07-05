# dlex

A framework for running deep learning experiments

## commands

`dlex add [definitionname] [experiment path]`

adds a new experiment definition

`dlex list`

lists all experiment definitions

`dlex remove [definition name]`

removes an experiment definition

`dlex run [definition name] [hyperparams]`

executes a deep learning experiment

`dlex status`

shows the status of all running/paused experiments

`dlex edit [experiment id] [hyperparams]`

edits a running experiment

`dlex pause [experiment id | all]`

pauses the execution of an experiment, but leaves all state in memory

`dlex resume [experiment id | all]`

resumes a paused experiment

`dlex copy [experiment id]`

copies the entire state of an experiment to a new experiment
