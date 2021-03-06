from logging import root
import serial
import http.client
import os, sys
import requests
from datetime import datetime
import http.client
import json
import urllib.parse as urlparse
import tkinter as tk
#import RPi.GPIO as GPIO
import time
import _thread

from circuit_breaker import circuit_breaker


def destroy_windows():
    window.destroy()

class ConnectSite(object):
    site = None
    def __init__(self, site):
        self.site = site

    @circuit_breaker()
    def requestGet(self, url, params):
        try:
            response = requests.get(url,params, timeout=0.3)
            if response.status_code == http.HTTPStatus.OK:
                print(f"Call to {url} succeed with status code = {response.status_code}")
                return response
            if 500 <= response.status_code < 600:
                print(f"Call to {url} failed with status code = {response.status_code}")
                raise Exception("Server Issue")
        except Exception:
            print(f"Call to {url} failed")

    @circuit_breaker()
    def requestPost(self, url, payload, headers):
        try:
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code == http.HTTPStatus.OK:
                print(f"Call to {url} succeed with status code = {response.status_code}")
                return response
            if 500 <= response.status_code < 600:
                print(f"Call to {url} failed with status code = {response.status_code}")
                raise Exception("Server Issue")

        except Exception:
            print(f"Call to {url} failed")

class FullScreenApp(object):

        def __init__(self, master, **kwargs):
                self.master=master
                pad=3
                self._geom='200x200+0+0'
                master.geometry("{0}x{1}+0+0".format(
                        master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
                master.bind('<Escape>',self.toggle_geom)
                master= tk.Toplevel(root)
        def toggle_geom(self,event):
                geom=self.master.winfo_geometry()
                print(geom,self._geom)
                self.master.geometry(self._geom)
                self._geom=geom

        #def initGPIO(self):
        #    GPIO.setwarnings(False)
        #    GPIO.setmode(GPIO.BOARD)
        #    GPIO.setup(29, GPIO.OUT)
        #    GPIO.setup(33, GPIO.OUT)
        #    GPIO.setup(40, GPIO.OUT)
        #    GPIO.output(29, False)
        #    GPIO.output(33, False)
        #    GPIO.output(40, False)

        def validateUrl(url, connetVacuno):
            findRequestSign = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=AIzaSyBHBNWPNPGF33TnGCKbY_6Tw_LTdTcYYIA"
            parsed = urlparse.urlparse(url)
            if parsed.netloc == "scanmevacuno.gob.cl":
                try:
                    payload = json.dumps({
                        "returnSecureToken": True
                    })
                    headers = {
                        'Referer': 'https://scanmevacuno.gob.cl/',
                        'Content-Type': 'application/json',
                    }
                    responseFile = connetVacuno.requestPost(findRequestSign, payload, headers)
                    dataJson = json.loads(responseFile.content.decode("utf-8"))
                    a = urlparse.parse_qs(parsed.query)['a'][0]
                    b = urlparse.parse_qs(parsed.query)['b'][0]
                    c = urlparse.parse_qs(parsed.query)['c'][0]
                    bearer = "Bearer " + dataJson.get('idToken')

                    payloadNeo = json.dumps({
                        "data": {
                            "a": a,
                            "b": b,
                            "c": c
                        }
                    })
                    headersNeo = {
                        'Referer': 'https://scanmevacuno.gob.cl/',
                        'Origin': 'https://scanmevacuno.gob.cl',
                        'Authorization': bearer,
                        'Content-Type': 'application/json'
                    }
                    findRequestValidate = "https://us-central1-scanner-mevacuno.cloudfunctions.net/neogcscanner"
                    responseFileValidate = connetVacuno.requestPost(findRequestValidate, payloadNeo, headersNeo)
                    dataJsonNeo = json.loads(responseFileValidate.content.decode("utf-8"))
                    status = dataJsonNeo.get('result').get('payload').get('global_status')
                    print(status)
                    if status == "green":
                        #GPIO.output(29, True)
                        #GPIO.output(40, True)
                        os.system('omxplayer -o local pm_valido.mp3')
                        window = tk.Tk()
                        window.attributes('-fullscreen', True)
                        window.title("Control Acceso")
                        window.configure(bg='green')
                        label1 = tk.Label(window, text="", bg="green")
                        label1.config(font=("Arial", 25))
                        label2 = tk.Label(window, text="Todo Ok", bg="green")
                        label2.config(font=("Arial", 25))
                        label3 = tk.Label(window, text="Bienvenido", bg="green")
                        label3.config(font=("Arial", 25))
                        label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
                        window.bind("<FocusIn>")
                        label1.pack()
                        label2.pack()
                        label3.pack()
                        #GPIO.output(40, False)
                        window.after(3000, window.destroy())
                        window.mainloop()
                    else:
                        #GPIO.output(33, True)
                        #GPIO.output(40, True)
                        os.system('omxplayer -o local pm_invalido.mp3')
                        window = tk.Tk()
                        window.attributes('-fullscreen', True)
                        window.title("Control Acceso")
                        window.configure(bg='red')
                        label1 = tk.Label(window, text="", bg="red")
                        label1.config(font=("Arial", 25))
                        label2 = tk.Label(window, text="", bg="red")
                        label2.config(font=("Arial", 25))
                        label3 = tk.Label(window, text="Pase Invalido", bg="red")
                        label3.config(font=("Arial", 25))
                        label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
                        window.bind("<FocusIn>")
                        label1.pack()
                        label2.pack()
                        label3.pack()
                        #GPIO.output(40, False)
                        time.sleep(3)
                        window.destroy()
                    window.mainloop()
                except:
                    status = "Algo Salio Mal - Favor Acercarse al Guardia"
                    print(status)
                    #GPIO.output(33, True)
                    #GPIO.output(40, True)
                    os.system('omxplayer -o local err_validacion.mp3')
                    window = tk.Tk()
                    window.attributes('-fullscreen', True)
                    window.title("Control Acceso")
                    window.configure(bg='red')
                    label1 = tk.Label(window, text="", bg="red")
                    label1.config(font=("Arial", 25))
                    label2 = tk.Label(window, text="Algo Salio Mal", bg="red")
                    label2.config(font=("Arial", 25))
                    label3 = tk.Label(window, text="Favor Acercarse al Guardia", bg="red")
                    label3.config(font=("Arial", 25))
                    label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
                    window.bind("<FocusIn>")
                    label1.pack()
                    label2.pack()
                    label3.pack()
                    #GPIO.output(40, False)
                    time.sleep(3)
                    window.destroy()
                    window.mainloop()
            else:
                try:
                    date2 = urlparse.parse_qs(parsed.query)['date'][0]
                    date = datetime.strptime(date2, "%Y/%m/%d")
                    # print(date2)
                    # print(date)
                    # print(datetime.today().date())
                    if date.date() == datetime.today().date():
                        #GPIO.output(29, True)
                        #GPIO.output(40, True)
                        os.system('omxplayer -o local pcv_valido.mp3')
                        print("Todo OK - Bienvenido")
                        window = tk.Tk()
                        window.attributes('-fullscreen', True)
                        window.title("Control Acceso")
                        window.configure(bg='green')
                        label1 = tk.Label(window, text="", bg="green")
                        label1.config(font=("Arial", 25))
                        label2 = tk.Label(window, text="Todo Ok", bg="green")
                        label2.config(font=("Arial", 25))
                        label3 = tk.Label(window, text="Bienvenido", bg="green")
                        label3.config(font=("Arial", 25))
                        label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
                        window.bind("<FocusIn>")
                        label1.pack()
                        label2.pack()
                        label3.pack()
                        #GPIO.output(40, False)
                        time.sleep(3)
                        window.destroy()
                        window.mainloop()

                    else:
                        #GPIO.output(33, True)
                        #GPIO.output(40, True)
                        os.system('omxplayer -o local pcv_invalido.mp3')
                        print("Pase Invalido")
                        window = tk.Tk()
                        window.attributes('-fullscreen', True)
                        window.title("Control Acceso")
                        window.configure(bg='red')
                        label1 = tk.Label(window, text="", bg="red")
                        label1.config(font=("Arial", 25))
                        label2 = tk.Label(window, text="", bg="red")
                        label2.config(font=("Arial", 25))
                        label3 = tk.Label(window, text="Pase Invalido", bg="red")
                        label3.config(font=("Arial", 25))
                        label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
                        window.bind("<FocusIn>")
                        label1.pack()
                        label2.pack()
                        label3.pack()
                        #GPIO.output(40, False)
                        time.sleep(3)
                        window.destroy()
                        window.mainloop()
                except:
                    status = "Algo Salio Mal - Favor Acercarse al Guardia"
                    print(status)
                    #GPIO.output(33, True)
                    #GPIO.output(40, True)
                    os.system('omxplayer -o local err_validacion.mp3')
                    window = tk.Tk()
                    window.attributes('-fullscreen', True)
                    window.title("Control Acceso")
                    window.configure(bg='red')
                    label1 = tk.Label(window, text="", bg="red")
                    label1.config(font=("Arial", 25))
                    label2 = tk.Label(window, text="Algo Salio Mal", bg="red")
                    label2.config(font=("Arial", 25))
                    label3 = tk.Label(window, text="Favor Acercarse al Guardia", bg="red")
                    label3.config(font=("Arial", 25))
                    label1.pack()
                    label2.pack()
                    label3.pack()
                    #GPIO.output(40, False)
                    time.sleep(3)
                    window.destroy()
                    window.mainloop()

        def readSerialOne(Thread):
           #ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
            connetVacuno = ConnectSite("www.googleapis.com")
            while True:
                #line = ser.readline().decode()
                #if len(line) > 0:
                 #   print(line)
                FullScreenApp.validateUrl(line, connetVacuno)
                time.sleep(0.1)
        try:
            _thread.start_new_thread(readSerialOne, ("QR-1",))
        except:
            print("Error: unable to start thread")





while 1:
    pass



