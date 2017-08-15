"""A wrapper around SQLite for dlex and dlexd state

See DLEXDB class docstring for usage.
"""

import sqlite3
import json
from typing import Dict, Any, List # pylint: disable=unused-import
from typing import Tuple, Union # pylint: disable=unused-import


def _defs_sql_to_json(rows):
    # type: (List[Tuple[int, str, str]]) -> List[Dict[str, Union[int, str]]]
    """Transform a row from an definition experiment table SQL query to JSON"""
    return [{'id': row[0], 'name': row[1], 'path': row[2]} for row in rows]

class DLEXDB(object):
    """A wrapper around sqlite3

    example:
        db = DLEXDB('~/mystate.db')
        db.insert_definition('exp_name')
        db.close()
    """
    def __init__(self, name='test.db'):
        self.name = name
        self.conn = sqlite3.connect(name)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' AND name='definitions'")

        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "CREATE TABLE definitions ("
                "  id    INTEGER PRIMARY KEY,"
                "  name  TEXT UNIQUE,"
                "  path  TEXT"
                ")")

        self.cursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' AND name='experiments'")

        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "CREATE TABLE experiments ("
                "  id             INTEGER PRIMARY KEY,"
                "  definition_id  INTEGER,"
                "  hyperparams    TEXT,"
                "  pid            INTEGER UNIQUE,"
                "  FOREIGN KEY    (definition_id) REFERENCES definitions(id)"
                ")")

        self.cursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' AND name='checkpoints'")

        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "CREATE TABLE checkpoints ("
                "  id INTEGER     PRIMARY KEY,"
                "  experiment_id  INTEGER,"
                "  FOREIGN KEY    (experiment_id) REFERENCES experiments(id)"
                ")")

        self.cursor.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' AND name='datasets'")

        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute(
                "CREATE TABLE datasets ("
                "  id INTEGER     PRIMARY KEY,"
                "  name           TEXT,"
                "  directory      TEXT"
                ")")


    def insert_definition(self, name, path):
        # type: (str, str) -> Union[bool, int]
        """Insert a new experiment definition"""
        try:
            self.cursor.execute(
                "INSERT INTO definitions (name, path)"
                "VALUES (?, ?)", (name, path))

            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return False

    def delete_definition(self, name):
        # type: (str) -> bool
        """Delete an experiment definition"""
        self.cursor.execute(
            "DELETE FROM definitions WHERE name=?", (name,))
        self.conn.commit()
        return self.cursor.rowcount

    def get_definition(self, name):
        # type: (str) -> Union[None, Dict[str, Union[int, str]]]
        """Query for an existing experiment definition by name.

        Args:
            name: the name of the experiment definition

        Returns:
            None if the experiment definition of name `name` doesn't exist.
            Otherwise returns a JSON object containing the experiment ID,
            experiment name, and experiment OS PID.
        """
        self.cursor.execute(
            "SELECT id, name, path"
            "  FROM definitions"
            "  WHERE name=?", (name,))
        resp = self.cursor.fetchall()
        if resp == []:
            return None
        return _defs_sql_to_json(resp)[0]

    def get_definitions(self):
        # type: () -> List[Union[None, Dict[str, Union[int, str]]]]
        """Return a list of all experiment definitions."""
        self.cursor.execute('SELECT * FROM definitions')
        return _defs_sql_to_json(self.cursor.fetchall())

    def set_pid(self, exp_id, pid):
        # type: (int, int) -> bool
        """Setter for experiment OS PID

        Args:
            exp_id: (int) experiment ID
            pid: (int) OS PID corresponding to experiment

        Returns:
            None
        """
        self.cursor.execute(
            "UPDATE experiments "
            "SET pid = ? "
            "WHERE id = ?",
            (pid, exp_id))
        self.conn.commit()
        return self.cursor.rowcount == 1

    def create_experiment(self, def_name, hyperparams):
        # type: (str, Dict[Any, Any]) -> Union[int, None]
        """Creates an experiment from a definition

        Args:
            def_name: name of the definition
            hyperparams: the hyperparams
        Returns:
            The ID of the experiment
        """
        self.cursor.execute(
            "INSERT INTO experiments"
            "  (definition_id, hyperparams)"
            "  SELECT id, ? FROM definitions WHERE name=?", (
                json.dumps(hyperparams), def_name))
        self.conn.commit()
        if self.cursor.rowcount == 0:
            return None
        return self.cursor.lastrowid

    def get_experiment(self, exp_id):
        # type: (int) -> Union[None, Dict[str, Union[int, str]]]
        """Reads an experiment given its ID

        Args:
            exp_id: the SQL ID of the experiment
        Returns:
            Either a SQL row containing the experiment data or None if it
            doesn't exist.
        """
        self.cursor.execute(
            "SELECT experiments.definition_id, definitions.path, "
            "       experiments.hyperparams, experiments.pid"
            "  FROM experiments"
            "  INNER JOIN definitions"
            "  ON experiments.definition_id == definitions.id"
            "  WHERE experiments.id=?"
            , (exp_id,))

        resp = self.cursor.fetchall()
        if resp == []:
            return None
        [(def_id, def_path, hyperparams, pid)] = resp
        return {
            'id': exp_id,
            'def_id': def_id,
            'def_path': def_path,
            'hyperparams': json.loads(hyperparams),
            'pid': pid}

    def delete_experiment(self, exp_id):
        # type: (int) -> bool
        """Deletes an experiment"""
        self.cursor.execute(
            "DELETE FROM experiments WHERE id=?", (exp_id,))
        self.conn.commit()
        return self.cursor.rowcount == 1

    def get_status(self):
        # type: () -> List[Any]
        """Gets the status of all experiments"""
        self.cursor.execute("SELECT id, hyperparams, pid FROM experiments")
        exps = []
        for exp_id, hyperparams, pid in self.cursor.fetchall():
            exps.append({'id': exp_id, 'hyperparams': hyperparams, 'pid': pid})
        return exps

    def get_datasets(self):
        # type: () -> List[Any]
        """Gets a list of all datasets"""
        self.cursor.execute("SELECT id, name, directory FROM datasets")
        datasets = []
        for d_id, name, directory in self.cursor.fetchall():
            datasets.append({'id': d_id, 'name': name, 'directory': directory})
        return datasets

    def close(self):
        # type: () -> None
        """Close the SQLite connection."""
        self.conn.close()
