from dotenv import load_dotenv
import os

# curr_file_path = os.path.dirname(os.path.abspath(__file__))
# dotenv_path = os.path.join(curr_file_path, '.env')
if load_dotenv():
    print(f"Loaded environment variables")
else:
    print(f"Failed to load environment variables")

# Insert these in .env file
local_creds = {
    'SECRET_KEY': os.getenv('LOCAL_SECRET_KEY'),
    'ACCESS_KEY': os.getenv('LOCAL_ACCESS_KEY'),
    'ENDPOINT': os.getenv('LOCAL_ENDPOINT'),
    'LLM_CHAT_ENGINE_ID': os.getenv('LOCAL_LLM_CHAT_ENGINE_ID'),
    'LLM_EMBEDDING_ENGINE_ID': os.getenv('LOCAL_LLM_EMBEDDING_ENGINE_ID'), 
    'VECTOR_ENGINE_ID': os.getenv('LOCAL_VECTOR_ENGINE_ID'),
    'DATABASE_ENGINE_ID': os.getenv('LOCAL_DATABASE_ENGINE_ID'),
    'STORAGE_ENGINE_ID': os.getenv('LOCAL_STORAGE_ENGINE_ID'),
}

# Don't change these values unless there are problems ie. permissions, etc.
dev_creds = {
    'SECRET_KEY': os.getenv('DEV_SECRET_KEY'),
    'ACCESS_KEY': os.getenv('DEV_ACCESS_KEY'),
    'ENDPOINT': os.getenv('DEV_ENDPOINT'),
    'LLM_CHAT_ENGINE_ID': os.getenv('DEV_LLM_CHAT_ENGINE_ID'),
    'LLM_EMBEDDING_ENGINE_ID': os.getenv('DEV_LLM_EMBEDDING_ENGINE_ID'),
    'VECTOR_ENGINE_ID': os.getenv('DEV_VECTOR_ENGINE_ID'),
    'DATABASE_ENGINE_ID': os.getenv('DEV_DATABASE_ENGINE_ID'),
    'STORAGE_ENGINE_ID': os.getenv('DEV_STORAGE_ENGINE_ID'),
}

# Dynamically select the credentials dictionary
active_creds = os.getenv('ACTIVE_CREDS')
if active_creds == 'local_creds':
    active_creds = local_creds
elif os.getenv('ACTIVE_CREDS') == 'dev_creds':
    active_creds = dev_creds
else:
    raise ValueError(f"Invalid value for ACTIVE_CREDS: {active_creds}")

# These are the variables that will be used in the tests
SECRET_KEY = active_creds['SECRET_KEY']
ACCESS_KEY = active_creds['ACCESS_KEY']
ENDPOINT = active_creds['ENDPOINT']
LLM_CHAT_ENGINE_ID = active_creds['LLM_CHAT_ENGINE_ID']
LLM_EMBEDDING_ENGINE_ID = active_creds['LLM_EMBEDDING_ENGINE_ID']
VECTOR_ENGINE_ID = active_creds['VECTOR_ENGINE_ID']
DATABASE_ENGINE_ID = active_creds['DATABASE_ENGINE_ID']
STORAGE_ENGINE_ID = active_creds['STORAGE_ENGINE_ID']