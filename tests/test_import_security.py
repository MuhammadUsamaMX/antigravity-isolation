import io
import os
import sys
import shutil
import zipfile
import tarfile
import pytest

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app import app, ANTIGRAVITY_PROFILES_DIR

@pytest.fixture(autouse=True)
def cleanup_profiles():
    # Teardown / cleanup before and after tests
    yield
    if os.path.exists(ANTIGRAVITY_PROFILES_DIR):
        for item in os.listdir(ANTIGRAVITY_PROFILES_DIR):
            item_path = os.path.join(ANTIGRAVITY_PROFILES_DIR, item)
            try:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.unlink(item_path)
            except Exception:
                pass

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def create_test_zip(files_dict):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname, content in files_dict.items():
            zf.writestr(fname, content)
    buffer.seek(0)
    return buffer

def create_test_tar(files_dict):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as tar:
        for fname, content in files_dict.items():
            data = content.encode('utf-8')
            ti = tarfile.TarInfo(name=fname)
            ti.size = len(data)
            tar.addfile(ti, io.BytesIO(data))
    buffer.seek(0)
    return buffer

def test_import_zip_path_traversal_blocked(client):
    """Test that zip archives with path traversal elements are rejected."""
    malicious_zip = create_test_zip({
        'validprofile/../../evil.txt': 'malicious content'
    })

    response = client.post(
        '/api/profiles/import',
        data={'file': (malicious_zip, 'validprofile.zip')},
        content_type='multipart/form-data'
    )

    json_data = response.get_json()
    assert response.status_code == 400
    assert 'error' in json_data

def test_import_tar_path_traversal_blocked(client):
    """Test that tar archives with path traversal elements are rejected."""
    malicious_tar = create_test_tar({
        'validprofile/../../evil.txt': 'malicious content'
    })

    response = client.post(
        '/api/profiles/import',
        data={'file': (malicious_tar, 'validprofile.tar.gz')},
        content_type='multipart/form-data'
    )

    json_data = response.get_json()
    assert response.status_code == 400
    assert 'error' in json_data

def test_import_zip_invalid_profile_name_blocked(client):
    """Test that zip archives resulting in invalid profile names are rejected."""
    malicious_zip = create_test_zip({
        '../invalid_name/file.txt': 'content'
    })

    response = client.post(
        '/api/profiles/import',
        data={'file': (malicious_zip, 'invalid.zip')},
        content_type='multipart/form-data'
    )

    json_data = response.get_json()
    assert response.status_code == 400
    assert 'error' in json_data

def test_import_valid_zip_succeeds(client):
    """Test that a valid zip archive imports successfully."""
    valid_zip = create_test_zip({
        'goodprofile/file.txt': 'good content',
        'goodprofile/Downloads/readme.txt': 'downloads'
    })

    response = client.post(
        '/api/profiles/import',
        data={'file': (valid_zip, 'goodprofile.zip')},
        content_type='multipart/form-data'
    )

    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data['status'] == 'imported'
    assert json_data['name'] == 'goodprofile'
    assert os.path.exists(os.path.join(ANTIGRAVITY_PROFILES_DIR, 'goodprofile', 'file.txt'))
