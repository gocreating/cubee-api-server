from tests.mock_app import TestBasicApp
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token, get_csrf_token

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

    def test_success_to_register_new_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/register', json={
                'username': FAKE_USERNAME,
                'password': FAKE_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertEqual(res_json['data']['user']['username'], FAKE_USERNAME)

    def test_fail_to_register_new_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/register', json={
                'username': EXIST_USERNAME,
                'password': EXIST_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 422)
            self.assertEqual(res_json['code'], 422)
            self.assertTrue(res_json['data']['message'])

    def test_success_to_login_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': EXIST_USERNAME,
                'password': EXIST_PASSWORD,
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertTrue(res_json['data']['access_token'])
            self.assertTrue(res_json['data']['csrf_token'])
            self.assertTrue(res_json['data']['user'])
            tokenCookieList = [cookie for cookie in client.cookie_jar if cookie.name == 'access_token_cookie']
            csrfTokenCookieList = [cookie for cookie in client.cookie_jar if cookie.name == 'csrf_access_token']
            self.assertEqual(len(tokenCookieList), 1)
            self.assertEqual(len(csrfTokenCookieList), 1)
            tokenCookie = tokenCookieList[0]
            csrfTokenCookie = csrfTokenCookieList[0]
            self.assertEqual(tokenCookie.value, res_json['data']['access_token'])
            self.assertEqual(csrfTokenCookie.value, res_json['data']['csrf_token'])

    def test_fail_to_login_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': EXIST_USERNAME,
                'password': 'wrongpassword',
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 401)
            self.assertEqual(res_json['code'], 401)
            self.assertTrue(res_json['data']['message'])

    def test_fail_to_login_non_exist_user(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/login', json={
                'username': 'nonexistusername',
                'password': 'wrongpassword',
            })
            res_json = res.get_json()
            self.assertEqual(res.status_code, 401)
            self.assertEqual(res_json['code'], 401)
            self.assertTrue(res_json['data']['message'])

    def test_success_to_access_user(self):
        with self.flask_app.test_client() as client:
            access_token = client.post('/auth/login', json={
                'username': EXIST_USERNAME,
                'password': EXIST_PASSWORD,
            }).get_json()['data']['access_token']

            res = client.get('/users/me', headers={
                'Authorization': 'Bearer {}'.format(access_token),
            })
            res_json = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertTrue(res_json['data']['user'])

    def test_fail_to_access_user_without_token(self):
        with self.flask_app.test_client() as client:
            res = client.get('/users/me')
            res_json = res.get_json()

            self.assertEqual(res.status_code, 401)
            self.assertEqual(res_json['code'], 401)

    def test_fail_to_access_user_with_invalid_token(self):
        with self.flask_app.test_client() as client:
            res = client.get('/users/me', headers={
                'Authorization': 'Bearer ThisIsAnInvalidToken',
            })
            res_json = res.get_json()

            self.assertEqual(res.status_code, 401)
            self.assertEqual(res_json['code'], 401)

    def test_success_to_logout_logged_in_user(self):
        with self.flask_app.test_client() as client:
            access_token = ''
            with self.flask_app.app_context():
                identity = {
                    'id': '1',
                    'username': EXIST_USERNAME,
                }
                access_token = create_access_token(identity=identity)
                csrf_token = get_csrf_token(access_token)
            client.set_cookie('.example.com', 'access_token_cookie', access_token)
            res = client.post('/auth/logout', headers={
                'X-CSRF-TOKEN': csrf_token,
            })
            res_json = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertEqual(res_json['data']['user']['username'], EXIST_USERNAME)
            self.assertEqual(len(res.headers.getlist('Set-Cookie')), 4) # access_token_cookie, csrf_access_token, refresh_token_cookie, csrf_refresh_token

    def test_fail_to_logout_without_access_token(self):
        with self.flask_app.test_client() as client:
            res = client.post('/auth/logout')
            res_json = res.get_json()

            self.assertEqual(res.status_code, 401)
            self.assertEqual(res_json['code'], 401)
