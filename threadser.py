#################################
#################################
############ SERVER THREAD
#################################
def _thread_server(_S,_eof_q,_vlcqueue):
    ### CONFIGURACIONES
    #HOST = '192.168.0.92'
    HOST = '127.0.0.1'
    # (non-privileged ports are > 1023)
    PORT = 65432
    CLOCK_SECS = 0.5
    # For best match with hardware and network realities, the value of
    # bufsize should be a relatively small power of 2, for example, 4096.
    RBUFF_LEN = 1024 * 512  # KB
    CONNRX_MAX = 1024 * 1024 * 10  # MB
    # MAX_CONNS=5
    CONN_TOUT = 9
    CMD_MAXL = 10
    KEY_F = "keyser"
    KEY_SIZE = 20
    #EOF_CHAR = b'\x00'  # bytes("\n", "utf-8")#'\n'#str.encode('\n')
    EOF_SEQ=b'\x00'*5+b'\x03'*5+b'\x08'*5
    EOF_SEQLEN=len(EOF_SEQ)

    def sockprint(*arg):
        return print(ptt()+arg[0])

    from byteshuman import b2hum

    ### CARGAMOS CLAVE SECRETA COMPARTIDA
    from connkey import loadkey
    key = loadkey(KEY_F,KEY_SIZE,RBUFF_LEN)

    ### CLASE CONN DATA
    from conndata import ConnData
    #indice por filedescriptor de conexiones
    conndata = {}

    ### CARGAMOS COMANDOS
    print("Cargando comandos")
    cmds = ['data', 'cerrar', 'cagar']
    cmdbys = []
    cmdcb = {}
    def cb(c, conn):
        if c == 'data':
            conndata[conn].recvdata = True
            conndata[conn].acceptcmd = False

    for c in cmds:
        if len(c) > CMD_MAXL:
            print('Comando largo no permitido')
            sys.exit(0)
        else:
            cmdbys.append(bytes(c, "utf-8"))
            cmdcb[c] = cb

    ##################################
    ################### SOCKET
    import datetime
    def ptt():
        #21:22:04.712950
        return str(datetime.datetime.now().time())[:8] + " "
    import socket
    import select
    S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _S.append(S)
    # para evitar "OSError: [Errno 98] Address already in use"
    S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #S.setblocking(0)
    sockprint("Creando servidor tcp en {}:{}".format(HOST, PORT))
    S.bind((HOST, PORT))
    S.listen()
    sockprint("Sirviendo en {}:{}".format(HOST, PORT))
    conns = [S]
    connwr = [S]
    def closeConn(pconn, msg):
        if _vlcqueue.qsize() > 0:
            _vlcqueue.put(_eof_q)
        sockprint( 'Fin {} (T={}), {}'.format(
            conndata[pconn].a,
            b2hum(conndata[pconn].rx),
            msg))
        pconn.close()
        del conndata[pconn]
        conns.remove(pconn)

    ###############
    ##### DIRECT TEXST
    ###############
    '''S.setblocking(1)
    conn, addr = S.accept()
    print(ptt()+'Conexion de {}:{}'.format(addr[0], addr[1]))
    conns.append(conn)
    conndata[conn] = ConnData(addr)
    RBUFF_LEN = 1024 * 50  # KB
    while True:
        D = conn.recv(RBUFF_LEN)
        print(ptt()+'rcv', len(D))
        if D:
            _vlcqueue.put(D)
        else:
            closeConn(conn, 'bad')
            break
    print('end direct test')
    vlcthread.join(timeout=None)
    sys.exit(0)'''
    #############

    def connDataIn(conn, D):
        if not D:
            closeConn(conn, 'cerrado por cliente')
            return False
        C = conndata[conn];
        if C.rx + len(D) > CONNRX_MAX:
            closeConn(conn, 'data maxima excedida')
            return False
        C.rx += len(D)

        #### TIENE KEY?
        if not C.k:
            if len(D) >= KEY_SIZE and D[:KEY_SIZE] == key:
                C.k = True
                sockprint( 'Clave ok de {} ({})'.format(C.a, b2hum(KEY_SIZE)) )
                D = D[KEY_SIZE:]
                C.lt = datetime.datetime.now()
                if not D:
                    return True
            else:
                closeConn(conn, 'clave incorrecta')
                return False

        #### MODO CMD?
        if C.acceptcmd:
            for c in cmdbys:
                if len(D) >= len(c) and D[:len(c)] == c:
                    sockprint( 'Comando <{}> recibido'.format(c.decode("utf-8", "strict")) )
                    cmdcb[c.decode("utf-8", "strict")](c.decode("utf-8", "strict"), conn)
                    D = D[len(c):]
                    C.lt = datetime.datetime.now()
                    break
            # talvez entro justo la key 0 justo key+cmd
            if not D:
                return True

        #### DATA!
        if C.recvdata:
            C.lt = datetime.datetime.now()
            dlen = len(D);

            #viene solo EOF_SEQ?
            if dlen <= EOF_SEQLEN:
                if D == EOF_SEQ[-dlen:]:
                    C.eof=True
                    cortadostr='' if dlen==EOF_SEQLEN else 'cortado ('+str(dlen)+') '
                    sockprint('Data EOF{} de {}'.format(cortadostr, C.a))
                    closeConn(conn, 'ok')
                    return True
                else:
                    closeConn(conn, 'no termino con EOF')
                    return True

            #viene data + EOF_SEQ?
            if D[-EOF_SEQLEN:] == EOF_SEQ:
                C.eof=True
                #no mandar EOF_SEQ a vlc
                D = D[:-len(EOF_SEQ)]

            _vlcqueue.put(D)
            C.dx += len(D)
            sockprint('Data {} de {} (T={})'.format(
                b2hum(len(D)),
                C.a,
                b2hum(C.dx)
                # D[:(20 if len(D) > 20 else len(D))].decode("utf-8", "strict")
            ))

            if C.eof:
                sockprint('Data EOF de {}'.format(C.a))
                closeConn(conn, 'ok')

    #################################
    ############ MAIN LOOP
    while True:
        sr, sw, se = select.select(conns, connwr, [], CLOCK_SECS)
        #for s in se: print('ERR' + '*' * 60, s)
        #for s in sw: print('W', s)
        ## CHECK TOUT
        n = datetime.datetime.now()
        for c in conns[1:]:
            if (n - conndata[c].lt).seconds >= CONN_TOUT:
                closeConn(c, 'timeout')
        ## READ CONN
        for s in sr:
            if s is S:
                ## PRIMER ENCUENTRO
                conn, addr = s.accept()
                sockprint('Conexion de {}:{}'.format(addr[0], addr[1]))
                conn.setblocking(0)
                conns.append(conn)
                conndata[conn] = ConnData(addr)
            else:
                ## NUEVO MENSAJE
                d = s.recv(RBUFF_LEN)
                connDataIn(s, d)
                #conn = s
                #D = conn.recv(RBUFF_LEN)