import click
from pathlib import Path
import pandas as pd
from databridge.storage.connection_store import ConnectionStore
from databridge.services.connection_service import ConnectionService
from databridge.services.transfer_service import TransferService
from databridge.model.connection_type import ConnectionType
from databridge.model.file_type import FileType
from databridge.util.schema_inference import infer_json_schema, infer_csv_schema

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
    
    connection_service.create_connection(name, type, params)

    click.echo(
        f"Connection '{name}' created"
    )

@cli.command()
@click.option("--connection", required=True)
def check_health(connection):
    result = connection_service.check_health(connection)
    click.echo(result["message"])

@cli.command()
@click.option("--connection", required=True)
def list(connection):

    connector = connection_service.load_connector(connection)

    files = connector.list_files()

    if not files:
        click.echo("Folder is empty")
        return
        
    for file in files:
        click.echo(file)


@cli.command()
@click.option("--connection", required=True)
@click.option("--file", "file_name", required=True)
def head(connection, file_name):

    connector = connection_service.load_connector(connection)

    data = connector.read_file(file_name)

    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    valid_extensions = [t.value for t in FileType]
    if ext in valid_extensions:
        _print_schema(data, ext)

def _print_schema(data: bytes, ext: str) -> None:
    try:
        fields = infer_csv_schema(data) if ext == FileType.CSV.value else infer_json_schema(data)
    except (ValueError, Exception) as e:
        raise click.ClickException(f"Schema inference failed: {e}")

    if not fields:
        click.echo("(no fields found)")
        return

    # align columns for readability
    col_w = max(len(f["column"]) for f in fields)
    type_w = max(len(f["type"]) for f in fields)

    click.echo(f"  {'COLUMN':<{col_w}}  {'TYPE':<{type_w}}  NULLABLE")
    click.echo(f"  {'-'*col_w}  {'-'*type_w}  --------")
    for f in fields:
        nullable = "YES" if f["nullable"] else "no"
        click.echo(f"  {f['column']:<{col_w}}  {f['type']:<{type_w}}  {nullable}")
        

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
