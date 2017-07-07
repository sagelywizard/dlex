"""
This module defines the main interface for running dlex experiments.
"""
import db
import unix_rpc

class Client(object):
    """An object for executing CLI commands."""
    def __init__(self, db_name='test.db', socket_path='/tmp/sock_path'):
        self.ddb = db.DLEXDB(db_name)
        self.socket_path = socket_path

    def close(self):
        # type: () -> ()
        """Close the CLI object."""
        self.ddb.close()

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
        print('run')
        exp_id = self.ddb.create_experiment(def_name, hyperparams)
        client = unix_rpc.Client(self.socket_path)
        client.run('arg1', exp_id=exp_id)
        return exp_id

    def status(self):
        # type: () -> List[Any]
        """Returns the status of all experiments"""
        return self.ddb.get_status()
