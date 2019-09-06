from datetime import timedelta
from datetime import datetime
import click
from .commands import show_cmd, create_cmd

@click.group()
def ak():
    pass

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
def delete():
    pass

@click.command()
@click.argument("query_body")
@click.argument("lambda_body")
def update(query_body, lambda_body):
    update_cmd(query_body, lambda_body)

ak.add_command(show)
ak.add_command(create)
ak.add_command(delete)
ak.add_command(update)

if __name__=='__main__':
    ak()
