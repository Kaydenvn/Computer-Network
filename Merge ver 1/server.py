import socket
import threading
import pyodbc
import json
dirver ='ODBC Driver 17 for SQL Server'
sqlServer='MSI\SQLEXPRESS;Database=BTL_MMT'
sqlUsername ='test1'
sqlPassword ='123456'
connections = []
# conect database
conx = pyodbc.connect(f'DRIVER={dirver};SERVER={sqlServer};UID={sqlUsername};PWD={sqlPassword};')
cursor = conx.cursor()
# cursor.execute('select * from OnlineAccount')
# data=cursor.fetchall()
# print(data)
# cursor.execute("insert OnlineAccount values('u','123')")
# conx.commit()
# conx.close()

format='utf8'


def find_free_port(host,start_port, end_port):
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
    return ip_address

def createServer():
  #host=getIPAdress()
  #server_port=find_free_port(host,11111,22222)
  host = '127.0.0.1'
  server_port = 65315
  server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  server.bind((host,server_port))
  server.listen(5)
  print('server listening')
  while(True):
    try:
      conection,addr=server.accept()
      thread = threading.Thread(target=handleClient, args=(conection,addr))
      thread.daemon = False
      thread.start()
    except Exception as e:
      print('error: ', e)
      conection.close()

def sendList(conn,list):
  for item in list:
    conn.sendall(item.encode(format))
    conn.recv(1024)
  msg = 'end'
  conn.send(msg.encode(format))

def sendFileHoder(fileName,conection):
    # print('getfilehoder')
    cursor.execute("select UserName from UserFiles where SharedFileName = ?", fileName)
    response= cursor.fetchall()
    usernames = [item[0] for item in response]
    usernames_online=connections[2]
    usernames=usernames.intersection(usernames_online)
    sendList(conection,usernames)

def recvList(conn):
    list = []

    item = conn.recv(1024).decode(format)

    while (item != "end"):
        
        list.append(item)
        #response
        conn.sendall(item.encode(format))
        item = conn.recv(1024).decode(format)
    
    return list


def serverLogin(conn,addr):

    # recv account from client
    client_account = recvList(conn)

    # query data: password
    cursor.execute("select Pass from Users where UserName = ?", client_account[0])
    password = cursor.fetchone()
    data_password = password[0]
    print(data_password)

    msg = "ok"
    if (client_account[1] == data_password):
        msg = "Login successfully"
        print(msg)
        conn.sendall(msg.encode(format))
        client_port=conn.recv(1024).decode(format)
        connections.append({'conn': conn, 'addr': addr,'user':client_account[0],'ip':addr[0],'port':client_port})
        return client_account[0]
    else:
        msg = "Invalid password"
        print(msg)
        conn.sendall(msg.encode(format))
    return None
     
def handleClient(conn, addr):
    print('client address: ', addr)
    # print('conection: ', conn.getsockname())
    msg=None
    loginName=None
    while (msg != "x"):
        msg = conn.recv(1024).decode(format)
        print("client ",addr, "says", msg)    
        if (msg == "login"):
            conn.sendall(msg.encode(format))
            loginName=serverLogin(conn,addr)   
        elif 'getfileholder' in msg.lower():
            temp = msg.split()[1]
            sendFileHoder(temp,conn)      
    if loginName!=None:
        connections = list(filter(lambda item: not (item['conn'] == conn and item['addr'] == addr and item['user'] == loginName), connections))

    print('client addrees', addr, 'finish')
    print(conn.getsockname(),'closed')
    conn.close()
def serverCommand():
    while True:
        try:
            command = input("Enter a command: ")
            if command.lower() == 'exit':
                break
            elif 'ping' in command.lower():
                temp = command.split()[1]
                ping(temp)
            elif 'discover' in command.lower():
                temp = command.split()[1]
                discover(temp)
            else:
                print(f"Unknown command: {command}")
        except:
            print("Error Command")
def ping(name):
    for connection in connections:
        if connection['user']==name:
            print(name,":",connection['addr'])
def discover(name):
    for connection in connections:
        if connection['user']==name:
            print("discover host:",name)
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LISTEN_PORT=8888
    try:
        sock1.connect(("127.0.0.1", LISTEN_PORT))
        print(f"[*] Connected to peer at 127.0.0.1")    
        
        # Send data to peer
        sock1.sendall("discover".encode(format))
        discover_data=sock1.recv(1024).decode(format)
        discover_data = json.loads(discover_data)
        print(json.dumps(discover_data, indent=2))
        
    except Exception as e:
        print(f"Error connecting to peer: {e}")
    finally:
        sock1.close()
# ------------------------------------------------------
if __name__ == "__main__":
    server_thread = threading.Thread(target=createServer)
    server_thread.start()
    serverCommand()
