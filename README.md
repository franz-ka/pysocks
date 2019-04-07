# pysocks
Servidor tcp en python usando socket api low-level, multithreading, nonblocking io y VLC player

El protocolo para enviarle audio al servidor es: [bytes llave de acceso]["data"][bytes sonido a reproducir....

uso: 'python3 main.py'
para prender el servidor escuchando en localhost:65432

uso: 'python3 sockcli.py'
para prender el cliente

! ! ! El cliente sockcli.py esta en constante modificacion, no lo reviso antes de subirlo, es con el que se testea el servidor ! ! !

Si se desea testear remotamente hay que modificar la variable HOST en sockcli.py poniendo la ip publica del servidor (myip.com), y en el servidor se debe abrir el puerto tcp 65432 en el router (port forwarding) y se debe modificar la variable HOST en threadser.py con su ip lan (p.ej. 192.168.1.55). 

En este momento el cliente busca una cancion song.mp3 (que no esta en el repositorio) en su mismo directorio y se la envia al servidor. Este recibe song.mp3 y la reproduce con vlc (usando el comando 'vlc -' en otro thread)

Si hay desconexiones, solo se envian segmentos de canciones, o se envian segmentos de distintas canciones, todo bien, el servidor siempre reproduce lo que le llegue, cuando le llegue, y vuelve al estado de escuchar conexiones.

Los archivos principales son:
threadser.py - codigo del thread del servidor
threadvlc.py - codigo del thread del vlc
main.py - donde se inicializan los otros dos threads
keyser - archivo que tienen que tener tanto el servidor como el cliente para validarse
