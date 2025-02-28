from dotenv import load_dotenv
import os

# curr_file_path = os.path.dirname(os.path.abspath(__file__))
# dotenv_path = os.path.join(curr_file_path, '.env')
if load_dotenv():
    print(f"Loaded environment variables")
else:
    print(f"Failed to load environment variables")

# SWAP THESE WITH YOUR OWN VALUES IF TESTING LOCALLY
local_creds = {
    'SECRET_KEY': os.getenv('LOCAL_SECRET_KEY'),
    'ACCESS_KEY': os.getenv('LOCAL_ACCESS_KEY'),
    'ENDPOINT': "http://localhost:9090/Monolith_Dev/api",
    'LLM_CHAT_ENGINE_ID': '4801422a-5c62-421e-a00c-05c6a9e15de8',
    'LLM_EMBEDDING_ENGINE_ID': '',
    'VECTOR_ENGINE_ID': 'dae9096d-1891-4077-b8bc-63ecdce08e14',
    'DATABASE_ENGINE_ID': '515721c0-340f-42fa-b3ff-138882b8b75b'
}

# Don't change these values unless there are problems ie. permissions, etc.
dev_creds = {
    'SECRET_KEY': os.getenv('DEV_SECRET_KEY'),
    'ACCESS_KEY': os.getenv('DEV_ACCESS_KEY'),
    'ENDPOINT': "https://workshop.cfg.deloitte.com/cfg-ai-dev/Monolith/api",
    'LLM_CHAT_ENGINE_ID': '4801422a-5c62-421e-a00c-05c6a9e15de8',
    'LLM_EMBEDDING_ENGINE_ID': 'e4449559-bcff-4941-ae72-0e3f18e06660',
    'VECTOR_ENGINE_ID': '1222b449-1bc6-4358-9398-1ed828e4f26a',
    'DATABASE_ENGINE_ID': '950eb187-e352-444d-ad6a-6476ed9390af',
    'STORAGE_ENGINE_ID': '2d905aa3-b703-4c98-8133-5bcaefddac1e',
}

# SWAP THIS VALUE TO CHANGE BETWEEN LOCAL AND DEV CREDENTIALS
active_creds = dev_creds

# These are the variables that will be used in the tests
SECRET_KEY = active_creds['SECRET_KEY']
ACCESS_KEY = active_creds['ACCESS_KEY']
ENDPOINT = active_creds['ENDPOINT']
LLM_CHAT_ENGINE_ID = active_creds['LLM_CHAT_ENGINE_ID']
LLM_EMBEDDING_ENGINE_ID = active_creds['LLM_EMBEDDING_ENGINE_ID']
VECTOR_ENGINE_ID = active_creds['VECTOR_ENGINE_ID']
DATABASE_ENGINE_ID = active_creds['DATABASE_ENGINE_ID']
STORAGE_ENGINE_ID = active_creds['STORAGE_ENGINE_ID']
