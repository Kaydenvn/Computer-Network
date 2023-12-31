import socket
import threading
import os
import json
# myport and host
# server port and host
format = 'utf8'
myPort=None
myHost=None
fetchfileid=None
fetchfileport=None
json_file_name = "repository.json"
# print('client')
# sendList
def find_free_port(host,start_port, end_port):
    host='127.0.0.1'
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
            return port
        except socket.error as e:
            continue
    return None

def getIPAddress():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return str(ip_address)

def send_file_to_client(fileName, conn):
  with open("repository.json", "r") as json_file: 
    filedata = json.load(json_file) 
  for data in filedata:
    if data["SharedFileName"] == fileName:
      fileName=data["LocalFileName"]
      break
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
      
def fetchFile(filename: str, client):
  client_data=getAvailable(filename,client)
  fetchIp=client_data[0]['ip']
  fetchPort=client_data[0]['port']
  clientFetch = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  clientFetch.connect((fetchIp,int(fetchPort)))
  msg = 'DOWNLOAD '+filename
  clientFetch.sendall(msg.encode(format))
  try:
        # Nhận kích thước của file từ server
        file_size_bytes = clientFetch.recv(4)
        file_size = int.from_bytes(file_size_bytes, byteorder='big')
        # Nhận nội dung của file từ server
        file_content = b''
        while len(file_content) < file_size:
            chunk = clientFetch.recv(1024)
            if not chunk:
                break
            file_content += chunk
        # Lấy đường dẫn của thư mục chứa file Python hiện tại
        current_directory = os.getcwd()
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
        publishFile(filename,filename)
  except Exception as e:
        print(f"Lỗi khi nhận và lưu file: {str(e)}")
def handleClient(conn, addr):
    print('client address: ', addr)
    # print('conection: ', conn.getsockname())
    msg=None
    while(msg!='x'):
      try:
        msg = conn.recv(1024).decode(format)
        if (msg == "discover"):
          with open(json_file_name, "r") as json_file:
              filedata = json.load(json_file)  
          file_data_str = json.dumps(filedata, indent=2)
          conn.sendall(file_data_str.encode(format)) 
        elif 'download' in msg.lower():
          temp = msg.split()[1]
          send_file_to_client(temp,conn)
      except Exception as e:
        print(f"Đã xảy ra lỗi: {type(e).__name__} - {str(e)}")
    print('client addrees', addr, 'finish')
    print(conn.getsockname(),'closed')
    conn.close()
# tạo p2p server
def createP2PServer():
  myHost='127.0.0.1'
  P2Pserver=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  P2Pserver.bind((myHost,myPort))
  P2Pserver.listen(5)
  while(True):
    try:
      conection,addr=P2Pserver.accept()
      thread = threading.Thread(target=handleClient, args=(conection,addr))
      thread.daemon = False
      thread.start()
    except Exception as e:
      print(f"Đã xảy ra lỗi: {type(e).__name__} - {str(e)}")
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
  msg = 'GETFILEHOLDER '+filename
  client.sendall(msg.encode(format))
  received_data = client.recv(1024).decode(format)
  received_array = json.loads(received_data)
  if received_data:
    received_array = json.loads(received_data)
    print('file holder', received_array)
    return received_array
  else: 
    print(f'không tồn tại file {filename} trong hệ thống')
    return None

def clientSignup(client):
    client.sendall("signup".encode(format))
    account = []
    username = input('username:')
    password = input('password:')

    # Check username and password validation
    account.append(username)
    account.append(password)
    
    # Send account to server
    sendList(client, account)

    # Receive response from server
    validCheck = client.recv(1024).decode(format)
    print(validCheck)  

def clientLogin(client):
    client.sendall("login".encode(format))
    client.recv(1024)
    account = []
    username = input('username:')
    password = input('password:')

    # Check username and password validation
    account.append(username)
    account.append(password)
    
    # Send account to server
    sendList(client, account)

    # Receive response from server
    validCheck = client.recv(1024).decode(format)
    if validCheck=="Log in successfully":
        client.sendall(str(myPort).encode(format))
    print(validCheck)

def publishFile(lname,fname):
  new_item = {
    "LocalFileName": lname,
    "SharedFileName": fname
  }
  if os.path.exists('repository.json'):
    with open('repository.json', 'r') as file:
      data = json.load(file)
      data.append(new_item)
    with open('repository.json', 'w') as file:
      json.dump(data, file, indent=2)
  else:
    with open('repository.json', 'w') as file:
        json.dump(new_item, file)

def removeFile(lname,fname):
  with open('repository.json', 'r') as file:
    data = json.load(file)
    file_to_remove = {
      "LocalFileName": lname,
      "SharedFileName": fname
    }
    data = [item for item in data if (item["LocalFileName"] != file_to_remove["LocalFileName"]) or (item["SharedFileName"] != file_to_remove["SharedFileName"])]
    with open('repository.json', 'w') as file:
      json.dump(data, file, indent=2)
def clientLogout(client):
    client.sendall("logout".encode(format))
    msg = client.recv(1024).decode(format)
    print(msg)
# main
def main():
  host = '127.0.0.1'
  server_port = 65315
  client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  try:
    client.connect((host,server_port))
    msg = None
    while True:
      msg = input("Command: ")
      temp = msg.split()
      if(msg=="exit"):
        client.close()
      elif msg == "login": 
        clientLogin(client)
      elif msg == "signup":
        clientSignup(client)
      elif msg == "logout":
        clientLogout(client)
      elif len(temp)==2:
        if 'getavailable' in msg.lower():
          getAvailable(temp[1],client)
        if 'fetch' in msg.lower():
          threadfetch = threading.Thread(target=fetchFile, args=(temp[1],client))
          threadfetch.daemon=False
          threadfetch.start()
      elif len(temp)==3:
        if 'publish' in msg.lower():
          client.sendall(msg.encode(format))
          publishFile(temp[1],temp[2])
        if 'remove' in msg.lower():
          client.sendall(msg.encode(format))
          removeFile(temp[1],temp[2])
  except Exception as e:
    print('error: ', e)
    client.close()
  
if __name__ == "__main__":
  myHost = getIPAddress()
  myPort = find_free_port(myHost,22222,33333)
  p2pThread = threading.Thread(target=createP2PServer)
  p2pThread.daemon = False
  p2pThread.start()
  main()
  # createServer()