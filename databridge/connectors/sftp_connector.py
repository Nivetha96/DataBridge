import posixpath
import paramiko
from databridge.connectors.base_connector import BaseConnector


class SFTPConnector(BaseConnector):

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.username = user
        self.password = password
        self.base_path = "data"
        self.sftp = None
        self.transport = None

        self._connect()

    def _connect(self):
        transport = paramiko.Transport((self.host, self.port))
        try:
            transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception:
            transport.close()
            raise

        self.transport = transport
        self.healthcheck()

    def healthcheck(self):
        try:
            self.sftp.listdir(self.base_path)
            return {
                "status": "healthy",
                "message": "SFTP connection successful"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": str(e)
            }

    def close(self):
        if self.sftp:
            self.sftp.close()
            self.sftp = None
        if self.transport:
            self.transport.close()
            self.transport = None

    def list_files(self):
        return self.sftp.listdir(self.base_path)

    def get_full_path(self, file_path: str) -> str:
        return posixpath.join(self.base_path, file_path)
        
    def read_file(self, file_path: str) -> bytes:
        full_path = self.get_full_path(file_path)
        try:
            self.sftp.stat(full_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"File does not exist: {full_path}")
        
        with self.sftp.open(full_path, "rb") as f:
            return f.read()

    def write_file(self, file_path: str, data: bytes) -> None:
        full_path = self.get_full_path(file_path)
        with self.sftp.open(full_path, "wb") as f:
            f.write(data)
