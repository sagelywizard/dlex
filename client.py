"""
This module defines the main interface for running dlex experiments.
"""
import os
import select
import multiprocessing

import selectable
import runner
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
        exp_id = self.ddb.create_experiment(def_name, hyperparams)
        if exp_id is None:
            return None
        def_path = self.ddb.get_definition(def_name)['path']
        spawner = Spawner(self.socket_path, def_path, exp_id, hyperparams)
        spawner.run()
        return exp_id

    def status(self):
        # type: () -> List[Any]
        """Returns the status of all experiments"""
        return self.ddb.get_status()

class Spawner(multiprocessing.Process):
    """A process to fork the model runner daemon.

    This wrapper is necessary so as to not cause the os.fork to copy the CLI.
    """
    def __init__(self, socket_path, def_path, exp_id, hyperparams):
        self.socket_path = socket_path
        self.def_path = def_path
        self.exp_id = exp_id
        self.hyperparams = hyperparams
        super(Spawner, self).__init__()

    def run(self):
        if os.fork() == 0:
            if os.fork() == 0:
                pipe = selectable.Pipe()
                run = runner.Runner(
                    pipe,
                    self.def_path,
                    self.exp_id,
                    self.hyperparams)
                run.start()
                pipe.use_left()
                client = unix_rpc.Client(self.socket_path)
                client.running(self.exp_id)
                read_from = [pipe, client]
                while read_from != []:
                    (readable, _, _) = select.select(read_from, [], [])
                    for obj in readable:
                        msg = obj.read()
                        if msg is None:
                            read_from.remove(obj)
