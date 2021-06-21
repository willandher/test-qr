from tkinter import *
from PIL import ImageTk, Image
import os

class Application(Frame):
    path_base_audio = 'assets/audio/{}'
    path_base_image = 'assets/image/{}'
    def __init__(self, parent):
        Frame.__init__(self,parent)
        self.pack(fill=BOTH, expand=True)
        self.create_Menu()
        self.create_widgets()

    def create_Menu(self):
        self.menuBar = Menu(self)
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open", command=self.getImage)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.exitProgram)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)
        root.config(menu=self.menuBar)

    def create_widgets(self):
        self.viewWindow = Canvas(self, bg="white")
        self.viewWindow.pack(side=TOP, fill=BOTH, expand=True)

    def getImage(self):
        print(Application.path_base_audio.join("veamos.png"))
        imageFile = Image.open("robot.png")
        image = imageFile.resize((200,100)) 
        imageFile = ImageTk.PhotoImage(image)
        self.viewWindow.image = imageFile
        self.viewWindow.create_image(self.viewWindow.winfo_width()/2, self.viewWindow.winfo_height()/2, anchor=CENTER, image=imageFile, tags="bg_img")
        self.update()    
    def exitProgram(self):
        os._exit(0)


print(Application.path_base_audio.format("veamos.png"))
root = Tk()
root.title("Photo Zone")
root.wm_state('normal')

app = Application(root)

root.mainloop()