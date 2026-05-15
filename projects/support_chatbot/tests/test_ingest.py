import os
from unittest.mock import patch, MagicMock
from src import ingest

@patch('src.ingest.shutil.rmtree')
@patch('src.ingest.os.path.exists')
def test_ingest_data_reindex(mock_exists, mock_rmtree, capsys):
    mock_exists.return_value = True
    
    with patch('src.ingest.TextLoader') as mock_loader, \
         patch('src.ingest.RecursiveCharacterTextSplitter') as mock_splitter, \
         patch('src.ingest.OpenAIEmbeddings') as mock_embeddings, \
         patch('src.ingest.Chroma') as mock_chroma:
         
        mock_loader_instance = MagicMock()
        mock_loader_instance.load.return_value = ["doc1"]
        mock_loader.return_value = mock_loader_instance
        
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.split_documents.return_value = ["chunk1"]
        mock_splitter.return_value = mock_splitter_instance
        
        ingest.ingest_data(reindex=True)
        
        from src.config import CHROMA_DB_DIR
        mock_rmtree.assert_called_with(CHROMA_DB_DIR)

@patch('src.ingest.os.path.exists')
def test_ingest_data_file_not_found(mock_exists, capsys):
    mock_exists.return_value = False
    
    ingest.ingest_data(reindex=False)
    
    captured = capsys.readouterr()
    assert "Error: Knowledge file not found" in captured.out
