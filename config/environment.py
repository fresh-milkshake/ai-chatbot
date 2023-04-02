import os

import dotenv

dotenv.load_dotenv()

# Credentials
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Startup
PRODUCTION = bool(os.environ.get('PRODUCTION', 1))

# Redis
REIDS_PASSWORD = os.environ.get('REIDS_PASSWORD', None)