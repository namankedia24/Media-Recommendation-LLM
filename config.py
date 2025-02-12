import os

ROOT_DIR: str = '.'

DATA_DIR: str = os.path.join(ROOT_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
ORIGINAL_DATA_DIR: str = os.path.join(DATA_DIR, 'original')
os.makedirs(ORIGINAL_DATA_DIR, exist_ok=True)
PROCESSED_DATA_DIR: str = os.path.join(DATA_DIR, 'processed')
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
VECTOR_STORE_DIR: str = os.path.join(DATA_DIR, 'vector_store')
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

EMBED_MODEL_NAME: str = 'all-MiniLM-L6-v2'  # TODO
LLM_MODEL_NAME: str = 'meta-llama/Llama-3.3-70B-Instruct-Turbo'  # TODO
