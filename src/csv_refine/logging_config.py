import logging
from pathlib import Path


def configure_logging() -> None:
    path = Path("logs")

    if not path.is_dir():
        path.mkdir(parents=True)

    logging.basicConfig(
        filename=path / "app.log",
        filemode="a",
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(filename)s:%(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
