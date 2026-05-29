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
            config=params
        
        self.store.save_connection(name=name, connection_type=type, config=params)
        
    def load_connector(self, connection_name: str):
        connection = self.store.get_connection(
            connection_name
        )

        if not connection:
            raise ValueError(
                f"Connection '{connection_name}' not found"
            )
            
        return ConnectorFactory.create_connection(connection)
