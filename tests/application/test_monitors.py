class TestMonitors:
    def test_200_ok_when_ping(self, api_client):
        url = api_client.app.url_path_for("monitors:ping")
        assert api_client.get(url).status_code == 200
