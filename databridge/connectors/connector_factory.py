from databridge.connectors.local_connector import LocalConnector
from databridge.connectors.sftp_connector import SFTPConnector


class ConnectorFactory:

    _builders = {
        "local": lambda config: LocalConnector(config["path"]),
        "sftp": lambda config: SFTPConnector(
            config["host"], config["port"], config["user"], config["password"]
        ),
    }

    @staticmethod
    def create_connection(connection):
        connection_type = connection["type"]
        config = connection["config"]

        builder = ConnectorFactory._builders.get(connection_type)

        if builder is None:
            supported = list(ConnectorFactory._builders)
            raise ValueError(
                f"Unsupported connection type: '{connection_type}'. "
                f"Supported types: {supported}"
            )

        return builder(config)

    @staticmethod
    def check_health(connection):
        connector = ConnectorFactory.create_connection(connection)
        return connector.healthcheck()
