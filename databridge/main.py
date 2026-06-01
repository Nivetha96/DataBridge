import click
from typing import List, Dict
import json
import csv, io
from databridge.storage.connection_store import ConnectionStore
from databridge.services.connection_service import ConnectionService
from databridge.services.transfer_service import TransferService
from databridge.model.connection_type import ConnectionType
from databridge.model.file_type import FileType, file_type_from_filename
from databridge.util.schema_inference import infer_schema

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
    try:
        connection_type = ConnectionType(type)
    except ValueError:
        raise click.ClickException(f"Unsupported connection type: {type}")
    if type == ConnectionType.LOCAL.value:
        params = {"path": path}
    elif type == ConnectionType.SFTP.value:
        params = {"host": host, "port": port, "user": user, "password": password}

    connection_service.create_connection(name, type, params)

    click.echo(f"Connection '{name}' created")


@cli.command()
@click.option("--connection", required=True)
def check_health(connection):
    try:
        result = connection_service.check_health(connection)
        click.echo(result["message"])
    except Exception as e:
        raise click.ClickException(str(e))


@cli.command(name="list")
@click.option("--connection", required=True)
def list_files(connection):
    try:
        connector = connection_service.load_connector(connection)
    except Exception as e:
        raise click.ClickException(str(e))
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
    try:
        connector = connection_service.load_connector(connection)
    except Exception as e:
        raise click.ClickException(str(e))
    data = connector.read_file(file_name)

    file_type = file_type_from_filename(file_name)
    if file_type is None:
        raise click.ClickException(
            f"Unsupported file type. Supported: {[t.value for t in FileType]}"
        )
    click.echo("Displaying schema ->")
    _print_schema(data, file_type)
    click.echo("Displaying data ->")
    _print_rows(data, file_type)


def _print_rows(data: bytes, file_type: FileType, n: int = 5) -> None:
    match file_type:
        case FileType.CSV:
            rows = _read_csv_rows(data, n)
        case FileType.JSON:
            rows = _read_json_rows(data, n)
        case _:
            raise click.ClickException(f"Unsupported file type: {file_type}")

    if not rows:
        click.echo("(no rows found)")
        return

    headers = list(rows[0].keys())
    col_widths = {h: max(len(h), max(len(str(r[h])) for r in rows)) for h in headers}

    header_line = "  ".join(f"{h:<{col_widths[h]}}" for h in headers)
    separator = "  ".join("-" * col_widths[h] for h in headers)
    click.echo(header_line)
    click.echo(separator)
    for row in rows:
        click.echo("  ".join(f"{str(row[h]):<{col_widths[h]}}" for h in headers))


def _read_csv_rows(data: bytes, n: int) -> List[Dict]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8", errors="replace")))
    return [row for _, row in zip(range(n), reader)]


def _read_json_rows(data: bytes, n: int) -> List[Dict]:
    rows = json.loads(data.decode("utf-8", errors="replace"))
    if not isinstance(rows, list):
        raise click.ClickException("JSON file must contain an array of objects")
    return rows[:n]


def _print_schema(data: bytes, file_type: FileType) -> None:
    try:
        fields = infer_schema(data, file_type)
    except Exception as e:
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
def transfer(source, source_file, destination, destination_file):

    result = transfer_service.transfer(
        source, source_file, destination, destination_file
    )
    click.echo(f"Transfer completed successfully")
    click.echo(f"Bytes transferred: " f"{result['bytes_transferred']}")
    click.echo(f"Started: {result['started_at']}")
    click.echo(f"Completed: {result['completed_at']}")


if __name__ == "__main__":
    cli()
