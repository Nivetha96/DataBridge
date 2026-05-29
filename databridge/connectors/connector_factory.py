from databridge.connectors.local_connector import LocalConnector
from databridge.connectors.sftp_connector import SFTPConnector


class ConnectorFactory:

    @staticmethod
    def create_connection(connection):

        connection_type = connection["type"]
        config = connection["config"]

        connectors = {
            "local": lambda: LocalConnector(
                config["path"]
            ),

            "sftp": lambda: SFTPConnector(
                config["host"],
                config["port"],
                config["user"],
                config["password"]
            )
        }

        connector_builder = connectors.get(
            connection_type
        )

        if not connector_builder:
            raise ValueError(
                f"Unsupported connection type: "
                f"{connection_type}"
            )

        return connector_builder()
