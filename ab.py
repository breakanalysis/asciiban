#!/usr/bin/env python3
from datetime import timedelta
from datetime import datetime
import click
from commands import show_cmd, create_cmd, update_cmd, delete_cmd, show_issues_cmd

@click.group()
def ab():
    pass

@click.command()
@click.argument("lambda_body")
def show_issues(lambda_body):
    show_issues_cmd(lambda_body)

@click.command()
@click.argument("lambda_body")
def show(lambda_body):
    show_cmd(lambda_body)

@click.command()
@click.argument("title")
@click.argument("lambda_body", required=False)
def create(title, lambda_body=None):
    create_cmd(title, lambda_body)

@click.command()
@click.argument("query_body")
def delete(query_body):
    delete_cmd(query_body)

@click.command()
@click.argument("query_body")
@click.argument("lambda_body")
def update(query_body, lambda_body):
    update_cmd(query_body, lambda_body)

ab.add_command(show)
ab.add_command(show_issues)
ab.add_command(create)
ab.add_command(delete)
ab.add_command(update)

if __name__=='__main__':
    ab()
