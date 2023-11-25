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
def fetchFile(filename,client):
  msg = 'DOWNLOAD '+filename
  client.sendall(msg.encode(format))
  try:
        # Nhận kích thước của file từ server
        file_size_bytes = client.recv(4)
        print('filesizeByte: ',file_size_bytes)
        file_size = int.from_bytes(file_size_bytes, byteorder='big')
        print('fileSize: ', file_size)
        # Nhận nội dung của file từ server
        file_content = b''
        while len(file_content) < file_size:
            chunk = client.recv(1024)
            if not chunk:
                break
            file_content += chunk
        # Lấy đường dẫn của thư mục chứa file Python hiện tại
        current_directory = os.getcwd()
        print('1')
        # Tạo một file mới trong thư mục của file Python và lưu nội dung vào file
        file_path = os.path.join(current_directory, filename)
        counter = 1
        while os.path.exists(file_path):
            # Nếu file đã tồn tại, thêm số vào tên file
            filename = f"{counter}_{filename}"
            file_path = os.path.join(current_directory, filename)
            counter += 1
        with open(file_path, 'wb') as new_file:
            new_file.write(file_content)

        print(f"Đã nhận và lưu file {filename} thành công.")
  except Exception as e:
        print(f"Lỗi khi nhận và lưu file: {str(e)}")
def handleClient(conn, addr):
    print('client address: ', addr)
    # print('conection: ', conn.getsockname())
    msg=None
    while(msg!='x'):
      msg = conn.recv(1024).decode(format)
      command,data = msg.split(' ')
      if (command =='DOWNLOAD'):
        send_file_to_client(data,conn)
    print('client addrees', addr, 'finish')
    print(conn.getsockname(),'closed')
    conn.close()
# tạo p2p server
def createP2PServer():
  myHost = '192.168.1.3'
  myPort = 65314
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
  host = '192.168.1.3'
  server_port = 65315
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    client.connect((host,server_port))
    while(True):
      msg=input('fileName request: ')
      if(msg=='x'):
        client.close()
      # if(msg =='geta'):
      #  getAvailable('a',client)
      # if(msg =='getb'):
      #  getAvailable('b',client)
      # if(msg =='getc'):
      #   getAvailable('c',client)
      if(msg=='download tho.txt'):
        fetchFile('tho.txt',client)
      if(msg=='download tho.docx'):
        fetchFile('tho.docx',client)
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



