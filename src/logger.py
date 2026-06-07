import logging
import sys
import warnings


def setup_logging() -> None:
    # Silencia avisos de depreciação do BeautifulSoup (e.g. lxml builder no Python 3.14+)
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="bs4")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
