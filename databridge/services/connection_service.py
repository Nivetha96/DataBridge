from databridge.connectors.local_connector import LocalConnector
from databridge.connectors.sftp_connector import SFTPConnector

class ConnectionService:

    def __init__(self, store):
        self.store = store

    def create_connection(
        self,
        name: str,
        type: str,
        params: dict
    ):
        self.store.save_connection(
            name=name,
            connection_type=type,
            config=params
        )

    def load_connector(self, connection_name: str):
        connection = self.store.get_connection(
            connection_name
        )

        if not connection:
            raise ValueError(
                f"Connection '{connection_name}' not found"
            )

        if connection["type"] == "local":
            return LocalConnector(
                connection["config"]["path"]
            )
        elif connection["type"] == "sftp":
            return SFTPConnector(
                connection["config"]["host"],
                connection["config"]["port"],
                connection["config"]["user"],
                connection["config"]["password"],
            )

        raise ValueError("Unsupported connection type")
