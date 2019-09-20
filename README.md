# Textbased kanban issue tracker

Each issue has a key-value data structure with predefined and custom data.
The mandatory keys are id (auto-generated increasing id), title and status.
Status is automatically initiated to 'backlog'.
The 'status' key has predefined usage as columns of a kanban board.
A kanban layout is given by an ordered list of column names, but by default the list
is ['backlog', 'selected', 'wip', 'blocked', 'done'].

Certain subcommands (show, show-issues, edit, delete and tag) can be applied in batch to
issues that match a specified filter. The filter is specified using command line arguments
and giving values and expressions according to a simple syntax.

## Filters
- Id: -i, --ids ids (comma separated, any will match)
- Status: -s, --status comma separated (prefixes of) statuses, any will match. The filter can be negated by adding ~: before.
- Creation date: -c, --created \[><=\]\(\[0-9\]\[YMdwhms\]\)+ or \[><=\]YEAR-MONTH-DAY
- Tags: -T, --tags comma separated tag. The filter can be negated by adding ~: before.
- Parent: -p, -parent id
- Ancstor: -a, -ancestor id
- Title:  -t, --title string (uses fuzzy matching)
- Description: -d, --description string (uses fuzzy matching)
- Title or Description: -m, --match string (uses fuzzy matching)

## Journaling/logging
- Use ```fab log -i ID```.
- The due-date is set with same syntax as for creation date, but relative dates refer to future dates.

## Habits
- Create a habit with ```fab create-habit```.
- Report habit success with ```fab log -i ID```. To just edit log use ```fab log -i ID --no-report```.
- Successes, failures and days remaining are displayed in kanban board

## Settings
- Use ```fab settings``` to edit settings. If settings file is abscent a template is created.
- Comment lines with #.
- Settings are in $ASCIIBAN_DOTFILE or by default in $HOME/.asciiban

## Data
- Data resides in $ASCIIBAN_DATADIR or by default in $HOME/.asciiban.d
- To persist issues use any method of your choice. If the data directory is a git repo, pushing and pulling can be done with ```fab push``` and ```fab pull```.

## Install

```
# get python 3
pip install -r requirements.txt
clone this repo
chmod +x fab.py
alias fab="/path/to/fab.py"
```

## Help

```
fab --help
fab SUBCOMMAND --help
```

## Examples

```
fab create                                   # create a new issue, opens editor
fab rename -i 1 "My new title"               # sets a new title
fab show -c "<2d"                            # show board with issues created earlier than 2 days ago
fab edit -c ">2h30m" -c "<1h"                # edit issues created between 1h and 2h30m ago
fab delete -p 4                              # delete issues whose parent has id 4
fab subtask 2 4                              # make issue 4 a subtask of issue 2
fab tag -a 5 "food,china"                    # add tags food and china to all tasks descending from issue 5
fab ls-tags -s wip                           # list all tags and counts for issues that are wip
fab show-issues -t "food,japan"              # display detailed information about all tasks tagged with food or japan (or both)
fab show-issues --no-details                 # show paths for all issues
fab show-issues --no-path                    # show one json per line for all issues
fab show-issues --pretty                     # expand issues and add separating vertical lines
fab log -i 1                                 # update log for issue 1
fab create-habit                             # start a new healthy habit
fab log -i 10                                # report success on issue 10 if it's a habit and update log
fab transition -s wip done                   # transition all issues from wip to done
fab git-status                               # show git status for data directory
fab pull                                     # git pull changes from remote
fab push                                     # git push changes to remote
```

