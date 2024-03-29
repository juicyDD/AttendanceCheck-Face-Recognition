from tkinter import *
from tkinter import messagebox
from camera_diemdanh import *
from tkinter.ttk import *
import cv2, db
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import tkinter as tk
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets_attendance")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class AttendanceCheck:
    def callback(self, event):
        self.my_list.delete(0,'end')
        lophocphan =[]
        lophocphan = db.getLopHocPhan(db.connect(), self.msgv_entry.get())
        for row in lophocphan:
            self.my_list.insert(END, row)
    
    def diemdanh(self):
        if self.day =='' or self.lophp =='':
            messagebox.showinfo(title=None, message="Chọn lớp học phần và buổi học cần điểm danh")
            print('no selection')
            return
        self.lophp = list(self.lophp)[0]
        print('Mã lớp học phần đã chọn:', self.lophp)
        print('Buổi học đã chọn:', self.day)
        
        self.dssv = db.get_student_of_class(db.connect(), self.lophp)
        
        print('so sv trong lop',self.dssv)
        noneidx = 0
        for mssv in self.dssv:
            vttemp=db.get_embeddings(db.connect(),mssv)
            print(vttemp)
            
            if vttemp is None:
                continue
            self.vectordactrung_theolop.extend(vttemp)
        print('so luong vt',len(self.vectordactrung_theolop))
        
            
        
        embeddings_ref = []
        for vector in self.vectordactrung_theolop:
            embeddings_ref.append(vector[1])
            
        cap, height, width = camera_init()
        embeddings_ref = np.array(embeddings_ref)
        print(embeddings_ref.shape)
        stream(cap,embeddings_ref,self.vectordactrung_theolop,self.lophp,self.day)
        
            
    def callback1(self,e):
        name = self.cbbox.get()
        values_from_selected_name = self.df[name]
        self.day = values_from_selected_name
    def callback2(self,e):
        lophp = self.my_list.get(self.my_list.curselection())
        self.lophp = lophp
        
    def __init__(self):
        self.vectordactrung_theolop =[]
        
        self.day = '' #buổi học
        self.lophp = '' #lớp học phần
        self.dsdiemdanh = None  #danh sách điểm danh
        
        self.df= {'Buổi 1' :'buoi_1', 'Buổi 2' : 'buoi_2','Buổi 3': 'buoi_3','Buổi 4' : 'buoi_4',
                  'Buổi 5' : 'buoi_5', 'Buổi 6' : 'buoi_6','Buổi 7': 'buoi_7', 'Buổi 8' : 'buoi_8',
                  'Buổi 9':'buoi_9', 'Buổi 10': 'buoi_10','Buổi 11' : 'buoi_11', 'Buổi 12' : 'buoi_12',
                  'Buổi 13' : 'buoi_13', 'Buổi 14' : 'buoi_14','Buổi 15':'buoi_15'}
                   #column = buổi học (value,display)
        self.window = tk.Toplevel()
        
        # self.window.configure(height=400, width=700)
        self.window.title="Điểm danh"
        self.window.geometry("700x400")
        self.window.configure(bg = "#FFE5E5")
        self.canvas = Canvas(
            self.window,
            bg = "#FFE5E5",
            height = 400,
            width = 700,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        self.canvas.place(x = 0, y = 0)
        self.image_image_1 = PhotoImage(
            file=relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(
            350.0,
            189.0,
            image=self.image_image_1
        )
        
        #MSGV
        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        
        entry_bg_1 = self.canvas.create_image(
            157.0,
            65.5,
            image=entry_image_1
        )
        self.msgv_text = StringVar()
        self.msgv_entry = Entry(
            self.window,
            bd=0,
            bg="#FFC7C7",
            highlightthickness=0,
            textvariable=self.msgv_text
        )
        self.msgv_entry.place(
                x=60.0,
                y=46.0,
                width=194.0,
                height=37.0
            )
        self.msgv_entry.bind('<Return>', self.callback)
        
        #combobox
        self.cbbox = Combobox(self.window, state="readonly")
        self.cbbox.place(x=287.0,y=46.0,width=179.0,height=42.0)
        all_values = ('Buổi 1', 
                        'Buổi 2',
                        'Buổi 3',
                        'Buổi 4',
                        'Buổi 5',
                        'Buổi 6',
                        'Buổi 7',
                        'Buổi 8',
                        'Buổi 9',
                        'Buổi 10',
                        'Buổi 11',
                        'Buổi 12',
                        'Buổi 13',
                        'Buổi 14',
                        'Buổi 15')
        self.cbbox['values'] = all_values
        self.cbbox.bind("<<ComboboxSelected>>", self.callback1)
        #button
        button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
        attendance_btn = Button(
            self.window,
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.diemdanh,
            relief="flat"
        )
        attendance_btn.place(
            x=499.0,
            y=46.0,
            width=145.0,
            height=39.0
        )
        #list
        self.my_list = Listbox(self.window,height=12,width=80, border = 0)
        # self.my_list.grid(row=3,column=0,columnspan=8,rowspan=6,pady=10,padx=20)
        self.my_list.place(x=56,y=144,width=590,height=199)
        self.my_list.bind("<<ListboxSelect>>", self.callback2)
        
        #scrollbar
        self.scrollbar=Scrollbar(self.window)
        # self.scrollbar.grid(row=3,column=7)
        self.scrollbar.place(x=627,y=146,width=17,height=196)
        
        # #set scroll to listbox
        self.my_list.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.my_list.yview)
        
        self.window.resizable(False, False)
        self.window.mainloop()
        