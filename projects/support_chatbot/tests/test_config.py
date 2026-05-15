import os
from src import config

def test_config_paths():
    assert hasattr(config, 'BASE_DIR')
    assert hasattr(config, 'DATA_DIR')
    assert hasattr(config, 'CHROMA_DB_DIR')
    assert isinstance(config.CHUNK_SIZE, int)
    assert isinstance(config.CHUNK_OVERLAP, int)
    assert isinstance(config.COLLECTION_NAME, str)
