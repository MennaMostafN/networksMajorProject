from socket import *
import sys
import webbrowser

if len(sys.argv) <= 1:
    print ('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    # sys.exit(2)

port = 5078   
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(('', port))   
tcpSerSock.listen(1) 

try:
    while 1:
        # Start receiving data from the client
        print ('\nReady to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        print ('Received a connection from:', addr)
        message = tcpCliSock.recv(2048)
        print(message)

        if message == b'':  
            print("No connection")  
            sys.exit("0") 
            break
        
        if message != b'': 
            # Extract the filename, hostname, and URL from the given message
            filename = message.split()[1].decode("utf-8").rpartition("/")[2]
            hostn=message.split()[4].decode("utf-8") 
            URL = message.split()[1].decode("utf-8") 

        print("Filename: "+ filename)
        print("Hostname: " + hostn)  
        print("URL is: " + URL)  

        #cache the file
        fileExist = "false"
        filetouse = './cache'+ filename
        print (filetouse)

        #check if file is blocked or not in the list of blocked urls of the server
        getout=1  
        with open('blockBlockBlock.txt') as f: 
            for line in f:   
                if URL in line:
                    print("BLOCKED")
                    getout=0 
                    break   
                else:  
                    getout=1  
        if getout==0:  
            webbrowser.open_new_tab('blocked.html')
            break  

        try:
            # Check wether the file exist in the cache
            f = open(filetouse[1:], "rb")
            outputdata = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send(b"HTTP/1.0 200 OK\r\n")
            tcpCliSock.send(b"Content-Type:text/html\r\n")
            for i in range(0,len(outputdata)):  
                tcpCliSock.send(outputdata[i])  
            f.close()   

        # Error handling for file not found in cache
        except IOError:
            try:
                if fileExist == "false":
                # Create a socket on the proxyserver
                    c = socket(AF_INET, SOCK_STREAM) 
                    # hostn = filename.replace("www.","",1).strip()
                    print(hostn)
                    c.connect((hostn,80)) 
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobjwrite = c.makefile('w',None)  
                    fileobjwrite.write("GET "+message.split()[1].decode("utf-8") + " HTTP/1.0\n\n")  
                    fileobjwrite.close()
                    #read response
                    fileobj = c.makefile('rb',None) 
                    buffer = fileobj.readlines() 
                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socket and the corresponding file in the cache
                    File = open( './cache/'+ filename,"wb+") 
                    # Fill in start.
                    for line in buffer:                                                 
                        File.write(line);                                             
                        tcpCliSock.send(line)   
                    File.close()  
                    c.close()  
                
            except:
                print ("Illegal request")
    else:
        # HTTP response message for file not found
        tcpCliSock.send("HTTP/1.0 404 sendError\r\n")                           
        tcpCliSock.send("Content-Type:text/html\r\n") 
        # Close the client and the server sockets
        tcpCliSock.close()  
        print("socket closed") 
        sys.exit("System done, file not found")  
        
except:
    print('connection blocked') 
    tcpCliSock.close() 
    sys.exit("System done, no message")  

