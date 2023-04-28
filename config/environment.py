import os
import dotenv

dotenv.load_dotenv()

# Credentials
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Startup
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE')

# Redis
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', None)
