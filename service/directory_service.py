# directory service
# a simple file server that can handle client requests and provide file information back to the client

# 1. Imports and Initialization:
import os
import csv      
from socket import *

# The service binds to a socket on the specified IP and port.
# It listens for incoming connections and, upon establishing a connection, receives a request.
serverPort = 9090
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(10)
print ('DIRECTORY SERVICE is ready to receive...')

# 2.check_mappings Function:
# Takes in the client's message (client_msg) and a boolean (list_files) to decide what action to perform.

# When a client connects and requests a file by its user-friendly name,
# the directory service checks the mappings in the CSV
# to determine where the actual file filenames and locations
# and sends this information back to the client.
def check_mappings(client_msg, list_files):

	# case 1: If list_files is False, it splits the client_msg to retrieve the desired filename and the operation (read or write).
	# 	Opens the CSV file file_mappings.csv and reads its contents.
	# case 2: If list_files is True, it creates a set of all user-friendly file names to send back to the client.
	# case 3: If list_files is True, it checks the CSV data for the given file and desired operation
	# 	and sends back string with the actual filename and its location, or a message indicating the file doesn't exist.

	# case 1
	if not list_files:
		filename = client_msg.split('|')[0]
		RW = client_msg.split('|')[1]

	# The open() function is a built-in Python function used to open a .csv file.
	# The first argument "file_mappings.csv" is the name of the file you want to open.
	# The second argument 'rt' specifies the mode in which the file is opened:
	# r: This stands for "read mode", meaning you're opening the file to read its contents.
	# t: This stands for "text mode", meaning you're working with a text file (as opposed to a binary file, for which you would use b).
	with open("file_mappings.csv",'rt') as infile:        
		# read file as a csv file, taking values after commas
		d_reader = csv.DictReader(infile, delimiter=',')    
		# skip header of csv file
		header = d_reader.fieldnames    	
		file_set = set()
		for row in d_reader:
			# case 1
			if list_files == False:
				# use the dictionary reader to read the values of the cells at the current row
				user_filename = row['user_filename']
				primary_copy = row['primary']

				# check if file inputted by the user exists	(eg. file123)
				if user_filename == filename and RW == 'w':		
					print("WRITING")
					# get actual filename (eg. file123.txt)
					actual_filename = row['actual_filename']	
					# get the file's file server IP address
					server_addr = row['server_addr']			
					# get the file's file server PORT number
					server_port = row['server_port']			

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					# return string with the information on the file
					return actual_filename + "|" + server_addr + "|" + server_port	

				elif user_filename == filename and RW == 'r' and primary_copy == 'no':
					print("READING")
					# get actual filename (eg. file123.txt)
					actual_filename = row['actual_filename']	
					# get the file's file server IP address
					server_addr = row['server_addr']			
					# get the file's file server PORT number
					server_port = row['server_port']			

					print("actual_filename: " + actual_filename)
					print("server_addr: " + server_addr)
					print("server_port: " + server_port)

					# return string with the information on the file
					return actual_filename + "|" + server_addr + "|" + server_port	
			# case 2
			else:
				user_filename = row['user_filename']
				# add filename to file set
				file_set.add(user_filename)
		# case 3
		if list_files == True:
			file_row = ""
			for i in file_set:
				file_row = file_row + i + "\n"
			return file_row		
	# if file does not exist return None
	return None 	

# 3. Main Function:
# Continuously listens for incoming connections.
# Once a connection is established, it receives a message from the client and decodes it.
# message contains the string "LIST" or a file request.
# After responding, it closes the connection to that specific client.
def main():

	# This is an infinite loop that keeps the server running and accepting client connections.
	# It will run until the program is terminated.
	while 1:
		# The accept() method is called on the serverSocket to accept an incoming client connection.
		# It blocks until a client connects and returns a new socket object connectionSocket
		# to communicate with the client, and the address addr of the client.
		connectionSocket, addr = serverSocket.accept()
		response = ""
		# The server receives data from the client through connectionSocket.
		# In this case, it expects to receive a message of up to 1024 bytes from the client.
		recv_msg = connectionSocket.recv(1024)
		# The received data is decoded from bytes to a string
		recv_msg = recv_msg.decode()

		# If the received message is a file request, （list_files = False in func send_directory_service）
		# it checks the CSV file for a mapping of the user-friendly filename to the actual file and its location.
		# If the received message contains the string "LIST", （list_files = True in func send_directory_service）
		# it returns a list of all the user-friendly file names available.
		if "LIST" not in recv_msg:
			# check the mappings for the file
			response = check_mappings(recv_msg, False)		
		elif "LIST" in recv_msg:
			response = check_mappings(recv_msg, True)

		# Based on the request,
		# either the actual filename and its location are returned to the client,
		# or a message indicating the file does not exist is sent.
		if response is not None:
			response = str(response)
			print("RESPONSE: \n" + response)
			print("\n")
		else:
			response = "FILE_DOES_NOT_EXIST"
			print("RESPONSE: \n" + response)
			print("\n")

		# The server sends the response back to the client after converting it to bytes.
		# the file information or non-existance message in the response
		connectionSocket.send(response.encode())
		# The server closes the connection with the current client after handling its request.
		connectionSocket.close()


if __name__ == "__main__":
	main()
