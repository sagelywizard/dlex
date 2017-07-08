class Experiment(object):
    def __init__(self, epochs=1):
        self.epochs = epochs

    def get_epochs(self):
        return self.epochs

    def train(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError

    def set_loss(self):
        raise NotImplementedError

    def checkpoint(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError

    def is_done(self):
        raise NotImplementedError

class PyTorchExperiment(object):
    def save(self):
        pass
