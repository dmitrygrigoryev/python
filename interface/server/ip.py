import socket
print socket.gethostbyname_ex(socket.gethostname())[2][0]

def check_node_online(node_ip,node_port):
    worker_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_port.connect ((node_ip, node_port))
    worker_port.send('ping')
    response = worker_port.recv(1024)
    print response
    if response:
        print 'online'
        return 1       
    else:
        print 'offline'
        return 0
    worker_port.close()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('10.50.70.173', 2727))
# server_socket.listen(5)
check_node_online('10.50.70.173',2728)
# server_socket.close()