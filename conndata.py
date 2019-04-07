import datetime
class ConnData:
    def __init__(self, saddr):
        self.a = '{}:{}'.format(saddr[0], saddr[1])
        self.r = b""
        self.lt = datetime.datetime.now()
        self.k = False
        self.rx = 0
        self.acceptcmd = True
        self.recvdata = False
        self.dx = 0
        self.eof=False