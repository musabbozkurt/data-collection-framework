import socket

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host= '10.107.52.44'
port=5555
socksize=1024

s.bind((host,port))

while True:
    print("Now listening...\n")
    s.listen(5)
    conn, addr = s.accept()

    print ('New connection from %s:%d' % (addr[0], addr[1]))
    data = conn.recv(socksize)
    data=data.decode("utf-8")
    if not data:
        break
    elif data=="killserver":
        print("server is closed")
        conn.close()
        break
    elif data=="Terminate":
        sendTelemetry="Client read() function works"
        # Respond to the client with current telemetry and status
        #s.sendall(chr(len(sendTelemetry)))
        conn.sendall(sendTelemetry.encode())
        print("server works: data="+str(data))
    else:
        print("Process is not defined!!!")