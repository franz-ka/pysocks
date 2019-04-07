# pysocks
python tcp socket server client app

uso: python3 main.py
para prender el servidor en localhost:65432

uso: python3 sockcli.py
para prender el cliente

en este momento el cliente busca una cancion song.mp3 (que no esta en el repositorio) y se la envia al servidor
el servidor recibe song.mp3 y se la manda a vlc usando el comando 'vlc -'

el archivo keysec contiene la llave con la que el servidor valida un nueva conexion (cliente)
el cliente es lo primero que manda al iniciar la conexion con el servidor

el servidor despues de validar la conexion espera un nuevo <comando> de la lista de comandos
el cliente envia un <comando>

en este caso el comando <data> hace que el servidor abra vlc y reproduzca song.mp3
el cliente envia el comando <data> y transfiere los bytes de song.mp3
