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
import threading
from multiprocessing import Process, Queue
from time import sleep
from pygame import mixer
from PIL import Image, ImageTk

from circuit_breaker import circuit_breaker


class OpenWindow(object):

    def run_parallel(*functions):
        '''
        Run functions in parallel
        '''
        from multiprocessing import Process
        processes = []
        for function in functions:
            proc = Process(target=function)
            proc.start()
            processes.append(proc)
        for proc in processes:
            proc.join()

    def openWindow(self, title, label1, label2, label3, color, command, gpi1, gpi2, gpi3, image):
        OpenWindow.openWindowsSecundary(title, label1, label2, label3, color, command, gpi1, gpi2, gpi3, image)

    def openWindowsSecundary(title, label1, label2, label3, color, command, gpi1, gpi2, gpi3, image):
        status = label3
        print(status)
        window = tk.Tk()
        GPIO.output(gpi1, True)
        imageLoad = Image.open(image)
        imageResize = imageLoad.resize((window.winfo_screenwidth(), window.winfo_screenheight()))
        imagePrint = ImageTk.PhotoImage(imageResize)
        fondo = tk.Label(window, image=imagePrint).place(x=0, y=0)
        window.attributes('-fullscreen', True)
        print("tamaño de la pantalla: ", window.winfo_screenwidth(), window.winfo_screenheight())
        #         fondo.pack()
        # window.attributes('-fullscreen', True)
        # window.title(title)
        # window.configure(bg=color)
        # label1 = tk.Label(window, text=label1, bg=color)
        # label1.config(font=("Arial", 25))
        # label2 = tk.Label(window, text=label2, bg=color)
        # label2.config(font=("Arial", 25))
        # label3 = tk.Label(window, text=label3, bg=color)
        # label3.config(font=("Arial", 25))
        # label3.place(x=window.winfo_width() // 2, y=window.winfo_height() // 2, anchor='center')
        # window.bind("<FocusIn>")
        # label1.pack()
        # label2.pack()
        # label3.pack()
        mixer.init()
        mixer.music.load(command)
        mixer.music.play()
        window.after(3000, window.destroy)
        window.mainloop()

    def stardSounds(sound):
        os.system(sound)


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
    path_base_audio = 'assets/audio/{}'
    path_base_image = 'assets/image/{}'
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
        # GPIO.setup(40, GPIO.OUT)
        GPIO.output(29, False)
        GPIO.output(33, False)
        # GPIO.output(40, False)

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
                    openWindow.openWindow("Control Acceso", "", "BIENVENIDO", "Pase de movilidad válido", "green",
                                          FullScreenApp.path_base_audio.format("pm_valido.mp3"), 29,
                                          40, 40, FullScreenApp.path_base_image.format("movilidad-valido.png"))
                else:
                    openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                          "Pase de movilidad inválido\nFavor acercarse al guardia", "red",
                                          FullScreenApp.path_base_audio.format("pm_invalido.mp3"), 33, 40, 40,
                                          FullScreenApp.path_base_image.format("movilidad-invalido.png"))

            except:
                openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                      "Error de validación\nPor favor acercarse al guardia", "red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33, 40, 40,
                                      FullScreenApp.path_base_image.format("error_validacion.png"))
        elif parsed.netloc == "cmv.interior.gob.cl":
            try:
                openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                      "El pase único colectivo no es válido para ingresar", "red",
                                      FullScreenApp.path_base_audio.format("puc_novalido.mp3"), 33, 40, 40,
                                      FullScreenApp.path_base_image.format("movilidad-valido.png"))
            except:
                openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                      "Error de validación por favor acercarse al guardia", "red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33, 40, 40,
                                      FullScreenApp.path_base_image.format("pase-colectivo.png"))

        else:
            try:
                date2 = urlparse.parse_qs(parsed.query)['date'][0]
                date = datetime.strptime(date2, "%Y/%m/%d")
                # print(date2)
                # print(date)
                # print(datetime.today().date())
                if date.date() == datetime.today().date():
                    openWindow.openWindow("Control Acceso", "", "BIENVENIDO", "Pase de comisaría virtual válido",
                                          "green",
                                          FullScreenApp.path_base_audio.format("pcv_valido.mp3"), 29, 40, 40,
                                          FullScreenApp.path_base_image.format("comisaria-valido.png"))
                else:
                    openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                          "Pase de comisaría virtual inválido\nFavor acercarse al guardia", "red",
                                          FullScreenApp.path_base_audio.format("pcv_invalido.mp3"), 33, 40, 40,
                                          FullScreenApp.path_base_image.format("comisaria-invalido.png"))
            except:
                openWindow.openWindow("Control Acceso", "", "ALGO SALIÓ MAL",
                                      "Error de validación\nFavor acercarse al guardia", "red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33, 40, 40,
                                      FullScreenApp.path_base_image.format("error-validacion.png"))

    def readSerialOne(Thread):
        # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
        FullScreenApp.initRaspberry()
        connetVacuno = ConnectSite()
        openWindow = OpenWindow()
        # while True:
        #     line = ser.readline().decode()
        #     if len(line) > 0:
        # print(line)
        time.sleep(3)
        FullScreenApp.validateUrl("https://scanmevacuno.gob.cl/?a=109355338&b=1614219941&c=0", connetVacuno, openWindow)
        time.sleep(3)
        FullScreenApp.validateUrl(
            "https://comisariavirtual.cl/tramites/pdf/verifica.html?id=16223093312878ee6441b-3217-4860-84dc-2fbbdfad5c35&ate=2021/06/08&tramiteId=135",
            connetVacuno, openWindow)
        time.sleep(3)
        FullScreenApp.validateUrl(
            "https://comisariavirtual.cl/tramites/pdf/verifica.html?id=16223093312878ee6441b-3217-4860-84dc-2fbbdfad5c35&ate=2021/06/18&tramiteId=135",
            connetVacuno, openWindow)

    try:
        _thread.start_new_thread(readSerialOne, ("QR-1",))
    except:
        print("Error: unable to start thread")


while 1:
    pass
