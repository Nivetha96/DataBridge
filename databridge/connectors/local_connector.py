from pathlib import Path
from databridge.connectors.base_connector import BaseConnector


class LocalConnector(BaseConnector):

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

        if not self.base_path.exists():
            raise ValueError(f"Directory does not exist: {base_path}")
        if not self.base_path.is_dir():
            raise ValueError(f"Path is not a directory: {base_path}")

    def healthcheck(self):
        if not self.base_path.exists() or not self.base_path.is_dir():
            return {
                "status": "unhealthy",
                "message": "Path/ Directory issue. Connection Failure",
            }
        return {"status": "healthy", "message": "Local connection successful"}

    def get_full_path(self, path: str) -> Path:
        return self.base_path / path

    def read_file(self, path: str) -> bytes:
        full_path = self.get_full_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File does not exist: {full_path}")
        with open(full_path, "rb") as f:
            return f.read()

    def list_files(self):
        return [f.name for f in self.base_path.iterdir() if f.is_file()]

    def write_file(self, path, data):
        with open(self.get_full_path(path), "wb") as f:
            f.write(data)
