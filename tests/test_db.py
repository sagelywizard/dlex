"""
Tests for db.py
"""
import unittest
import uuid
import os

import db

DB_NAME = 'test.%s.db' % str(uuid.uuid4())

class TestDLEXDB(unittest.TestCase):
    """Test corresponding to db.py"""
    def setUp(self):
        self.ddb = db.DLEXDB(DB_NAME)

    def test_db_exists(self):
        """Test that DLEXDB.__init__ created db file"""
        self.assertTrue(os.path.isfile(DB_NAME))

    def test_definition_crud(self):
        """Tests for basic definition CRUD."""
        self.assertTrue(self.ddb.insert_definition('exp1', '/a/b/c'))
        self.assertTrue(self.ddb.insert_definition('exp2', '/d/e/f'))
        self.assertTrue(self.ddb.insert_definition('exp3', '/a/b/c'))
        # Don't re-insert
        self.assertFalse(self.ddb.insert_definition('exp1', '/a/b/c'))
        self.assertFalse(self.ddb.insert_definition('exp2', '/d/e/f'))
        self.assertFalse(self.ddb.insert_definition('exp3', '/a/b/c'))

        exps = self.ddb.get_definitions()
        self.assertEqual(len(exps), 3)
        self.assertEqual(self.ddb.get_definition('exp1')['name'], 'exp1')
        self.assertEqual(self.ddb.get_definition('exp2')['name'], 'exp2')
        self.assertEqual(self.ddb.get_definition('exp3')['name'], 'exp3')
        self.assertEqual(self.ddb.get_definition('exp1')['path'], '/a/b/c')
        self.assertEqual(self.ddb.get_definition('exp2')['path'], '/d/e/f')
        self.assertEqual(self.ddb.get_definition('exp3')['path'], '/a/b/c')

        self.assertTrue(self.ddb.delete_definition('exp1'))
        self.assertFalse(self.ddb.get_definition('exp1'))
        self.assertTrue(self.ddb.delete_definition('exp2'))
        self.assertFalse(self.ddb.get_definition('exp2'))
        self.assertTrue(self.ddb.delete_definition('exp3'))
        self.assertFalse(self.ddb.get_definition('exp3'))

    def test_experiment_crud(self):
        self.assertTrue(self.ddb.insert_definition('exp1', '/a/b/c'))
        exp_id = self.ddb.create_experiment('exp1', {'k1': 'v1'})
        self.assertEqual(exp_id, 1)
        exp = self.ddb.get_experiment(exp_id)
        self.assertEqual(exp['hyperparams']['k1'], 'v1')
        self.assertTrue(self.ddb.delete_experiment(exp_id))
        self.assertIsNone(self.ddb.get_experiment(exp_id))

    def tearDown(self):
        self.ddb.close()
        os.remove(DB_NAME)
