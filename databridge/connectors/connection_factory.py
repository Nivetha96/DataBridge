from databridge.connector.local_connect import LocalConnector
from databridge.connector.sftp_connector import SFTPConnector

class ConnectorFactory:

    @staticmethod
    def create(connection, params):
        if connection.type == "local":
            return LocalConnector(params)
        elif connection.type == "sftp":
            return SFTPConnector(params)
