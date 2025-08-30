import pytest
import os
import sys
import tempfile
import shutil
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_openai():
    with patch('openai.OpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        
        mock_client.embeddings.create.return_value.data = [MagicMock(embedding=[0.1] * 1536)]
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        yield mock_client

@pytest.fixture
def sample_pdf_content():
    return "This is a sample PDF content for testing RAG functionality."

@pytest.fixture
def mock_chromadb():
    with patch('chromadb.PersistentClient') as mock:
        mock_client = MagicMock()
        mock_collection = MagicMock()
        
        mock_client.get_or_create_collection.return_value = mock_collection
        mock.return_value = mock_client
        
        mock_collection.query.return_value = {
            'documents': [['Sample document content']],
            'metadatas': [{'source': 'test.pdf'}],
            'distances': [[0.5]]
        }
        
        yield mock_client

@pytest.fixture
def mock_streamlit():
    with patch.dict('sys.modules', {'streamlit': MagicMock()}):
        yield

@pytest.fixture
def sample_investment_data():
    return {
        'company': 'Test Company',
        'sector': 'Technology',
        'revenue': 1000000,
        'profit': 100000,
        'assets': 5000000,
        'liabilities': 2000000
    }

@pytest.fixture(autouse=True)
def env_setup():
    os.environ['OPENAI_API_KEY'] = 'test-key'
    yield
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']