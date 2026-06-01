from enum import Enum


class FileType(Enum):
    CSV = "csv"
    JSON = "json"


def file_type_from_filename(file_name: str) -> FileType | None:
    ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
    try:
        return FileType(ext)
    except ValueError:
        return None
