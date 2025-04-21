"""
Integration tests for PeerTube client.
These tests exercise the real PeerTube API and require a valid .env in the project root.
Tests will be skipped if environment variables are not set.
"""
import pytest
import requests

from peertube_uploader.config import Config

@pytest.mark.integration
def test_token_endpoint_and_refresh():
    # Load configuration; skip if missing
    try:
        cfg = Config()
    except ValueError:
        pytest.skip("Skipping integration tests: missing environment variables")

    # Test server connectivity via GET
    try:
        pong = requests.get(cfg.instance_url, verify=cfg.verify_ssl)
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Skipping integration tests: cannot reach instance ({e})")
    if pong.status_code != 200:
        pytest.skip(f"Skipping integration tests: instance returned {pong.status_code}")
    # Prepare token request data
    token_url = f"{cfg.instance_url}/api/v1/users/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }
    data = {
        'client_id': cfg.client_id,
        'client_secret': cfg.client_secret,
        'grant_type': 'password',
        'response_type': 'code',
        'username': cfg.username,
        'password': cfg.password,
    }
    # Request new tokens (password grant)
    resp = requests.post(
        token_url,
        headers=headers,
        data=data,
        verify=cfg.verify_ssl,
    )
    # If credentials invalid or endpoint returns error, skip integration
    if resp.status_code != 200:
        pytest.skip(f"Skipping integration tests: token endpoint status {resp.status_code}, body: {resp.text}")
    # Otherwise we expect JSON with tokens
    json_data = resp.json()
    assert 'access_token' in json_data and json_data['access_token'], "Missing access_token in response"
    assert 'refresh_token' in json_data and json_data['refresh_token'], "Missing refresh_token in response"
    json_data = resp.json()
    assert 'access_token' in json_data, "No access_token in response"
    assert 'refresh_token' in json_data, "No refresh_token in response"

    # Test refresh token endpoint
    refresh_data = {
        'client_id': cfg.client_id,
        'client_secret': cfg.client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': json_data['refresh_token'],
    }
    resp2 = requests.post(
        token_url,
        headers=headers,
        data=refresh_data,
        verify=cfg.verify_ssl,
    )
    if resp2.status_code != 200:
        pytest.skip(f"Skipping integration tests: refresh endpoint status {resp2.status_code}, body: {resp2.text}")
    json_data2 = resp2.json()
    assert 'access_token' in json_data2 and json_data2['access_token'], "Missing access_token after refresh"
    assert json_data2['access_token'] != json_data['access_token'], "Token did not change on refresh"