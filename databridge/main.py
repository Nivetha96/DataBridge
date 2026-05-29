import click

from databridge.storage.connection_store import ConnectionStore
from databridge.services.connection_service import ConnectionService
from databridge.services.transfer_service import TransferService
from databridge.model.connection_type import ConnectionType

store = ConnectionStore()
connection_service = ConnectionService(store)
transfer_service = TransferService(connection_service)

@click.group()
def cli():
    pass


@cli.command()
@click.option("--name", required=True)
@click.option("--type", required=True)
@click.option("--path", default=".")
@click.option("--host", default="localhost")
@click.option("--port", default=8888)
@click.option("--user", default="testuser")
@click.option("--password", default="testpwd")
def create_connection(name, type, path, host, port, user, password):

    params = {}
    if type == ConnectionType.LOCAL.value:
        params = {"path" : path}
    elif type == ConnectionType.SFTP.value:
        params = {"host": host, "port": port, "user": user, "password": password}
    
    service.create_connection(name, type, params)

    click.echo(
        f"Connection '{name}' created"
    )


@cli.command()
@click.option("--connection", required=True)
def list(connection):

    connector = connection_service.load_connector(connection)

    files = connector.list_files()

    for file in files:
        click.echo(file)


@cli.command()
@click.option("--connection", required=True)
@click.option("--file", "file_name", required=True)
def head(connection, file_name):

    connector = connection_service.load_connector(connection)

    data = connector.read_file(file_name)

    text = data.decode("utf-8")

    lines = text.splitlines()[:5]

    for line in lines:
        click.echo(line)
        

@cli.command()
@click.option("--source", required=True)
@click.option("--source-file", required=True)
@click.option("--destination", required=True)
@click.option("--destination-file", required=True)
def transfer(
    source,
    source_file,
    destination,
    destination_file
):

    result = transfer_service.transfer(
        source,
        source_file,
        destination,
        destination_file
    )

    click.echo(
        f"Transfer completed successfully"
    )

    click.echo(
        f"Bytes transferred: "
        f"{result['bytes_transferred']}"
    )

    click.echo(
        f"Started: {result['started_at']}"
    )

    click.echo(
        f"Completed: {result['completed_at']}"
    )
    
    
if __name__ == "__main__":
    cli()
