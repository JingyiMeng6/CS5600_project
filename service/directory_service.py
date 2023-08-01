# directory service
import os
# work with csv file
import csv      
from socket import *

serverPort = 9090
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(10)
print ('DIRECTORY SERVICE is ready to receive...')

def check_mappings(client_msg, list_files):

	filename = client_msg.split('|')[0]
	RW = client_msg.split('|')[1]

	# open the .csv file storing the mappings
	with open("file_mappings.csv",'rt') as infile:        
		# read file as a csv file, taking values after commas
		d_reader = csv.DictReader(infile, delimiter=',')    
		# skip header of csv file
		header = d_reader.fieldnames    	
		file_row = ""
		for row in d_reader:
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

			else:
				user_filename = row['user_filename']
				# append filename to return string
				file_row = file_row + user_filename +  "\n"		
		if list_files == True:
			return file_row		
	# if file does not exist return None
	return None 	

def main():

	while 1:
		connectionSocket, addr = serverSocket.accept()

		response = ""
		recv_msg = connectionSocket.recv(1024)
		recv_msg = recv_msg.decode()

		if "LIST" not in recv_msg:
			# check the mappings for the file
			response = check_mappings(recv_msg, False)		
		elif "LIST" in recv_msg:
			response = check_mappings(recv_msg, True)

		if response is not None:	# for existance of file
			response = str(response)
			print("RESPONSE: \n" + response)
			print("\n")
		else:
			response = "FILE_DOES_NOT_EXIST"
			print("RESPONSE: \n" + response)
			print("\n")

		# send the file information or non-existance message to the client
		connectionSocket.send(response.encode())	
			
		connectionSocket.close()


if __name__ == "__main__":
	main()
