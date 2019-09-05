# Textbased kanban issue tracker

Each issue has a key-value data structure with arbitrary information.
The mandatory keys are id (auto-generated increasing id), title and status.
Status is automatically initiated to 'backlog'.
The 'status' key has predefined usage as columns of a kanban board.
A kanban layout is given by an ordered list of column names, but by default the list
is ['backlog', 'selected', 'wip', 'blocked', 'done'].

TODO: add max rows for kanban board and crud operations for the kanban boards.
TODO: handle separate location of python code and issues/

Each command is a selection followed by a command.

Commands are accomanied with python expressions QUERY and LAMBDA which are bodies of lambdas
whose variable is x. QUERY is used for issue selection by filtering and LAMBDA is used for setting key-value data on issues.

Install:

```
# get python 3
pip install -r requirements.txt
```


Usage:

```
python -m commands.ak show QUERY
python -m commands.ak delete QUERY
python -m commands.ak update QUERY LAMBDA
python -m commands.ak create TITLE [LAMBDA]
```

Examples:

```
python -m commands.ak show 'date>\today'
python -m commands.ak delete 'status=done'
python -m commands.ak update 'x.due_date+=timedelta(day=1)' 'x.importance>=3'
python -m commands.ak create 'my_title' 'x.date=\today'
```


Current sample output:
```
> cat issues/1                                                                                                                                                                                                                                                                                                      Thu Sep  5 22:37:24 2019
{"title": "test", "id": "J-1", "status": "done"}
> python -m commands.ak show True                                                                                                                                                                                                                                                                                   Thu Sep  5 22:37:30 2019
---------------------------------------------------------------------------------
|    backlog    |   upcoming    |      wip      |    blocked    |     done      |
---------------------------------------------------------------------------------
|               |               |               |               |      J-1      |
|               |               |               |               |     test      |
|               |               |               |               |               |
---------------------------------------------------------------------------------
```
