"""This module provides a class to run experiments
"""
import multiprocessing
import importlib.util
import inspect
import select

from dlexperiment import Experiment

class Runner(multiprocessing.Process):
    """A process for running an experiment.

    This process runs an experiment. It also handles communication with dlexd
    and the experiment, via a UNIX domain socket and UNIX pipe respectively.
    """
    def __init__(self, pipe, path, exp_id, hyperparams):
        self.pipe = pipe
        self.path = path
        self.exp_id = exp_id
        self.hyperparams = hyperparams
        super(Runner, self).__init__()

    def run(self):
        self.pipe.use_right()
        self.pipe.write(['status', 'loading module'])
        name = self.path.split('/')[-1].split('.')[0]
        spec = importlib.util.spec_from_file_location(name, self.path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        exp_class = None
        for item in dir(mod):
            if (inspect.isclass(getattr(mod, item))
                    and Experiment in getattr(mod, item).__bases__):
                exp_class = getattr(mod, item)
                break

        if exp_class is not None:
            self.pipe.write(['status', 'initializing experiment'])
            experiment = exp_class()
            self.pipe.write(['epochs', experiment.get_epochs()])
            self.pipe.write(['status', 'experiment running'])
            while not experiment.is_done():
                experiment.train()
                (readable, _, _) = select.select([self.pipe], [], [], 0)
                if readable != []:
                    msg = self.pipe.read()
                    print('model got a message: %s' % msg)
            self.pipe.write(['status', 'done'])
        else:
            self.pipe.write(['status', 'failed'])
