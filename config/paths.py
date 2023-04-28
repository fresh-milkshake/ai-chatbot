import os

# Paths
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = '' or os.path.basename(PROJECT_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

USERS_DATA_FILE_NAME = 'users.json'
USERS_DATA_PATH = os.path.join(DATA_DIR, USERS_DATA_FILE_NAME)
REPORTS_PATH = os.path.join(DATA_DIR, 'reports')