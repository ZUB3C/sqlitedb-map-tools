from pathlib import Path


def _remove_file(file_path: Path, message: str, force: bool = False) -> None:
    if file_path.is_file():
        if force:
            Path.unlink(file_path)
        else:
            print(message % str(file_path))
            exit(1)
