import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from databridge.connectors.connector_factory import ConnectorFactory
from databridge.connectors.local_connector import LocalConnector
from databridge.connectors.sftp_connector import SFTPConnector


class TestConnectorFactory:
 
    def test_creates_local_connector(self, tmp_path):
        connection = {"type": "local", "config": {"path": str(tmp_path)}}
        connector = ConnectorFactory.create_connection(connection)
        assert isinstance(connector, LocalConnector)
 
    def test_creates_sftp_connector(self):
        connection = {
            "type": "sftp",
            "config": {"host": "h", "port": 22, "user": "u", "password": "p"}
        }
        with patch.object(SFTPConnector, "_connect"):
            connector = ConnectorFactory.create_connection(connection)
            assert isinstance(connector, SFTPConnector)
 
    def test_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported connection type"):
            ConnectorFactory.create_connection({"type": "ftp", "config": {}})
 
    def test_check_health_returns_dict(self, tmp_path):
        connection = {"type": "local", "config": {"path": str(tmp_path)}}
        result = ConnectorFactory.check_health(connection)
        assert "status" in result
        assert "message" in result
