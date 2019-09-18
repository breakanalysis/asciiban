#!/usr/bin/env python3
from datetime import timedelta
from datetime import datetime
from commands import (
        show_cmd, create_cmd, edit_cmd, delete_cmd,
        show_issues_cmd, tag_cmd, subtask_cmd
        )
import click
from argparse import ArgumentParser

def add_filtering(parsers):
    for parser in parsers:
        parser.add_argument('-i', '--id', type=int, help="Match issue with given id.")
        parser.add_argument('-s', '--status', help="Match issues whose status matches any of given comma separated statuses. May be repeated.")
        parser.add_argument('-T', '--tags', action='append', help="Match issues that have at least one tag among the comma separated tags in TAGS. May be repeated.")
        # parser.add_argument('-D', '--due-date', action='append', help="")
        parser.add_argument('-c', '--created', action='append', help="Match by creation date pattern CREATED which starts with [<>=] followed by ([0-9]+[YMwdhms])+ or YEAR-MONTH-DAY. For equality filtering, current time and creation time are rounded downward to the same precision as used in CREATED (i.e. day, hour or minute precision). May be repeated.")
        parser.add_argument('-a', '--ancestor', type=int, help="Match issues that are decendants of issue with id ANCESTOR.")
        parser.add_argument('-t', '--title', action='append', help="Fuzzily match issues by comparing their title with TITLE. May be repeated.")
        parser.add_argument('-d', '--description', action='append', help="Fuzzily match issues by comparing their description with DESCRIPTION. May be repeated.")
        parser.add_argument('-m', '--match', action='append', help="Fuzzily match issues by comparing their title and description with MATCH. May be repeated.")
        parser.add_argument('-p', '--parent', type=int, help="Match issues that are children of issue with id PARENT.")
        # parser.add_argument('-P', '--priority', action='append', help="")

def add_tag_parser(sub_parsers):
    tag_parser = sub_parsers.add_parser("tag")
    tag_parser.add_argument("mod", help="Comma delimited tags to add (or delete if tag is prepended by ~). E.g. fab tag -i 10 ~food,cuisine")
    return tag_parser

def add_subtask_parser(sub_parsers):
    subtask_parser = sub_parsers.add_parser("subtask", help="Make issue with id SUBTASK_ID a subtask of issue with id PARENT_ID.")
    subtask_parser.add_argument("parent_id")
    subtask_parser.add_argument("subtask_id")

if __name__=='__main__':
    parser = ArgumentParser()
    sub_parsers = parser.add_subparsers(help='Available commands', dest='command')
    show_issues_parser = sub_parsers.add_parser("show-issues", help="Detailed view of issues matching given filters.")
    show_parser = sub_parsers.add_parser("show", help="Display a kanban board.")
    create_parser = sub_parsers.add_parser("create", help="Create an issue by editing a json template.")
    delete_parser = sub_parsers.add_parser("delete", help="Delete all issues matching given filters.")
    edit_parser = sub_parsers.add_parser("edit", help="Edit all issues matching given filters.")
    tag_parser = add_tag_parser(sub_parsers)
    add_subtask_parser(sub_parsers)
    add_filtering([show_parser, show_issues_parser, delete_parser, edit_parser, tag_parser])
    args = parser.parse_args()
    command = args.command
    if command == 'show-issues':
        show_issues_cmd(args)
    elif command == 'show':
        show_cmd(args)
    elif command == 'create':
        create_cmd()
    elif command == 'delete':
        delete_cmd(args)
    elif command == 'edit':
        edit_cmd(args)
    elif command == 'tag':
        tag_cmd(args)
    elif command == 'subtask':
        subtask_cmd(args.parent_id, args.subtask_id)
    else:
        pass
