from reaper import Reaper
import logger

logger = logger.get_logger(__name__)

if __name__ == "__main__":
    """Initialize Reaper"""

    logger.info("Initializing the reaper.")
    reaper = Reaper()
    reaper.harvest()
