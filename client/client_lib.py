from socket import *
import sys
import os.path

curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))
def create_socket():
    s = socket(AF_INET, SOCK_STREAM)
    return s

def send_directory_service(client_socket, filename, RW, list_files):
    serverName = 'localhost'
    serverPort = 9090   # port of directory service
    client_socket.connect((serverName,serverPort))

    if not list_files:
        msg = filename + '|' + RW
        # send the string requesting file info to directory send_directory_service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
    else:
        msg = "LIST"
        # send the string requesting file info to directory service
        client_socket.send(msg.encode())
        reply = client_socket.recv(1024)
        reply = reply.decode()
        client_socket.close()
        print ("Listing files on directory server...")
        print (reply)

    #print (reply)
    return reply

def instructions():
    # instructions to the user
    print ("------------------- INSTRUCTIONS ----------------------")
    print ("<write> [filename] - write file mode")
    print ("<end> - finish writing")
    print ("<read> [filename] - read file mode")
    print ("<list> - lists all existing files")
    print ("<instructions> - check the instructions again")
    print ("<quit> - exits the application")
    print ("-------------------------------------------------------\n")

def print_breaker():
    print ("--------------------------------")

def check_valid_input(input_string):
    # check for correct format for message split
    if len(input_string.split()) < 2:
        print ("Incorrect format")
        instructions()
        return False
    else:
        return True

def handle_read(filename, file_version_map, client_id):
    client_socket = create_socket()  # create socket to directory service
    reply_DS = send_directory_service(client_socket, filename, 'r', False)  # send file name to directory service
    client_socket.close()   # close directory service connection

    if reply_DS == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        # parse info received from the directory service
        filename_DS = reply_DS.split('|')[0]
        fileserverIP_DS = reply_DS.split('|')[1]
        fileserverPORT_DS = reply_DS.split('|')[2]

        print("File name is: " + filename_DS)
        print("File server IP is: " + fileserverIP_DS)
        print("File server port is: " + fileserverPORT_DS)