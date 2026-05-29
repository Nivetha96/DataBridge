from databridge.connectors.connector_factory import ConnectorFactory

class ConnectionService:

    def __init__(self, store):
        self.store = store

    def create_connection(
        self,
        name: str,
        type: str,
        params: dict
    ):        
        self.store.save_connection(name=name, connection_type=type, config=params)
        
    def _get_connection(self, connection_name: str):
        connection = self.store.get_connection(connection_name)
        if not connection:
            raise ValueError(
                f"Connection '{connection_name}' not found"
            )
        return connection
        
    def load_connector(self, connection_name: str):
        connection = self._get_connection(connection_name)
        return ConnectorFactory.create_connection(connection)
        
    def check_health(self, connection_name: str):
        connection = self._get_connection(connection_name)
        return ConnectorFactory.check_health(connection)
