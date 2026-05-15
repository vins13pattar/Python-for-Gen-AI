import os
from unittest.mock import patch, MagicMock
from src import vectorstore

@patch('src.vectorstore.os.path.exists')
def test_get_retriever_no_dir(mock_exists):
    mock_exists.return_value = False
    retriever = vectorstore.get_retriever()
    assert retriever is None

@patch('src.vectorstore.Chroma')
@patch('src.vectorstore.OpenAIEmbeddings')
@patch('src.vectorstore.os.path.exists')
def test_get_retriever_success(mock_exists, mock_embeddings, mock_chroma):
    mock_exists.return_value = True
    
    mock_chroma_instance = MagicMock()
    mock_retriever = MagicMock()
    mock_chroma_instance.as_retriever.return_value = mock_retriever
    mock_chroma.return_value = mock_chroma_instance
    
    retriever = vectorstore.get_retriever()
    assert retriever == mock_retriever
    mock_chroma_instance.as_retriever.assert_called_once_with(search_kwargs={"k": 4})
