import logging
from rich.logging import RichHandler

formatter = logging.Formatter("%(message)s")
handler = RichHandler(level=logging.WARNING, markup=True)
handler.setFormatter(formatter)

logger = logging.getLogger("micro_fr_pred")
logger.addHandler(handler)
