from app import application
from loguru import logger
import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', required=True)

if __name__ == "__main__":
    logger.info("Starting application")
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Ending process")
