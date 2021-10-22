from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest import fixture


@fixture
def api_client(app: FastAPI) -> TestClient:
    return TestClient(app)
