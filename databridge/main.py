import click

from databridge.storage.connection_store import ConnectionStore
from databridge.services.connection_service import ConnectionService


store = ConnectionStore()
service = ConnectionService(store)


@click.group()
def cli():
    pass


@cli.command()
@click.option("--name", required=True)
@click.option("--path", required=True)
def create_connection(name, path):

    service.create_local_connection(name, path)

    click.echo(
        f"Connection '{name}' created"
    )


@cli.command()
@click.option("--connection", required=True)
def list(connection):

    connector = service.load_connector(connection)

    files = connector.list_files()

    for file in files:
        click.echo(file)


@cli.command()
@click.option("--connection", required=True)
@click.option("--file", "file_name", required=True)
def head(connection, file_name):

    connector = service.load_connector(connection)

    data = connector.read_file(file_name)

    text = data.decode("utf-8")

    lines = text.splitlines()[:5]

    for line in lines:
        click.echo(line)
        
        
if __name__ == "__main__":
    cli()
