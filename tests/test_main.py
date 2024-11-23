from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


def test_read_images():
    response = client.get("/images")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_results_endpoint():
    response = client.post(
        "/results",
        json={
            "data": ["abstract", "modern"],
            "contact": {
                "fname": "Test",
                "lname": "User",
                "email": "test.user@example.com",
                "testing": True
            }
        }
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "result" in json_data
    assert "output" in json_data
    assert len(json_data["result"]) > 0
    assert len(json_data["output"]) > 0


# Imagekit Mock
class MockedImageKitResponse:
    def __init__(self):
        self.response_metadata = self
        self.raw = [
            {"fileId": "mocked_file_id",
                "url": "https://example.com/image.jpg", "tags": ["abstract"]}
        ]

    @property
    def status(self):
        return 200


@patch("main.imagekit.list_files")
def test_results_endpoint_with_mocked_imagekit(mock_list_files):
    # Setup the mock
    mock_list_files.return_value = MockedImageKitResponse()

    response = client.post(
        "/results",
        json={
            "data": ["abstract", "modern"],
            "contact": {
                "fname": "Test",
                "lname": "User",
                "email": "test.user@example.com",
                "testing": True
            }
        }
    )
    assert response.status_code == 200


# Google Sheets Mock
class MockedGSpreadClient:
    def open(self, sheet_name):
        return MockedSheet()


class MockedSheet:
    def __init__(self):
        self.sheet1 = self

    def append_row(self, row):
        pass  # Do nothing or store the row in a list for assertions


@patch("main.gspread.authorize")
def test_results_endpoint_with_mocked_gsheets(mock_authorize):
    # Setup the mock
    mock_authorize.return_value = MockedGSpreadClient()

    response = client.post(
        "/results",
        json={
            "data": ["abstract", "modern"],
            "contact": {
                "fname": "Test",
                "lname": "User",
                "email": "test.user@example.com",
                "testing": True
            }
        }
    )
    assert response.status_code == 200
