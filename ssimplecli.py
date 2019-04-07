import socket
import sys
import time


HOST, PORT = "localhost", 65432
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
f = open('song.mp3', "rb")
b = [1];
while len(b)>0:
	b = f.read(1024);
	print('1')
	sock.send(b)
f.close()

sys.exit(0)




from queue import Queue
from threading import Thread
import subprocess
_queue = Queue()
_eof_q = object()

def _thread_rfile():
	print('archi');
	f = open('song.mp3', "rb")
	b = [1];
	while len(b)>0:
		b = f.read(1024);
		_queue.put(b)	
	_queue.put(_eof_q)	
	f.close()
	print('archi done');

def _thread_wproc():
	print('vlc');
	p = subprocess.Popen(["vlc",'-'], stdin=subprocess.PIPE)
	while True:
		b = _queue.get()
		if b is _eof_q:
			_queue.task_done()
			break
		p.stdin.write(b)
	print('vlc done');


t1 = Thread(target=_thread_rfile)
t1.daemon = True
t1.start()
print('t1 ok');
t2 = Thread(target=_thread_wproc)
t2.daemon = True
t2.start()
print('t2 ok');
t2.join()
print('t2 fin');
