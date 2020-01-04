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

    def test_success_to_response_when_uncaught_internal_error(self):
        with self.flask_app.test_client() as client:
            res = client.get('/errors/uncaught')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 500)
            self.assertEqual(res_json['code'], 500)
            self.assertTrue(res_json['data']['message'])

    def test_success_to_catch_generic_error(self):
        with self.flask_app.test_client() as client:
            res = client.get('/errors/4xx')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res_json['code'], 400)
            self.assertTrue(res_json['data']['message'])

        with self.flask_app.test_client() as client:
            res = client.get('/errors/5xx')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 500)
            self.assertEqual(res_json['code'], 500)
            self.assertTrue(res_json['data']['message'])
