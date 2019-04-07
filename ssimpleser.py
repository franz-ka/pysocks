#!/usr/bin/env python3
import socket
import select


from queue import Queue
from threading import Thread
import subprocess
_queue = Queue()
_eof_q = object()

def _thread_rfile():
	print('socket');
	HOST = '127.0.0.1'
	PORT = 65432
	S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#para evitar "OSError: [Errno 98] Address already in use"
	S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	S.setblocking(0)
	S.bind((HOST, PORT))
	S.listen()
	print("Sirviendo en {}:{}".format(HOST, PORT))
	conns = [S]
	desco=False
	while not desco:
		print('selectA')
		sr,sw,se=select.select(conns, [], [])	
		print('selectB')
		for s in sr:
			if s is S:
				conn, addr = s.accept()
				conn.setblocking(0)
				print('Conexion de {}:{}'.format(addr[0],addr[1]))
			else:
				D = s.recv()
				print('recv')
				if len(D) > 0:
					_queue.put(D)	
				else:
					desco = True
					break
	_queue.put(_eof_q)
	print('socket done');

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
t2 = Thread(target=_thread_wproc)
t2.daemon = True
t2.start()
print('t2 ok');
t1.start()
print('t1 ok');
t1.join()
