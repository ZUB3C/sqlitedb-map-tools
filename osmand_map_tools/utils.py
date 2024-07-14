from pathlib import Path


def _remove_file(file_path: Path, message: str, force: bool = False) -> None:
    if Path.is_file(file_path):
        if force:
            Path.unlink(file_path)
        else:
            print(message % str(file_path))
            exit(1)
