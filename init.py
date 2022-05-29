from tkinter import *
from tkinter import messagebox
import tkinter as tk
from camera import camera_init
import camera
import cv2, db
from attendance_check_tk import AttendanceCheck
def populate_list():
    print('Populating list')
def set_text(e,text):
    e.config(state='normal')
    e.delete(0,END)
    e.insert(0,text)
    e.config(state='disabled')
    return
def new_embeddings():
    x=mssv_entry.get()
    record =db.getSV(db.connect(),x)
    if record:
        print('Adding embeddings')
        cap, height, width = camera_init()
        faceprints=camera.stream(cap)
        db.save_embeddings(db.connect(),x,faceprints)
    else:
        messagebox.showinfo(title=None, message="Không tìm thấy MSSV")
    
def callback(event):
    x=mssv_entry.get()
    record =db.getSV(db.connect(),x)
    if record == None:
        set_text(name_entry,"")
        set_text(faculty_entry,"")
        return
    set_text(name_entry,record[1])
    khoa =db.getKhoa(db.connect(),record[4])
    set_text(faculty_entry,khoa)
    
    

def remove_embeddings():
    db.delete_embeddings(db.connect(),mssv_entry.get())
    print('Removed {} embeddings'.format(mssv_entry.get()))
    
def show_embeddings():
    x=mssv_entry.get()
    sv = db.getSV(db.connect(),x)
    if sv == None:
        messagebox.showinfo(title=None, message="Không tìm thấy SV")
        return
    records =db.get_embeddings(db.connect(),x)
    for record in records:
        print("\n")
        print(record[1])
#Create a new window
def attendance_check():
    AttendanceCheck()
app = Tk()


#MSSV
mssv_text = StringVar()
mssv_label = Label(app, text='MSSV', font=('bold',10), pady=20)
mssv_label.grid(row=0,column=0, sticky=W) #sticky = w => align to the west
mssv_entry= Entry(app, textvariable=mssv_text)
mssv_entry.bind('<Return>', callback)
mssv_entry.grid(row=0,column=1)

#Name
name_text = StringVar()
name_label = Label(app, text='Tên', font=('bold',10))
name_label.grid(row=0,column=2, sticky=W) 
name_entry= Entry(app, textvariable=name_text)
name_entry.config(state='disabled')
name_entry.grid(row=0,column=3)



#Faculty
faculty_text = StringVar()
faculty_label = Label(app, text='Khoa', font=('bold',10), pady=20)
faculty_label.grid(row=1,column=0, sticky=W) 
faculty_entry= Entry(app, textvariable=faculty_text)
faculty_entry.config(state='disabled')
faculty_entry.grid(row=1,column=1)

#remove embeddings button
remove_btn = Button(app,text='Remove faceprint',width=12,command=remove_embeddings)
remove_btn.grid(row=2,column=0,pady=20,columnspan=2,sticky = tk.W+tk.E)

#new embeddings button
new_btn = Button(app,text='New faceprint',width=12,command=new_embeddings)
new_btn.grid(row=2,column=2,sticky = tk.W+tk.E)

#show embeddings button
show_btn = Button(app,text='Show faceprint',width=12,command=show_embeddings)
show_btn.grid(row=2,column=3,sticky = tk.W+tk.E)

attendance_btn = Button(app,text='Attendance Check',width=12,command=attendance_check)
attendance_btn.grid(row=3,column=2,columnspan=2,pady=20,sticky = tk.W+tk.E)

app.title = "Faceprint Initialization"
app.geometry('600x250')

#Populate data
populate_list()
# db.update_diemdanh(db.connect(),'102190281',1,'buoi_1')
print(db.get_student_of_class(db.connect(),1))
#Start program
app.mainloop()

