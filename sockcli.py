import socket
import sys
import time

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
	read = f.read();
	f.close()
	fl = len(read)
	#fl = round(len(read) / 16)

	i=0
	dosend=True
	print('enviando song.mp3')
	while dosend:
		if (i+1)*SENDLEN < fl:
			s=read[i*SENDLEN:(i+1)*SENDLEN]
		else:
			s=read[i*SENDLEN:fl]
			dosend=False
		sock.send(s)
		print('sent',str(len(s))+'B')
		#time.sleep(1.000)
		i+=1
		
	print('sent EOF')
	sock.send(EOF_SEQ)
print('chau')