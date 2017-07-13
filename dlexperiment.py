class Experiment(object):
    def __init__(self, model, optimizer, train_data, test_data, epochs=1):
        self.model = model
        self.optimizer = optimizer
        self.train_data = train_data
        self.test_data = test_data
        self.epochs = epochs
        self.loss = 0
        self.current_epoch = 0

    def get_epoch(self):
        return self.current_epoch

    def train(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError

    def set_loss(self, loss):
        self.loss = loss

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
