import socket
import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk 
import threading
from datetime import datetime

HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"

LARGE_FONT = ("verdana", 13,"bold")

#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
LIST = "listall"

ADMIN_USERNAME = 'admin'
ADMIN_PSWD = 'database'

PUBLISH_FILE='publish_file'
REMOVE_FILE="remove_file"
#GUI intialize
class FileSharing_App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, HomePage,AdminPage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("700x500")
        elif container == AdminPage:
            self.geometry("450x500")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            
            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                if user =="admin":
                    self.showFrame(AdminPage)
                else:
                    self.showFrame(HomePage)
                
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def signUp(self,curFrame, sck):
        
        try:
        
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if pswd == "":
                curFrame.label_notice["text"] = "password cannot be empty"
                return 

            #notice server for starting log in
            option = SIGNUP
            sck.sendall(option.encode(FORMAT))
            
            
            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "True":
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")

    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"





class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")

        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        label_user = tk.Label(self, text="username ",fg='#20639b',bg="bisque2",font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',bg="bisque2",font='verdana 10 ')

        self.label_notice = tk.Label(self,text="",bg="bisque2")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white', command=lambda: controller.signUp(self, client)) 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        button_back = tk.Button(self, text="Go back",bg="#20639b",fg='#f5ea54', command=lambda: controller.logout(self,client))
        button_list = tk.Button(self, text="List all", bg="#20639b",fg='#f5ea54',command=self.listAll)

        label_title.pack(pady=10)

        button_list.configure(width=10)
        button_back.configure(width=10)


        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.pack(pady=4)

        button_list.pack(pady=2) 
        button_back.pack(pady=2)

        
        self.frame_list = tk.Frame(self, bg="tomato")
        
        self.tree = ttk.Treeview(self.frame_list)

        
        self.tree["column"] = ("fname", "lname")
        
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("fname", anchor='c', width=150)
        self.tree.column("lname", anchor='c', width=150)

        self.tree.heading("0", text="", anchor='c')
        self.tree.heading("fname", text="fname", anchor='c')
        self.tree.heading("lname", text="lname", anchor='c')
        
        self.tree.pack(pady=20)


    def recieveFiles(self):
        match = []
    
        matches = []
        data = ''
        while True:
            data = client.recv(1024).decode(FORMAT)
            client.sendall(data.encode(FORMAT))
            if data == "end":
                break
            
            # File : [fname, lname]

            for i in range(2):
                data = client.recv(1024).decode(FORMAT)
                client.sendall(data.encode(FORMAT))
                match.append(data) 

            
            matches.append(match)
            match = []

        return matches

    def listAll(self):
        try:
            self.frame_detail.pack_forget()

            option = LIST
            client.sendall(option.encode(FORMAT))
            
            matches = self.recieveFiles()
            
            x = self.tree.get_children()
            for item in x:
                self.tree.delete(item)

            i = 0
            for m in matches:
                self.tree.insert(parent="", index="end", iid=i, 
                        values=( m[0], m[1]))
                
                i += 1

            self.frame_list.pack(pady=10)
        except:
            self.label_notice["text"] = "Error"
        
    
class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
     
        self.file_frame=tk.Frame(self,bg="bisque2")
        

        label_title = tk.Label(self, text="\n      ADMINISTRATOR \n", font='verdana 22 bold',fg='#20639b',bg="bisque2").grid(row=0,column=0,columnspan=2,)
        button_back = tk.Button(self, text="LOG OUT",bg="#20639b",fg='#f5ea54' ,command=lambda: controller.logout(self,client))
        self.button_list = tk.Button(self, text="ENTER",bg="#20639b",fg='#f5ea54',command= self.Publish_File)
       
        self.label_option=tk.Label(self,text='OPTION\t',fg='#20639b',bg="bisque2",font='verdana 15 bold').grid(row=1,column=0)
        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.grid(row=2,column=1)
        # combobox
        self.n=tk.StringVar()
        self.option=ttk.Combobox(self,width=25,textvariable=self.n,font = "Helvetica 13 ")
        self.option['values']=('Publish File','Remove File')
        self.option['state'] = 'readonly'
        self.option.bind('<<ComboboxSelected>>',self.Choose_Function)
        self.option.current(0)
        self.option.grid(row=1,column=1)

        #file frame setup
        self.lname_entry=tk.Entry(self.file_frame,font = "Helvetica 13 bold")
        self.fname_entry=tk.Entry(self.file_frame,font = "Helvetica 13 bold")

        self.label_lname=tk.Label(self.file_frame, text='lname:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_fname=tk.Label(self.file_frame,text='fname:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
   
        # button setup
        self.button_list.grid(row=12,column=1, ipady=7,ipadx=20)
        self.button_list.configure(width=10)
        button_back.grid(row=13,column=1, ipady=7,ipadx=20)
        button_back.configure(width=10)
    
    def Grid_define(self):
        #file frame
        self.label_lname.grid(row=4,column=0)
        self.label_fname.grid(row=5,column=0)
       
        self.lname_entry.grid(row=4,column=1, ipady=7,ipadx=20)
        self.fname_entry.grid(row=5,column=1, ipady=7,ipadx=20)

    def Delete_Entry(self):
        self.lname_entry.delete(0,'end')
        self.fname_entry.delete(0,'end')

    def Choose_Function(self,event):
        msg= self.option.get()
        self.file_frame.grid_forget()
        self.label_notice["text"] = ""
        if msg=='Publish File':
            self.file_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_define()
            self.button_list.configure(command=self.Publish_File)
        
        if msg=='Remove File':
            self.file_frame.grid(row=3,column=0,columnspan=2)
            self.Grid_define()
            self.button_list.configure(command=self.Remove_File)

        self.Delete_Entry()

    def Publish_File(self):
        try:
            lname=self.lname_entry.get()
            fname=self.fname_entry.get()
            
            if lname=="" or fname=="":
                self.label_notice["text"] = "Field cannot be empty"
                return
            
            option=PUBLISH_FILE
            command=lname+" "+fname

            # Pad the command to a fixed length of 1024 characters
            padded_command = command.ljust(1024)

            # Send the padded command to the server
            client.send(padded_command.encode())

            # Receive the response from the server
            response = client.recv(1024).decode()
            print("Server response:", response)
        except:
            self.label_notice["text"] = "Error"


    def Remove_File(self):
        try:
            lname=self.lname_entry.get()
            fname=self.fname_entry.get()
            
            if lname=="" or fname=="":
                self.label_notice["text"] = "Field cannot be empty"
                return
            
            option=PUBLISH_FILE
            command=lname+" "+fname

            # Pad the command to a fixed length of 1024 characters
            padded_command = command.ljust(1024)

            # Send the padded command to the server
            client.send(padded_command.encode())

            # Receive the response from the server
            response = client.recv(1024).decode()
            print("Server response:", response)
        except:
            self.label_notice["text"] = "Error"

            

    
#GLOBAL socket initialize
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)

client.connect(server_address)


app = FileSharing_App()



#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()


