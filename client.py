"""
This module defines the main interface for running dlex experiments.
"""
import db # pylint: disable=unused-import

class Client(object):
    """An object for executing CLI commands."""
    def __init__(self, db_name='test.db'):
        self.ddb = db.DLEXDB(db_name)

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

    def create(self, def_name, hyperparams):
        # type: (str, Dict[str, Union[int, str]]) -> int
        """Creates a new experiment from a definition

        Args:
            def_name: (str) name of the experiment definition
            hyperparams: (dict) a dict of the hyperparams for the experiment

        Returns:
            The ID of the experiment
        """
        return self.ddb.create_experiment(def_name, hyperparams)
