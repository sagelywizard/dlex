import socket
import struct
import json
import os

RPC_VERSION = 1

def msg_send(sock, msg):
    j = json.dumps(msg)
    header = struct.pack('!LL', RPC_VERSION, len(j))
    sock.sendall(b'%b%b' % (header, j.encode('utf-8')))

def msg_recv(sock):
    buff = b''
    while len(buff) < 8:
        buff += sock.recv(1024)

    (version, length) = struct.unpack('!LL', buff[0:8])
    assert RPC_VERSION == version

    buff = buff[8:]

    while len(buff) < length:
        buff += sock.recv(1024)

    assert len(buff) == length

    return json.loads(buff.decode('utf-8'))

class UnknownRPCError(Exception):
    pass

class RPCError(Exception):
    pass

class RPC(object):
    def __init__(self, sock, method):
        self.sock = sock
        self.method = method

    def __call__(self, *args, **kwargs):
        msg_send(self.sock, ['rpc', self.method, args, kwargs])
        [msg_type, msg] = msg_recv(self.sock)
        assert msg_type in ['return', 'error']
        if msg_type == 'error':
            if msg == 'UnknownRPCError':
                raise UnknownRPCError
            raise RPCError(msg)

        return msg


class Server(object):
    def __init__(self, path):
        self.path = path
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.path)
        self.socket.listen(1)
        self.funs = {}

    def register(self, name, function):
        self.funs[name] = function

    def start(self):
        try:
            while True:
                conn, _ = self.socket.accept()
                [msg_type, method, args, kwargs] = msg_recv(conn)
                assert msg_type == 'rpc'
                if method not in self.funs:
                    msg_send(conn, ['error', 'UnknownRPCError'])
                else:
                    try:
                        ret = self.funs[method](*args, **kwargs)
                        msg_send(conn, ['return', ret])
                    except Exception as e:
                        try:
                            msg_send(conn, ['error', str(e)])
                        except:
                            pass
        finally:
            try:
                if os.path.exists(self.path):
                    os.remove(self.path)
            except: # pylint: disable=bare-except
                pass

class Client(object):
    def __init__(self, path):
        self.__path = path
        self.__socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.__socket.connect(self.__path)

    def __getattr__(self, method):
        return RPC(self.__socket, method)

    def fileno(self):
        return self.__socket.fileno()

    def read(self):
        return self.__socket.recv(1024)

    def close(self):
        self.__socket.close()
