from pathlib import Path
from databridge.connectors.base_connector import BaseConnector

class LocalConnector(BaseConnector):

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
        if not self.base_path.exists():
            raise ValueError(
                f"Directory does not exist: {base_path}"
            )

    def list_files(self):
        return [f.name for f in self.base_path.iterdir() if f.is_file()]

    def read_file(self, path):
        with open(self.base_path / path, "rb") as f:
            return f.read()

    def write_file(self, path, data):
        with open(self.base_path / path, "wb") as f:
            f.write(data)
