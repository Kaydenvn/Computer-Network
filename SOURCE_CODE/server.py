import socket
import threading
import pyodbc
import json
sqlUsername ='test1'
sqlPassword ='123456'
# conect database
conx = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=MSI\SQLEXPRESS; Database=BTL_MMT; UID=test1; PWD=123456;')
cursor = conx.cursor()

#connections='conn' 'addr''user''ip''port')

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

def createServer(connections):
  #host=getIPAdress()
  #server_port=find_free_port(host,11111,22222)
  host = '127.0.0.1'
  server_port = 65315
  server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  server.bind((host,server_port))
  server.listen(10)
  while(True):
    try:
      conection,addr=server.accept()
      thread = threading.Thread(target=handleClient, args=(conection,addr,connections))
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

def sendFileHolder(fileName,conection):
    # print('getfilehoder')
    cursor.execute("select UserName from UserFiles where SharedFileName = ?", fileName)
    response= cursor.fetchall()
    usernames = [item[0] for item in response]
    usernames_online = [{'user': temp['user'], 'ip': temp['ip'], 'port': temp['port']} for temp in connections if temp['user'] in usernames]
    json_data = json.dumps(usernames_online)
    conection.sendall(json_data.encode(format))

def recvList(conn):
    list = []

    item = conn.recv(1024).decode(format)

    while (item != "end"):
        
        list.append(item)
        #response
        conn.sendall(item.encode(format))
        item = conn.recv(1024).decode(format)
    
    return list
def serverSignup(conn):
    client_account = recvList(conn)
    cursor.execute("select UserName from Users")
    datas=cursor.fetchall()
    if any(client_account[0] in data for data in datas):
        msg = "User name already exists"
        conn.sendall(msg.encode(format))
    else:
        cursor.execute("INSERT INTO Users (UserName, Pass) VALUES (?, ?)", client_account[0], client_account[1])
        msg = "Sign up successfully"
        conn.sendall(msg.encode(format))
        conx.commit()
def serverLogin(conn,addr):

    # recv account from client
    client_account = recvList(conn)

    # query data: password
    cursor.execute("SELECT COUNT(*) FROM Users WHERE UserName = ?", client_account[0])
    result = cursor.fetchone()
    user_count = result[0]
    if user_count==0:
        msg = "Username does not exist"
        conn.sendall(msg.encode(format))
        return None
    cursor.execute("select Pass from Users where UserName = ?", client_account[0])
    password = cursor.fetchone()
    data_password = password[0]
    if (client_account[1] == data_password):
        msg = "Log in successfully"
        conn.sendall(msg.encode(format))
        client_port=conn.recv(1024).decode(format)
        connections.append({'conn': conn, 'addr': addr,'user':client_account[0],'ip':addr[0],'port':client_port})
        print("User", client_account[0], "login!")
        return client_account[0]
    else:
        msg = "Invalid password"
        conn.sendall(msg.encode(format))
    return None
    
def serverlogout(conn,connections,loginName):
    for connection in connections:
        if connection['user']==loginName:
            connections.remove(connection)
            break
    msg = "Log out successfully"
    conn.sendall(msg.encode(format))

def handleClient(conn, addr, connections):
    msg=None
    loginName=None
    while (msg != "x"):
        msg = conn.recv(1024).decode(format)
        parts = msg.split()
       # print("client ",addr, "says", msg)    
        if (msg == "login"):
            if loginName==None:
                conn.sendall(msg.encode(format))
                loginName=serverLogin(conn,addr)
            else:
                print("You are already logged in")
        elif (msg == "signup"):
            conn.sendall(msg.encode(format))
            serverSignup(conn)
        elif (msg == "logout"):
            serverlogout(conn,connections,loginName)
        elif len(parts) == 3:
            if parts[0]=="publish":
                publishFile(parts[1],parts[2],loginName)
            if parts[0]=="remove":
                removeFile(parts[1],parts[2],loginName)
        elif len(parts) == 2:
            if 'getfileholder' in msg.lower():
                sendFileHolder(parts[1],conn)  
    print('client addrees', addr, 'finish')
    print(conn.getsockname(),'closed')
    conn.close()
def removeFile(lname,fname,username):
    cursor.execute("DELETE FROM UserFiles WHERE UserName = ? AND LocalFileName = ? AND SharedFileName = ?", username, lname, fname)
    conx.commit()
    cursor.execute("SELECT * FROM UserFiles WHERE LocalFileName = ? AND SharedFileName = ?",lname,fname)
    rows = cursor.fetchall()
    if rows:
        pass
    else:
        cursor.execute("DELETE FROM Files WHERE LocalFileName = ? AND SharedFileName = ?", lname, fname)
        conx.commit()
def publishFile(lname,fname,username):
    cursor.execute("INSERT INTO Files (LocalFileName, SharedFileName) VALUES (?, ?)", lname, fname)
    cursor.execute("INSERT INTO UserFiles (UserName,LocalFileName, SharedFileName) VALUES (?, ?, ?)",username, lname, fname)
    conx.commit()

def serverCommand():
    while True:
        try:
            command = input()
            temp = command.split()
            if command.lower() == 'exit':
                break
            elif command=="ping":
                pingAll()
            elif len(temp)==2:
                if 'ping' in command.lower():
                    ping(temp[1])
                elif 'discover' in command.lower():
                    discover(temp[1])
            else:
                print(f"Unknown command: {command}")
        except:
            print("Error Command")
def pingAll():
    for connection in connections:
        print(connection['user'],":",connection['addr'])
def ping(name):
    for connection in connections:
        if connection['user']==name:
            print(name,":",connection['addr'])
            return
    print("User is not online or invalid user!")
def discover(name):
    port=None
    ip=None
    for connection in connections:
        if connection['user']==name:
            print("discover host:",name)
            port=connection['port']
            ip=connection['ip']
            print(connection)
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock1.connect((ip, int(port)))        
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
    connections=[]
    server_thread = threading.Thread(target=createServer,args=(connections,))
    server_thread.start()
    serverCommand()
