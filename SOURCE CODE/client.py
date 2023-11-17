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
SEARCH = "search"
LIST = "listall"

ADMIN_USERNAME = 'admin'
ADMIN_PSWD = 'database'

INSERT_NEW_MATCH='insert_a_match'
UPDATE_SCORE = "upd_score"
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

# match : [ID, TeamA, TeamB, Score, Date, Time]

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
        
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b',bg="bisque2")
        button_back = tk.Button(self, text="Go back",bg="#20639b",fg='#f5ea54', command=lambda: controller.logout(self,client))
        button_list = tk.Button(self, text="List all", bg="#20639b",fg='#f5ea54',command=self.listAll)

        self.entry_search = tk.Entry(self)
        button_search = tk.Button(self, text="Search for ID",bg="#20639b",fg='#f5ea54', command=self.searchID)

        label_title.pack(pady=10)

        button_search.configure(width=10)
        button_list.configure(width=10)
        button_back.configure(width=10)

        self.entry_search.pack()

        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.pack(pady=4)

        button_search.pack(pady=2)
        button_list.pack(pady=2) 
        button_back.pack(pady=2)

        self.frame_detail = tk.Frame(self, bg="steelblue1")
        
        self.label_score = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_time = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)
        self.label_status = tk.Label(self.frame_detail,bg="steelblue1", text="", font=LARGE_FONT)

        self.tree_detail = ttk.Treeview(self.frame_detail)
        self.tree_detail["column"] = ("Time", "Player", "Team", "Event")
        
        self.tree_detail.column("#0", width=0, stretch=tk.NO)
        self.tree_detail.column("Time", anchor='c', width=50)
        self.tree_detail.column("Player", anchor='c', width=200)
        self.tree_detail.column("Team", anchor='c', width=200)
        self.tree_detail.column("Event", anchor='c', width=180)

        self.tree_detail.heading("0", text="", anchor='c')
        self.tree_detail.heading("Time", text="Time", anchor='c')
        self.tree_detail.heading("Player", text="Player", anchor='c')
        self.tree_detail.heading("Team", text="Team", anchor='c')
        self.tree_detail.heading("Event", text="Event", anchor='c')


        self.label_score.pack(pady=5)
        self.label_time.pack(pady=5)
        self.label_status.pack(pady=5)
        self.tree_detail.pack()
        


        self.frame_list = tk.Frame(self, bg="tomato")
        
        self.tree = ttk.Treeview(self.frame_list)

        
        self.tree["column"] = ("ID", "TeamA", "Score", "TeamB", "Status")
        
        
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor='c', width=30)
        self.tree.column("TeamA", anchor='e', width=140)
        self.tree.column("Score", anchor='c', width=40)
        self.tree.column("TeamB", anchor='w', width=140)
        self.tree.column("Status", anchor='c', width=80)

        self.tree.heading("0", text="", anchor='c')
        self.tree.heading("ID", text="ID", anchor='c')
        self.tree.heading("TeamA", text="TeamA", anchor='e')
        self.tree.heading("Score", text="Score", anchor='c')
        self.tree.heading("TeamB", text="TeamB", anchor='w')
        self.tree.heading("Status", text="Status", anchor='c')
        
        self.tree.pack(pady=20)
        
    
class AdminPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg="bisque2")
     
        self.match_frame=tk.Frame(self,bg="bisque2")
        self.detail_frame=tk.Frame(self,bg="bisque2")
        

        label_title = tk.Label(self, text="\n      ADMINISTRATOR \n", font='verdana 22 bold',fg='#20639b',bg="bisque2").grid(row=0,column=0,columnspan=2,)
        button_back = tk.Button(self, text="LOG OUT",bg="#20639b",fg='#f5ea54' ,command=lambda: controller.logout(self,client))
        self.button_list = tk.Button(self, text="ENTER",bg="#20639b",fg='#f5ea54',command= self.Insert_New_Match)
       
        self.label_option=tk.Label(self,text='OPTION\t',fg='#20639b',bg="bisque2",font='verdana 15 bold').grid(row=1,column=0)
        self.label_notice = tk.Label(self, text="", bg="bisque2" )
        self.label_notice.grid(row=2,column=1)
        # combobox
        self.n=tk.StringVar()
        self.option=ttk.Combobox(self,width=25,textvariable=self.n,font = "Helvetica 13 ")
        self.option['values']=('Insert a match','Update Score','Update Date&time','Insert detail')
        self.option['state'] = 'readonly'
        self.option.bind('<<ComboboxSelected>>',self.Choose_Function)
        self.option.current(0)
        self.option.grid(row=1,column=1)

        #match frame setup
        self.ID_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")
        self.teamA_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")
        self.teamB_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")
        self.score_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")
        self.date_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")
        self.time_entry=tk.Entry(self.match_frame,font = "Helvetica 13 bold")

        self.label_ID=tk.Label(self.match_frame, text ='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_teamA=tk.Label(self.match_frame, text='TeamA:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_teamB=tk.Label(self.match_frame,text='TeamB:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_score=tk.Label(self.match_frame,text='Score:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_date=tk.Label(self.match_frame,text="Date:\t",bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_time=tk.Label(self.match_frame,text="Time:\t",bg="bisque2",fg='#20639b',font='verdana  15 bold')
       
       #Detail frame setup
        self.Did_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Dteam_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.player_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Event_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")
        self.Dtime_entry=tk.Entry(self.detail_frame,font = "Helvetica 13 bold")

        
        self.label_Did=tk.Label(self.detail_frame,text='ID:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Dteam=tk.Label(self.detail_frame, text='Team:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_player=tk.Label(self.detail_frame,text='Player:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Event=tk.Label(self.detail_frame,text='Event:\t',bg="bisque2",fg='#20639b',font='verdana 15 bold')
        self.label_Dtime=tk.Label(self.detail_frame,text="Time:\t",bg="bisque2",fg='#20639b',font='verdana  15 bold')
        
        # button setup
        self.button_list.grid(row=12,column=1, ipady=7,ipadx=20)
        self.button_list.configure(width=10)
        button_back.grid(row=13,column=1, ipady=7,ipadx=20)
        button_back.configure(width=10)
    
    def Grid_define(self):
        #match frame
        self.label_ID.grid(row=3,column=0)
        self.label_teamA.grid(row=4,column=0)
        self.label_teamB.grid(row=5,column=0)
        self.label_score.grid(row=6,column=0)
        self.label_date.grid(row=7,column=0)
        self.label_time.grid(row=8,column=0)
        

        self.ID_entry.grid(row=3,column=1, ipady=7,ipadx=20)
        self.teamA_entry.grid(row=4,column=1, ipady=7,ipadx=20)
        self.teamB_entry.grid(row=5,column=1, ipady=7,ipadx=20)
        self.score_entry.grid(row=6,column=1, ipady=7,ipadx=20)
        self.date_entry.grid(row=7,column=1, ipady=7,ipadx=20)
        self.time_entry.grid(row=8,column=1, ipady=7,ipadx=20)
        

        #detail frame
        self.label_Did.grid(row=3,column=0)
        self.label_Dteam.grid(row=4,column=0)
        self.label_player.grid(row=5,column=0)
        self.label_Event.grid(row=6,column=0)
        self.label_Dtime.grid(row=7,column=0)

        self.Did_entry.grid(row=3,column=1, ipady=7,ipadx=20)
        self.Dteam_entry.grid(row=4,column=1, ipady=7,ipadx=20)
        self.player_entry.grid(row=5,column=1, ipady=7,ipadx=20)
        self.Event_entry.grid(row=6,column=1, ipady=7,ipadx=20)
        self.Dtime_entry.grid(row=7,column=1, ipady=7,ipadx=20)
      
    
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


