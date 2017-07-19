class Experiment(object):
    def __init__(self, model, optimizer, dataset, epochs=1):
        self.model = model
        self.optimizer = optimizer
        self.dataset = dataset
        self.epochs = epochs
        self.loss = 0
        self.current_epoch = 0

    def get_epoch(self):
        return self.current_epoch

    def train(self):
        raise NotImplementedError

    def validate(self):
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

class Dataset(object):
    def __init__(self, dataset_file):
        self.file = dataset_file

    def next(self, batch_size=1):
        acc = []
        for _ in range(batch_size):
            next_line = self.file.readline()
            if next_line == '':
                if acc == []:
                    return None
                return acc
            acc.append(next_line)
        return acc
