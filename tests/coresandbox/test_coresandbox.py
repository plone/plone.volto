class TestCoresandbox:

    def test_coresandbox_example_content_schema_endpoint(self, api_manager_request):
        response = api_manager_request.get("/@types/example")
        assert response.status_code == 200
