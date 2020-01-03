from tests.mock_app import TestBasicApp

class TestApp(TestBasicApp):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_success_to_get_api_root(self):
        with self.flask_app.test_client() as client:
            res = client.get('/')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)

    def test_success_to_get_info(self):
        with self.flask_app.test_client() as client:
            res = client.get('/info')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
