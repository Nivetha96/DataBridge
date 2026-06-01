import io
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from databridge.connectors.sftp_connector import SFTPConnector


@pytest.fixture
def sftp_connector():
    """SFTPConnector with a fully mocked paramiko transport and SFTP client."""
    with patch(
        "databridge.connectors.sftp_connector.paramiko.Transport"
    ) as MockTransport:
        mock_transport = MagicMock()
        MockTransport.return_value = mock_transport

        mock_sftp = MagicMock()
        mock_sftp.listdir.return_value = ["file.csv"]

        with patch(
            "databridge.connectors.sftp_connector.paramiko.SFTPClient.from_transport",
            return_value=mock_sftp,
        ):
            from databridge.connectors.sftp_connector import SFTPConnector

            connector = SFTPConnector("host", 22, "user", "pass")
            connector.sftp = mock_sftp
            connector.transport = mock_transport
            yield connector, mock_sftp, mock_transport


class TestSFTPConnectorConnect:

    def test_successful_connect(self, sftp_connector):
        connector, mock_sftp, mock_transport = sftp_connector
        assert connector.sftp is mock_sftp
        assert connector.transport is mock_transport

    def test_auth_failure_closes_transport(self):
        with patch(
            "databridge.connectors.sftp_connector.paramiko.Transport"
        ) as MockTransport:
            import paramiko

            mock_transport = MagicMock()
            mock_transport.connect.side_effect = paramiko.AuthenticationException()
            MockTransport.return_value = mock_transport

            from databridge.connectors.sftp_connector import SFTPConnector

            with pytest.raises(paramiko.AuthenticationException):
                SFTPConnector("host", 22, "user", "wrongpass")

            mock_transport.close.assert_called_once()

    def test_healthy(self, sftp_connector):
        connector, mock_sftp, _ = sftp_connector
        result = connector.healthcheck()
        assert result["status"] == "healthy"

    def test_unhealthy_on_sftp_error(self, sftp_connector):
        connector, mock_sftp, _ = sftp_connector
        mock_sftp.listdir.side_effect = Exception("Connection lost")
        result = connector.healthcheck()
        assert result["status"] == "unhealthy"
        assert "Connection lost" in result["message"]

    def test_reads_existing_file(self, sftp_connector):
        connector, mock_sftp, _ = sftp_connector
        mock_sftp.stat.return_value = MagicMock()
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_file.read.return_value = b"csv content"
        mock_sftp.open.return_value = mock_file

        result = connector.read_file("data.csv")
        assert result == b"csv content"
        mock_sftp.open.assert_called_once_with("data/data.csv", "rb")

    def test_missing_file_raises(self, sftp_connector):
        connector, mock_sftp, _ = sftp_connector
        mock_sftp.stat.side_effect = FileNotFoundError()
        with pytest.raises(FileNotFoundError, match="File does not exist"):
            connector.read_file("missing.csv")

    def test_writes_file(self, sftp_connector):
        connector, mock_sftp, _ = sftp_connector
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: s
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_sftp.open.return_value = mock_file

        connector.write_file("out.csv", b"data")
        mock_sftp.open.assert_called_once_with("data/out.csv", "wb")
        mock_file.write.assert_called_once_with(b"data")

    def test_close_releases_resources(self, sftp_connector):
        connector, mock_sftp, mock_transport = sftp_connector
        connector.close()
        mock_sftp.close.assert_called_once()
        mock_transport.close.assert_called_once()
        assert connector.sftp is None
        assert connector.transport is None

    def test_close_is_idempotent(self, sftp_connector):
        connector, _, _ = sftp_connector
        connector.close()
        connector.close()

    def test_joins_base_and_relative(self, sftp_connector):
        connector, _, _ = sftp_connector
        assert connector.get_full_path("file.csv") == "data/file.csv"
