import socket
import threading
import os
# myport and host
# server port and host
format = 'utf8'
# print('client')
# sendList
def send_file_to_client(fileName, conn):
  current_directory = os.getcwd()
  file_path = os.path.join(current_directory, fileName)
  try:
  # Mở file để đọc nội dung
    with open(file_path, 'rb') as file:
       # Đọc nội dung file
      file_content = file.read()
      # Gửi kích thước của file đến client
      file_size = len(file_content)
      conn.sendall(file_size.to_bytes(4, byteorder='big'))
      # Gửi nội dung của file đến client
      conn.sendall(file_content)
      print(f"Đã gửi file {file_path} thành công.")
  except FileNotFoundError:
      print(f"File {file_path} không tồn tại.")
  except Exception as e:
      print(f"Lỗi khi gửi file: {str(e)}")
def handleClient(conn, addr):
    print('client address: ', addr)
    # print('conection: ', conn.getsockname())
    try:
      msg=None
      while(True):
        msg = conn.recv(1024).decode(format)
        if(msg=='x'):
          conn.close()
        command,data = msg.split(' ')
        if (command =='DOWNLOAD'):
          send_file_to_client(data,conn)
      print('client addrees', addr, 'finish')
      print(conn.getsockname(),'closed')
      conn.close()
    except Exception as e:
      print('error',e)
      conn.close()
# tạo p2p server
def createP2PServer():
  myHost = '192.168.1.3'
  myPort = 65315
  P2Pserver=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  P2Pserver.bind((myHost,myPort))
  P2Pserver.listen(2)
  print('server listening')
  while(True):
    try:
      conection,addr=P2Pserver.accept()
      thread = threading.Thread(target=handleClient, args=(conection,addr))
      thread.daemon = False
      thread.start()
    except:
      print('error')
      conection.close()
def sendList(client,list):
  for item in list:
    client.sendall(item.encode(format))
    client.recv(1024)
  msg = 'end'
  client.send(msg.encode(format))
def recvList(conn):
  list = []
  item = conn.recv(1024).decode(format)
  while(item!='end'):
    list.append(item)
    conn.sendall(item.encode(format))
    item = conn.recv(1024).decode(format)
  return list
# getvalilable
def getAvailable(filename,client):
  msg = 'GETFILEHODER '+filename
  client.sendall(msg.encode(format))
  fileHoder = recvList(client)
  if fileHoder:
    print('file holder', fileHoder)
  else: 
    print(f'không tồn tại file {filename} trong hệ thống')
# main
def main():
  host = '127.0.0.1'
  server_port = 65432
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    client.connect((host,server_port))
    while(True):
      msg=input('fileName request: ')
      if(msg=='x'):
        break
      if(msg =='geta'):
       getAvailable('a',client)
      if(msg =='getb'):
       getAvailable('b',client)
      if(msg =='getc'):
        getAvailable('c',client)
    client.close()
  except Exception as e:
    print('error: ', e)
    client.close()
  
if __name__ == "__main__":
  serverThread = threading.Thread(target=main)
  p2pThread = threading.Thread(target=createP2PServer)
  serverThread.daemon = False
  p2pThread.daemon = False
  serverThread.start()
  p2pThread.start()
  # createServer()



