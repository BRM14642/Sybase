import uno

from src.utils.logging_config import logger


def test_uno():
    try:
        local_context = uno.getComponentContext()
        logger.info("uno module is configured correctly.")
    except Exception as e:
        logger.info(f"Error: {e}")

test_uno()