class TestCoresandbox:

    def test_coresandbox_example_content_schema_endpoint(self, manager_request):
        response = manager_request.get("/@types/example")
        assert response.status_code == 200
