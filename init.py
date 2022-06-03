from pathlib import Path
from camera import camera_init
import camera
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, messagebox
import db
from tkinter import *
from attendance_check_tk import AttendanceCheck
def set_text(e,text):
    e.delete(0,END)
    e.insert(0,text)
    return

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
    x=mssv_entry.get()
    sv = db.getSV(db.connect(),x)
    if sv == None:
        messagebox.showinfo(title=None, message="Không tìm thấy SV")
        return
    db.delete_embeddings(db.connect(),mssv_entry.get())
    print('Removed {} embeddings'.format(mssv_entry.get()))

def new_embeddings():
    x=mssv_entry.get()
    record =db.getSV(db.connect(),x)
    if record:
        print('Adding embeddings')
        cap, height, width = camera_init()
        faceprints=camera.stream(cap)
        # print(faceprints)
        db.save_embeddings(db.connect(),x,faceprints)
    else:
        messagebox.showinfo(title=None, message="Không tìm thấy MSSV")
    
def attendance_check():
    AttendanceCheck()
    
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
        print(len(record[1]))
        
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


app = Tk()

app.geometry("894x600")
app.configure(bg = "#FFFFFF")


canvas = Canvas(
    app,
    bg = "#FFFFFF",
    height = 600,
    width = 894,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
image_image_1 = PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    434.0,
    300.0,
    image=image_image_1
)
#MSSV
mssv_text = StringVar()
entry_image_1 = PhotoImage(
    file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(
    612.0,
    98.0,
    image=entry_image_1
)
mssv_entry = Entry(
    app,
    bd=0,
    bg="#FFE1E1",
    highlightthickness=0,
    textvariable=mssv_text
)
mssv_entry.place(
    x=443.0,
    y=69.0,
    width=338.0,
    height=56.0
)
mssv_entry.bind('<Return>', callback)

#Name
name_text = StringVar()
entry_image_2 = PhotoImage(
    file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(
    612.0,
    206.0,
    image=entry_image_2
)
name_entry = Entry(
    app,
    bd=0,
    bg="#FFE1E1",
    highlightthickness=0,
    textvariable=name_text
)

name_entry.place(
    x=443.0,
    y=177.0,
    width=338.0,
    height=56.0
)
#Faculty
faculty_text = StringVar()
entry_image_3 = PhotoImage(
    file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(
    612.0,
    314.0,
    image=entry_image_3
)
faculty_entry = Entry(
    app,
    bd=0,
    bg="#FFE1E1",
    highlightthickness=0,
     textvariable=faculty_text
)
faculty_entry.place(
    x=443.0,
    y=285.0,
    width=338.0,
    height=56.0
)
#Attendance check button
button_image_1 = PhotoImage(
    file=relative_to_assets("button_1.png"))
attendance_btn = Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=attendance_check,
    relief="flat"
)
attendance_btn.place(
    x=30.0,
    y=467.0,
    width=290.0,
    height=65.0
)
#remove embeddings button
button_image_2 = PhotoImage(
    file=relative_to_assets("button_2.png"))
remove_btn = Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=remove_embeddings,
    relief="flat"
)
remove_btn.place(
    x=416.0,
    y=376.0,
    width=199.0,
    height=53.0
)

button_image_3 = PhotoImage(
    file=relative_to_assets("button_3.png"))
show_btn = Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=show_embeddings,
    relief="flat"
)
show_btn.place(
    x=625.0,
    y=375.0,
    width=185.0,
    height=54.0
)
button_image_4 = PhotoImage(
    file=relative_to_assets("button_4.png"))
new_btn = Button(
    image=button_image_4,
    borderwidth=0,
    highlightthickness=0,
    command=new_embeddings,
    relief="flat"
)
new_btn.place(
    x=414.0,
    y=456.0,
    width=404.0,
    height=52.0
)
app.resizable(False, False)
app.mainloop()