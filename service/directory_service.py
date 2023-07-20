# directory service
import os
import csv      
from socket import *

def check_mappings(client_msg, list_files):

	filename = client_msg.split('|')[0]
	RW = client_msg.split('|')[1]
  
  with open("file_mappings.csv",'rt') as infile:        
		docu_reader = csv.DictReader(infile, delimiter=',')    
		header = docu_reader.fieldnames    	
		for row in docu_reader:
      print("WRITING")
      print("READING")

def main():
  connection_socket, addr = serverSocket.accept()

	response = ""
	recv_msg = connection_socket.recv(1024)
	recv_msg = recv_msg.decode()

	connection_socket.send(response.encode())
	connection_socket.close()

if __name__ == "__main__":
	main()
