from tests.mock_app import TestBasicApp
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from app.models import metadata, users, posts

EXIST_USERNAME = 'postAuthor'
EXIST_PASSWORD = 'postAuthorPassword'

class TestRoutePost(TestBasicApp):
    def setUp(self):
        super().setUp()
        self.conn = self.flask_app.db_engine.connect()
        result = self.conn.execute(users.insert().returning(users.c.id, users.c.username),
            username=EXIST_USERNAME, password=generate_password_hash(EXIST_PASSWORD))
        user = result.fetchone()
        self.user_id = user[users.c.id]
        self.identity = {
            'id': self.user_id,
            'username': user[users.c.username],
        }

    def getAccessToken(self):
        with self.flask_app.app_context():
            return create_access_token(identity=self.identity)

    def createPost(self, author_id, title, body):
        result = self.conn.execute(posts.insert().returning(posts.c.id, posts.c.title, posts.c.body),
            author_id=author_id, title=title, body=body)
        post = result.fetchone()
        return post

    def tearDown(self):
        super().tearDown()
        metadata.drop_all(self.flask_app.db_engine)

    def test_success_to_create_post(self):
        with self.flask_app.test_client() as client:
            post_title = 'Some Post Title'
            post_body = {
                'key1': 'value1',
                'key2': [
                    'array value 1',
                    'array value 2',
                ],
                'key3': {
                    'key3.1': 'deep value',
                },
            }
            res = client.post(
                '/posts/',
                headers={
                    'Authorization': 'Bearer {}'.format(self.getAccessToken()),
                },
                json={
                    'title': post_title,
                    'body': post_body,
                },
            )
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertTrue(res_json['data']['post']['id'])
            self.assertEqual(res_json['data']['post']['title'], post_title)
            self.assertEqual(res_json['data']['post']['body'], post_body)

    def test_success_to_read_existing_post(self):
        post_title = 'POST TITLE'
        post_body = {
            'key1': 'value1',
            'key2': 'value2',
        }
        exist_post = self.createPost(self.user_id, post_title, post_body)
        with self.flask_app.test_client() as client:
            res = client.get('/posts/{}'.format(exist_post.id))
            res_json = res.get_json()
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res_json['code'], 200)
            self.assertTrue(res_json['data']['post']['id'])
            self.assertEqual(res_json['data']['post']['title'], post_title)
            self.assertEqual(res_json['data']['post']['body'], post_body)

    def test_fail_to_read_non_existing_post(self):
        with self.flask_app.test_client() as client:
            res = client.get('/posts/0')
            res_json = res.get_json()
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res_json['code'], 404)
            self.assertTrue(res_json['data']['message'])
