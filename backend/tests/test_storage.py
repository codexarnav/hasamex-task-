"""Tests for local file storage abstraction and security."""
import pytest
from uuid import uuid4
from app.storage.local import LocalStorage
from app.core.exceptions import FileStorageError


def test_storage_save_and_read(tmp_path):
    storage = LocalStorage()
    storage.base_dir = tmp_path

    project_id = uuid4()
    content = b"Sample interview guide content"
    rel_path = storage.save(project_id, "guide.txt", content)

    read_bytes = storage.read(rel_path)
    assert read_bytes == content

    read_text = storage.read_text(rel_path)
    assert read_text == "Sample interview guide content"


def test_storage_path_traversal_prevention(tmp_path):
    storage = LocalStorage()
    storage.base_dir = tmp_path

    project_id = uuid4()
    # Test path traversal filename sanitization
    rel_path = storage.save(project_id, "../../etc/passwd", b"malicious")
    assert ".." not in rel_path
    assert str(project_id) in rel_path


def test_storage_delete(tmp_path):
    storage = LocalStorage()
    storage.base_dir = tmp_path

    project_id = uuid4()
    rel_path = storage.save(project_id, "doc.txt", b"temp text")
    assert storage.read(rel_path) == b"temp text"

    storage.delete(rel_path)
    with pytest.raises(FileStorageError):
        storage.read(rel_path)
