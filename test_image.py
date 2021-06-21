import io
import urllib.request
import tkinter as tk

from PIL import Image, ImageTk


image = "robot.jpeg"

class MiApp:

    def __init__(self):

        self.root = tk.Tk()
        load = Image.open(image)
        imagen = ImageTk.PhotoImage(load)
        fm = tk.Frame(self.root)
        fm.pack()
        btn = tk.Button(fm, image=imagen)
        btn.img_ref = imagen # Nunca te olvides de maantener una referencia
        btn.pack()

    def mainloop(self):
        self.root.mainloop()

if __name__ == '__main__':
    ejemplo = MiApp()
    ejemplo.mainloop()