import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from analyze_dna.update_clinvar import download_clinvar

def test_download_clinvar_checksum_success(tmp_path):
    dest = tmp_path / "variant_summary.txt.gz"
    url = "https://example.com/data.gz"
    md5_url = url + ".md5"

    content = b"fake clinvar data"
    expected_hash = hashlib.md5(content).hexdigest()
    # NCBI MD5 format: "hash  filename"
    md5_content = f"{expected_hash}  variant_summary.txt.gz".encode()

    def mock_urlretrieve(url_arg, dest_arg, reporthook=None):
        if url_arg == md5_url:
            Path(dest_arg).write_bytes(md5_content)
        elif url_arg == url:
            Path(dest_arg).write_bytes(content)
        return (str(dest_arg), None)

    with patch("urllib.request.urlretrieve", side_effect=mock_urlretrieve):
        # This should succeed when implemented
        download_clinvar(url, dest, show_progress=False)

    assert dest.exists()
    assert dest.read_bytes() == content

def test_download_clinvar_checksum_failure(tmp_path):
    dest = tmp_path / "variant_summary.txt.gz"
    url = "https://example.com/data.gz"
    md5_url = url + ".md5"

    content = b"fake clinvar data"
    wrong_hash = "0" * 32
    md5_content = f"{wrong_hash}  variant_summary.txt.gz".encode()

    def mock_urlretrieve(url_arg, dest_arg, reporthook=None):
        if url_arg == md5_url:
            Path(dest_arg).write_bytes(md5_content)
        elif url_arg == url:
            Path(dest_arg).write_bytes(content)
        return (str(dest_arg), None)

    with patch("urllib.request.urlretrieve", side_effect=mock_urlretrieve):
        # This should raise an exception when implemented
        with pytest.raises(ValueError, match="Checksum mismatch"):
            download_clinvar(url, dest, show_progress=False)
