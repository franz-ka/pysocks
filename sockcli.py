import socket
import sys
import time
from byteshuman import b2hum

#HOST, PORT = "181.228.179.96", 65432
HOST, PORT = "127.0.0.1", 65432
#clave EOF única para saber cuál es el último paquete
EOF_SEQ=b'\x00'*5 + b'\x03'*5 + b'\x08'*5
SENDLEN=1024*50#KB

KEY_F="keyser"
KEY_SIZE=20

key = bytearray()
f = open(KEY_F, "rb")
key=f.read(KEY_SIZE)
f.close()

#data = " ".join(sys.argv[1:])*10
def socksendb(buff,start,n):
	totsent = 0
	while totsent < n:
		sent = sock.send( buff[start+totsent:start+totsent+SENDLEN] , SENDLEN )
		print('sent ' + b2hum(sent))
		totsent += sent
	print('tot sent ' + b2hum(totsent))
	return start+totsent

# Create a socket (SOCK_STREAM means a TCP socket)
print('creando socket tcp')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    # Connect to server and send data
	print('conectando a servidor en {}:{}'.format(HOST,PORT))
	sock.connect((HOST, PORT))
	#key
	print('enviando llave de acceso')
	sock.send(key);
	#data command
	print('enviando comando <data>')
	sock.send(bytes('data', "utf-8"))

	#cargamos entero a memoria
	print('cargando song.mp3')
	f = open('song.mp3', "rb")
	buff = f.read();
	f.close()

	print('enviando song.mp3')
	
	'''#en partes
	SENDONLY = 1024*181#KB
	SLEEP = 6#KB
	totsent = 0
	totsent+=socksendb(buff,0,SENDONLY)
	#time.sleep(SLEEP)
	totsent+=socksendb(buff,totsent,SENDONLY)
	time.sleep(SLEEP)
	totsent+=socksendb(buff,totsent,SENDONLY)

	time.sleep(12)'''
	sent = sock.send( buff )
	print('sent ' + b2hum(sent))
	

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.connect((HOST, PORT))
	sock.send(key);
	sock.send(bytes('data', "utf-8"))
	totsent+=socksendb(buff,totsent,1024*181)
	time.sleep(SLEEP)
	totsent+=socksendb(buff,totsent,1024*181)
	sent = sock.send( buff[totsent:] )
	print('sent ' + b2hum(sent))
	
	
	#entero de una
	#sent = socksendb( buff , 0,  len(buff))

	sock.send(EOF_SEQ)
	print('sent EOF')
print('chau')