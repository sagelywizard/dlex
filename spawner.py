import select
import multiprocessing
import os

import unix_rpc
import db
import runner
import selectable

class Spawner(multiprocessing.Process):
    """A process to fork the model runner daemon.

    This wrapper is necessary so as to not cause the os.fork to copy the CLI.
    """
    def __init__(self, db_path, socket_path, exp_id):
        self.db_path = db_path
        self.socket_path = socket_path
        self.exp_id = exp_id
        super(Spawner, self).__init__()

    def run(self):
        if os.fork() == 0:
            if os.fork() == 0:
                client = unix_rpc.Client(self.socket_path)
                client.running(self.exp_id, os.getpid())
                ddb = db.DLEXDB(self.db_path)
                assert ddb.set_pid(self.exp_id, os.getpid())
                exp = ddb.get_experiment(self.exp_id)
                pipe = selectable.Pipe()
                run = runner.Runner(
                    pipe,
                    exp['def_path'],
                    self.exp_id,
                    exp['hyperparams'])
                run.start()
                pipe.use_left()
                read_from = [pipe, client]
                while read_from != []:
                    (readable, _, _) = select.select(read_from, [], [])
                    if pipe in readable:
                        msg = pipe.read()
                        if msg is None and not pipe.read_pipe.is_open():
                            read_from.remove(pipe)
                        elif msg[0] == 'loss':
                            client.set_loss(self.exp_id, msg[1])
                        elif msg == ['status', 'done']:
                            response = client.done(self.exp_id, os.getpid())
                            if response == 'terminate':
                                client.close()
                                read_from.remove(client)
                        elif msg[0] == 'epoch':
                            client.set_epoch(self.exp_id, msg[1])
                    else:
                        msg = client.read()
                        if msg == 'terminate':
                            response = client.close()
                            if response == 'terminate':
                                read_from.remove(client)
                run.join()
