#!/usr/bin/env python3

from queue import Queue
from threading import Thread

### VLC THREAD
#share
_eof_q = object()
_vlcqueue = Queue()
_vlcproc = []
from threadvlc import _thread_vlc_wr
vlcthread = Thread( target=_thread_vlc_wr , args=[_vlcproc,_eof_q,_vlcqueue] )
vlcthread.daemon = True

### SERVER THREAD
#share
_S = []
from threadser import _thread_server
Sthread = Thread( target=_thread_server , args=[_S,_eof_q,_vlcqueue] )
Sthread.daemon = True

## CTRL+C
import signal
import sys
def signal_handler(sig, frame):
    print('\n')
    if _vlcproc:
        print('Cerrando vlc')
        _vlcproc[0].kill()
    if _S:
        print('Cerrando servidor')
        _S[0].close()
    print('Chau')
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

print('Vlc thread start');
vlcthread.start()
print('Server thread start');
Sthread.start()

#lock mainThread till Sthread terminates
#?deadlock?
Sthread.join(timeout=None)
print('Chau')
