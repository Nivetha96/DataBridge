import paramiko
from databridge.connectors.base_connector import BaseConnector


class SFTPConnector(BaseConnector):

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.username = user
        self.password = password
        self.base_path = "data"

        self._connect()

    def _connect(self):
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)

        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def list_files(self):
        return self.sftp.listdir(base_path)

    def get_full_path(self, file_path: str) -> str:
        return self.base_path + "/" + file_path
        
    def read_file(self, file_path: str) -> bytes:
        full_path = self.get_full_path(file_path)
        with self.sftp.open(full_path, "rb") as f:
            return f.read()

    def write_file(self, file_path: str, data: bytes) -> None:
        full_path = self.get_full_path(file_path)
        with self.sftp.open(full_path, "wb") as f:
            f.write(data)
