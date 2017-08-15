"""
This module defines the main interface for running dlex experiments.
"""
import os

import db
import unix_rpc
from spawner import Spawner

class Client(object):
    """An object for executing CLI commands."""
    def __init__(self, db_path='test.db', socket_path='/tmp/sock_path'):
        self.db_path = db_path
        self.ddb = db.DLEXDB(db_path)
        self.socket_path = socket_path

    def close(self):
        # type: () -> ()
        """Close the CLI object."""
        self.ddb.close()

    def clean(self):
        """Removes all non-running experiments from state"""
        for exp in self.status():
            if exp['pid'] is None:
                self.ddb.delete_experiment(exp['id'])
            else:
                try:
                    # raises OSError if pid is dead
                    os.kill(exp['pid'], 0)
                except OSError:
                    self.ddb.delete_experiment(exp['id'])

    def add(self, def_name, def_path):
        # type: (str, str) -> bool
        """Creates a new experiment definition

        This command tries to create a new experiment. It does so by trying
        to load the module at `def_path`.

        Args:
            def_name: name of the experiment to create
            def_path: filesystem path containing the experiment (i.e. a class
            inheriting from the Experiment class)

        Returns:
            True on success, False on failure
        """
        def_id = self.ddb.insert_definition(def_name, def_path)
        if def_id is None:
            return False
        return True

    def remove(self, def_name):
        # type: (str) -> bool
        """Removes an experiment definition

        Args:
            def_name: name of the experiment definition to remove

        Returns:
            True on success, False on failure
        """
        return self.ddb.delete_definition(def_name)

    def list(self):
        # type: () -> List[Union[None, Dict[str, Union[int, str]]]]
        """Lists all experiment difinitions

        Returns:
            A list of all experiment definitions
        """
        return self.ddb.get_definitions()

    def run(self, def_name, hyperparams):
        # type: (str) -> Union[None, int]
        """Runs an experiment, based on definition `def_name`."""
        exp_id = self.ddb.create_experiment(def_name, hyperparams)
        if exp_id is None:
            return None
        spawner = Spawner(self.db_path, self.socket_path, exp_id)
        spawner.run()
        return exp_id

    def status(self):
        # type: () -> List[Any]
        """Returns the status of all experiments"""
        status = self.ddb.get_status()
        client = unix_rpc.Client(self.socket_path)
        for exp in status:
            exp['status'] = client.get_status(exp['id'])
            exp['loss'] = client.get_loss(exp['id'])
            exp['epoch'] = client.get_epoch(exp['id'])
        return status

    def pause(self, exp_id):
        client = unix_rpc.Client(self.socket_path)

    def unpause(self, exp_id):
        pass

    def get_datasets(self):
        """List all known datasets"""
        return self.ddb.get_datasets()
