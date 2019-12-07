import unittest

from app import db
from app.main import create_app

class TestBasicApp(unittest.TestCase):
    def setUp(self):
        self.flask_app = create_app()

    def tearDown(self):
        pass
