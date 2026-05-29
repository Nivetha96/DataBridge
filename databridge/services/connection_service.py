from databridge.connectors.local_connector import LocalConnector


class ConnectionService:

    def __init__(self, store):
        self.store = store

    def create_local_connection(
        self,
        name: str,
        path: str
    ):
        self.store.save_connection(
            name=name,
            connection_type="local",
            config={"path": path}
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

        raise ValueError("Unsupported connection type")
