import argparse
from logging import root
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
from pygame import mixer
import serial
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

    def openWindow(self, color, command, gpi1, image):
        OpenWindow.openWindowsSecundary(color, command, gpi1,image)

    def openWindowsSecundary(color, command, gpi1, image):
        print(color)
        window = tk.Tk()
        GPIO.output(gpi1, True)
        imageLoad = Image.open(image)
        imageResize = imageLoad.resize((window.winfo_screenwidth(), window.winfo_screenheight()))
        imagePrint = ImageTk.PhotoImage(imageResize)
        fondo = tk.Label(window, image=imagePrint).place(x=0, y=0)
        window.attributes('-fullscreen', True)
        print("tamaño de la pantalla: ", window.winfo_screenwidth(), window.winfo_screenheight())
        mixer.init()
        mixer.music.load(command)
        mixer.music.play()
        window.after(3000, window.destroy)
        window.mainloop()
        time.sleep(3)
        GPIO.output(gpi1, False)


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
    
    def turn_off(green_pin, red_pin):
        GPIO.output(green_pin, False)
        GPIO.output(red_pin, False)
        

    def initRaspberry():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(29, GPIO.OUT)
        GPIO.setup(33, GPIO.OUT)
        GPIO.output(29, False)
        GPIO.output(33, False)

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
                find_request_validate = "https://us-central1-scanner-mevacuno.cloudfunctions.net/neogcscanner"
                response_file_validate = connetVacuno.requestPost(find_request_validate, payloadNeo, headersNeo)
                dataJsonNeo = json.loads(response_file_validate.content.decode("utf-8"))
                status = dataJsonNeo.get('result').get('payload').get('global_status')
                print(status)
                if status == "green":
                    openWindow.openWindow("green",
                                          FullScreenApp.path_base_audio.format("pm_valido.mp3"), 29,
                                          FullScreenApp.path_base_image.format("movilidad-valido.png"))
                else:
                    openWindow.openWindow("red",
                                          FullScreenApp.path_base_audio.format("pm_invalido.mp3"), 33,
                                          FullScreenApp.path_base_image.format("movilidad-invalido.png"))

            except:
                openWindow.openWindow("red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33,
                                      FullScreenApp.path_base_image.format("error-validacion.png"))
                FullScreenApp.turn_off(29,33)


        elif parsed.netloc=="cmv.interior.gob.cl":
            try:
                openWindow.openWindow("red",
                                      FullScreenApp.path_base_audio.format("puc_novalido.mp3"), 33,
                                      FullScreenApp.path_base_image.format("pase-colectivo.png"))
            except:
                openWindow.openWindow("red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33,
                                      FullScreenApp.path_base_image.format("pase-colectivo.png"))
                FullScreenApp.turn_off(29,33)

        else:
            try:
                date2 = urlparse.parse_qs(parsed.query)['date'][0]
                date = datetime.strptime(date2, "%Y/%m/%d")
                # print(date2)
                # print(date)
                # print(datetime.today().date())
                if date.date() == datetime.today().date():
                    openWindow.openWindow("green",
                                          FullScreenApp.path_base_audio.format("pcv_valido.mp3"), 29,
                                          FullScreenApp.path_base_image.format("comisaria-valido.png"))
                else:
                    openWindow.openWindow("red",
                                          FullScreenApp.path_base_audio.format("pcv_invalido.mp3"), 33,
                                          FullScreenApp.path_base_image.format("comisaria-invalido.png"))

            except:
                openWindow.openWindow("red",
                                      FullScreenApp.path_base_audio.format("err_validacion.mp3"), 33,
                                      FullScreenApp.path_base_image.format("error-validacion.png"))
                FullScreenApp.turn_off(29,33)

    def readSerialOne(Thread):
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=0)
        conn_vacuno = ConnectSite()
        open_window = OpenWindow()
        while True:
            line = ser.readline().decode()
            if len(line) > 0:
                print(line)
                FullScreenApp.validateUrl(line, conn_vacuno, open_window)
                time.sleep(0.1)

    try:
        _thread.start_new_thread(readSerialOne, ("QR-1",))
    except:
        print("Error: unable to start thread")

FullScreenApp.initRaspberry()

while 1:
    pass
