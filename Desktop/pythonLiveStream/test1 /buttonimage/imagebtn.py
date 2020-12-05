import tkinter
from tkinter import *
from tkinter import messagebox

def btnclick():
    messagebox.showinfo("Message","Button is clicked")

root = tkinter.Tk()
root.geometry("800x800")

photo = PhotoImage(file="group.png")
photo2 = PhotoImage(file="group2.png")
btn = Button(
    root,
    image=photo,
    command=btnclick,
    padx=100,
    pady=100,
)
btn.pack(pady=50)

btn2 = Button(
    root,
    image=photo2,
    command=btnclick,
    border=0,
)
btn2.pack()
root.mainloop()