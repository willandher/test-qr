import argparse
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
import time
import RPi.GPIO as GPIO
import _thread

from circuit_breaker import circuit_breaker


class OpenWindow(object):

    def openWindow(self, title, label1, label2, label3, color, command, gpi1, gpi2, gpi3):
        status = label3
        print(status)
        #GPIO.output(gpi2, True)
        window = tk.Tk()
        GPIO.output(gpi1, True)
        window.attributes('-fullscreen', True)
        window.title(title)
        window.configure(bg=color)
        label1 = tk.Label(window, text=label1, bg=color)
        label1.config(font=("Arial", 25))
        label2 = tk.Label(window, text=label2, bg=color)
        label2.config(font=("Arial", 25))
        label3 = tk.Label(window, text=label3, bg=color)
        label3.config(font=("Arial", 25))
        label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
        window.bind("<FocusIn>")
        label1.pack()
        label2.pack()
        label3.pack()
        #GPIO.output(gpi3, False)
        GPIO.output(gpi1, True)
        os.system(command)
        window.after(4000, window.destroy)
        window.mainloop()


class ConnectSite(object):

    @circuit_breaker()
    def requestGet(self, url, params):
        try:
            response = requests.get(url, params, timeout=0.3)
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
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)
        master = tk.Toplevel(root)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def initRaspberry():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(29, GPIO.OUT)
        GPIO.setup(33, GPIO.OUT)
        #GPIO.setup(40, GPIO.OUT)
        GPIO.output(29, False)
        GPIO.output(33, False)
        #GPIO.output(40, False)

    def validateUrl(url, connetVacuno, openWindow):
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
                    openWindow.openWindow("Control Acceso", "", "", "", "green", "omxplayer -o local pm_valido.mp3", 29,
                                          40, 40)
                else:
                    openWindow.openWindow("Control Acceso", "", "", "Pase Invalido", "red",
                                          "omxplayer -o local pm_invalido.mp3", 33, 40, 40)

            except:
                openWindow.openWindow("Control Acceso", "", "Algo Salio Mal", "Favor Acercarse al Guardia", "red",
                                      "omxplayer -o local err_validacion.mp3", 33, 40, 40)
        else:
            try:
                date2 = urlparse.parse_qs(parsed.query)['date'][0]
                date = datetime.strptime(date2, "%Y/%m/%d")
                # print(date2)
                # print(date)
                # print(datetime.today().date())
                if date.date() == datetime.today().date():
                    openWindow.openWindow("Control Acceso", "", "Todo Ok", "Bienvenido", "green",
                                          "omxplayer -o local pcv_valido.mp3", 29, 40, 40)
                else:
                    openWindow.openWindow("Control Acceso", "", "", "Pase Invalido", "red",
                                          "omxplayer -o local pcv_invalido.mp3", 33, 40, 40)

            except:
                openWindow.openWindow("Control Acceso", "", "Algo Salio Mal", "Favor Acercarse al Guardia",
                                      "red", "omxplayer -o local err_validacion.mp3", 33, 40, 40)

    def readSerialOne(Thread):
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
        connetVacuno = ConnectSite()
        openWindow = OpenWindow()
        while True:
            line = ser.readline().decode()
            if len(line) > 0:
                print(line)
                FullScreenApp.validateUrl(line, connetVacuno,openWindow)
                time.sleep(0.1)

    try:
        _thread.start_new_thread(readSerialOne, ("QR-1",))
    except:
        print("Error: unable to start thread")


FullScreenApp.initRaspberry()
while 1:
    pass
