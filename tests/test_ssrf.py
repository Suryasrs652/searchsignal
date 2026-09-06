import pytest
from app.core.ssrf import validate_target_url

def test_ssrf_blocks_private_ips():
    # Loopback
    is_safe, msg = validate_target_url("http://127.0.0.1:8080/test", allow_local_test=False)
    assert not is_safe
    assert "blocked" in msg.lower() or "restricted" in msg.lower()

    # Cloud metadata
    is_safe, msg = validate_target_url("http://169.254.169.254/latest/meta-data/", allow_local_test=False)
    assert not is_safe

    # RFC 1918 Private Range
    is_safe, msg = validate_target_url("http://10.0.0.1/admin", allow_local_test=False)
    assert not is_safe

    is_safe, msg = validate_target_url("http://192.168.1.1/router", allow_local_test=False)
    assert not is_safe

def test_ssrf_blocks_invalid_schemes_and_credentials():
    # Scheme
    is_safe, msg = validate_target_url("file:///etc/passwd")
    assert not is_safe
    assert "scheme" in msg.lower()

    # Userinfo / credentials
    is_safe, msg = validate_target_url("http://admin:password@example.com")
    assert not is_safe
    assert "credential" in msg.lower()

def test_ssrf_allows_safe_urls():
    is_safe, _ = validate_target_url("https://example.com/blog")
    assert is_safe

def test_ssrf_permits_local_when_explicitly_configured():
    is_safe, _ = validate_target_url("http://127.0.0.1:8089/200", allow_local_test=True)
    assert is_safe
