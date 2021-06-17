import http.client
import requests
import tk as tk
from datetime import datetime
import http.client
import json
import urllib.parse as urlparse
import tkinter as tk

from circuit_breaker import circuit_breaker




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




if __name__ == '__main__':

    connetVacuno = ConnectSite("www.googleapis.com")

    def __init__(self, master, **kwargs):
        self.master = master
        pad = 3
        self._geom = '200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - pad, master.winfo_screenheight() - pad))
        master.bind('<Escape>', self.toggle_geom)

    def toggle_geom(self, event):
        geom = self.master.winfo_geometry()
        print(geom, self._geom)
        self.master.geometry(self._geom)
        self._geom = geom

    def validateUrl(url):
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
                    print("veamosssss")

                else:
                    print("fallo")

            except:
                status = "Algo Salio Mal - Favor Acercarse al Guardia"
                print(status)
        else:
            try:
                date2 = urlparse.parse_qs(parsed.query)['date'][0]
                date = datetime.strptime(date2, "%Y/%m/%d")
                if date.date() == datetime.today().date():
                    print("Todo OK - Bienvenido")
                else:
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
            except:
                status = "Algo Salio Mal - Favor Acercarse al Guardia"
                print(status)
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


    findurl = "https://scanmevacuno.gob.cl/?a=109355338&b=1614219941&c=0"
    validateUrl(findurl)



