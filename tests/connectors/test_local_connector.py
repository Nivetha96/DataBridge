import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from databridge.connectors.local_connector import LocalConnector


class TestLocalConnector:

    def test_valid_directory(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        assert connector.base_path == tmp_path

    def test_nonexistent_directory_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Directory does not exist"):
            LocalConnector(str(tmp_path / "ghost"))

    def test_file_path_raises(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_bytes(b"data")
        with pytest.raises(ValueError, match="Path is not a directory"):
            LocalConnector(str(f))

    def test_healthy(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        result = connector.healthcheck()
        assert result["status"] == "healthy"

    def test_unhealthy_when_path_removed(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        tmp_path.rmdir()
        result = connector.healthcheck()
        assert result["status"] == "unhealthy"

    def test_reads_existing_file(self, tmp_path):
        (tmp_path / "sample.txt").write_bytes(b"hello")
        connector = LocalConnector(str(tmp_path))
        assert connector.read_file("sample.txt") == b"hello"

    def test_missing_file_raises(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        with pytest.raises(FileNotFoundError, match="File does not exist"):
            connector.read_file("missing.txt")

    def test_writes_file(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        connector.write_file("out.txt", b"world")
        assert (tmp_path / "out.txt").read_bytes() == b"world"

    def test_overwrites_existing_file(self, tmp_path):
        (tmp_path / "out.txt").write_bytes(b"old")
        connector = LocalConnector(str(tmp_path))
        connector.write_file("out.txt", b"new")
        assert (tmp_path / "out.txt").read_bytes() == b"new"

    def test_lists_files_only(self, tmp_path):
        (tmp_path / "a.txt").write_bytes(b"")
        (tmp_path / "b.txt").write_bytes(b"")
        (tmp_path / "subdir").mkdir()
        connector = LocalConnector(str(tmp_path))
        assert sorted(connector.list_files()) == ["a.txt", "b.txt"]

    def test_empty_directory(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        assert connector.list_files() == []

    def test_joins_base_and_relative(self, tmp_path):
        connector = LocalConnector(str(tmp_path))
        assert connector.get_full_path("file.csv") == tmp_path / "file.csv"
