from app import application
from loguru import logger

if __name__ == "__main__":
    logger.info("Starting application")
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Ending process")
