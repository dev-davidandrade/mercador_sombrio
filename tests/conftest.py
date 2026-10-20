import pytest
from fastapi.testclient import TestClient
from backend.main import create_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / 'test.db'))
    monkeypatch.delenv('OLLAMA_API_KEY', raising=False)
    monkeypatch.setenv('OLLAMA_HOST', 'https://ollama.com')
    with TestClient(create_app()) as c:
        yield c
