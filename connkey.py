def loadkey(KEY_F, KEY_SIZE,RBUFF_LEN):
    key = bytearray()
    f = open(KEY_F, "rb")
    try:
        key = f.read(KEY_SIZE)
    finally:
        f.close()
    if len(key) != KEY_SIZE:
        print('Llave muy corta {}B, requerido {}B'.format(len(key), KEY_SIZE))
        sys.exit(0)
    if RBUFF_LEN < KEY_SIZE:
        print('Buffer menor a llave no permitido')
        sys.exit(0)
    print('Clave cargada {}'.format(bytes(key)))
    return key