from tests.mock_app import TestBasicApp
from werkzeug.security import generate_password_hash

from app.models import metadata, users

EXIST_USERNAME = 'existuser'
EXIST_PASSWORD = 'existpassword'

FAKE_USERNAME = 'fakeuser'
FAKE_PASSWORD = 'fakepassword'

class TestApp(TestBasicApp):
    def setUp(self):
        super().setUp()
        self.conn = self.flask_app.db_engine.connect()
        self.conn.execute(users.insert(),
            username=EXIST_USERNAME, password=generate_password_hash(EXIST_PASSWORD))

    def tearDown(self):
        super().tearDown()
        metadata.drop_all(self.flask_app.db_engine)

    def test_success_to_get_info(self):
        with self.flask_app.test_client() as client:
            res = client.get('/info')
            self.assertEqual(res.status_code, 200)

    def test_success_to_register_new_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/register', json={
                'username': FAKE_USERNAME,
                'password': FAKE_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['user']['username'], FAKE_USERNAME)

    def test_fail_to_register_new_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/register', json={
                'username': EXIST_USERNAME,
                'password': EXIST_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 400)
            self.assertTrue(res_json['error'])

    def test_success_to_login_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': EXIST_USERNAME,
                'password': EXIST_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertTrue(res_json['access_token'])

    def test_fail_to_login_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': EXIST_USERNAME,
                'password': 'wrongpassword',
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 401)
            self.assertTrue(res_json['error'])

    def test_fail_to_login_non_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': 'nonexistusername',
                'password': 'wrongpassword',
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 401)
            self.assertTrue(res_json['error'])
