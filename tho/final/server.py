import socket
import threading
import pyodbc
dirver ='ODBC Driver 17 for SQL Server'
sqlServer='DESKTOP-Q3MGK47;Database=Socket_state'
sqlUsername ='ndt'
sqlPassword ='NDTnvt01987274'
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

def createServer():
  host = '127.0.0.1'
  server_port = 65432
  server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  server.bind((host,server_port))
  server.listen(3)
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
    cursor.execute("select * from fileUpload where filename = ?", fileName)
    response= cursor.fetchall()
    usernames = [item[1] for item in response]
    sendList(conection,usernames)
     
def handleClient(conn, addr):
    print('client address: ', addr)
    # print('conection: ', conn.getsockname())
    msg=None
    while(msg!='x'):
      msg = conn.recv(1024).decode(format)
      command,data = msg.split(' ')
      print('client command: ', command)
      print('client request file name: ', data)
      if (command =='GETFILEHODER'):
        sendFileHoder(data,conn)
    print('client addrees', addr, 'finish')
    print(conn.getsockname(),'closed')
    conn.close()
# ------------------------------------------------------
if __name__ == "__main__":
    createServer()

