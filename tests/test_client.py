"""
Tests for client.py
"""
import unittest
import uuid
import os

import client

DB_NAME = 'test.%s.db' % str(uuid.uuid4())

class TestClient(unittest.TestCase):
    """Test corresponding to client.py"""
    def setUp(self):
        self.cli = client.Client(db_name=DB_NAME)

    def test_add_and_remove(self):
        """Test that DLEXDB.__init__ created db file"""
        self.assertTrue(isinstance(self.cli.add('mydef', '/tmp/asdf'), int))
        self.assertEqual(self.cli.list()[0]['name'], 'mydef')
        self.assertTrue(self.cli.remove('mydef'))
        self.assertEqual(self.cli.list(), [])

    def test_experiment_crud(self):
        """Tests for basic experiment CRUD."""
        self.cli

    def tearDown(self):
        self.cli.close()
        os.remove(DB_NAME)
