# chat_server.py
 
import sys
import socket
import select
import pdb

HOST = '' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009

OPTIONS="The Commands list are : \n1.login\n2.list\n3.sendto\n4.help\n5.exit\n"

def chat_server():
    open("users.txt", 'w').close()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                print "Client (%s, %s) connected" % addr
                #broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        print data
                        process_command(server_socket,data,sock)
                        #broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 
                        process_command(server_socket,"removeuser",sock)

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    process_command(server_socket,"removeuser",sock)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    #pdb.set_trace()
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

def unicast_reply(sock,message):
    try :
        sock.send(message)
    except :
        # broken socket connection
        sock.close()
        # broken socket, remove it

def get_socket_by_name(name):
    sock_str = ""
    f = open("users.txt","r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if name == line.split("::")[0]:
             sock_str = line.split("::")[1].strip("\n")
    for sock in SOCKET_LIST:
        if sock_str.strip('\n') == str(sock):
            return sock

def process_command(server_sock,data,sock):
    #pdb.set_trace()
    if "login" in data:
        register_user(data,sock)
    if "removeuser" in data:
        deregister_user(data,sock)
    if "list" in data:
        users = list_users(data)
        unicast_reply(sock,users)
    if "sendto" in data:
        send_message(data,sock)
    if "help" in data:
        unicast_reply(sock,OPTIONS)

def send_message(data,sender_sock):
    data = data.split(" ")
    if len(data)==3:
        reciver_sock = get_socket_by_name(data[1])
        unicast_reply(reciver_sock,data[2] )
    else:
        unicast_reply(sender_sock,"error in send to command please refer to help")

def register_user(data,sock):
    with open("users.txt", "a") as myfile:
            myfile.write(data.split(" ")[1].strip("\n")+"::"+str(sock)+"\n")

def deregister_user(data,sock):
    f = open("users.txt","r")
    lines = f.readlines()
    f.close()
    f = open("users.txt","w")
    for line in lines:
        if not (str(sock) in line):
            f.write(line)
    f.close()

def list_users(data):
    f = open("users.txt","r")
    users = f.read()
    return users
  
if __name__ == "__main__":

    sys.exit(chat_server())
