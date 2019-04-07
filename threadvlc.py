#################################
#################################
############ VLC THREAD
#################################
# https://medium.com/tictail/python-streaming-request-data-files-streaming-to-a-subprocess-504769c7065f
def _thread_vlc_wr(_vlcproc,_eof_q,_vlcqueue):
    from queue import Empty
    import subprocess
    import time
    from fcntl import fcntl, F_GETFL, F_SETFL
    from os import read, O_NONBLOCK
    from byteshuman import b2hum

    print('Vlc thread esperando primer msg')
    b = _vlcqueue.get()

    print('Vlc abriendo')
    p = subprocess.Popen(["vlc", '-'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    _vlcproc.append(p)
    print('Vlc abierto')
    wtot=0;
    wsess=0;
    currflags = fcntl(p.stderr, F_GETFL) # get current p.stderr flags
    fcntl(p.stderr, F_SETFL, currflags | O_NONBLOCK)

    #primer msg
    p.stdin.write(b)
    wtot+=len(b)
    wsess+=len(b);
    while True:
        sleep=True

        #nonblock check queue
        try:
            b = _vlcqueue.get(False)#nonblock
            if b is _eof_q:
                _vlcqueue.task_done()
                print('Vlc data total='+b2hum(wsess));
                wsess=0
            else:
                p.stdin.write(b)
                #print('VLC_GO', str(len(b)) + "B")
                wtot+=len(b)
                wsess+=len(b)
                #no sleep when streming
                sleep=False
        except Empty:
            # no new msg
            pass

        #nonblock check stderr
        try:
            msg=read(p.stderr.fileno(), 1024);
            if msg:
                #strip errcodes
                msg = msg[len('[0000556f8368d630] '):]
                #ignore these always two intial errors
                if msg==b"main libvlc: Running vlc with the default interface. Use 'cvlc' to use vlc without interface.\n" \
                    or msg==b"prefetch stream error: unimplemented query (264) in control\n" :
                    pass
                # ignore last err before exit
                elif msg==b"Timers cannot be stopped from another thread\n":
                    pass
                # lag
                elif msg[:85]==b'main input error: ES_OUT_SET_(GROUP_)PCR  is called too late (pts_delay increased to ':
                    #sacamos los numeros
                    lag=''.join([ c if c.isnumeric() else '' for c in msg[85:].decode("utf-8", "strict") ])
                    print('Vlc lag[p] '+lag+'ms');
                elif msg[:72]==b'main input error: ES_OUT_SET_(GROUP_)PCR  is called too late (jitter of ':
                    lag=''.join([ c if c.isnumeric() else '' for c in msg[72:].decode("utf-8", "strict") ])
                    print('Vlc lag[j] '+lag+'ms');
                else:
                    print('Vlc err:',msg);
        except OSError:
            #no new msg
            pass

        #process end?
        if p.poll() != None:
            print('Vlc proc ended')
            break

        if sleep:
            time.sleep(0.5)

    print('Vlc thread die')
    pass#end thread