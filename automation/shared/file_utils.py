from pathlib import Path


def ensure_directory_exists(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)
