from datetime import datetime


class TransferService:

    def __init__(self, connection_service):
        self.connection_service = connection_service

    def transfer(
        self,
        source_connection,
        source_file,
        destination_connection,
        destination_file
    ):

        source_connector = (
            self.connection_service.load_connector(
                source_connection
            )
        )

        destination_connector = (
            self.connection_service.load_connector(
                destination_connection
            )
        )

        started_at = datetime.now()

        data = source_connector.read_file(
            source_file
        )

        destination_connector.write_file(
            destination_file,
            data
        )

        completed_at = datetime.now()

        bytes_transferred = len(data)

        return {
            "started_at": started_at,
            "completed_at": completed_at,
            "bytes_transferred": bytes_transferred
        }
