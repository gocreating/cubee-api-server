import unittest

from app import create_app, db

class TestBasicApp(unittest.TestCase):
    def setUp(self):
        self.flask_app = create_app()

    def tearDown(self):
        pass
