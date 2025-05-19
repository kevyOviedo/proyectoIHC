import tkinter as tk
import eyetracker
import threading
from PIL import Image, ImageTk
import pygame
import filtro
import sys
from PyQt5 import QtWidgets, QtCore
import keyboard
import time

qt_overlay = None
qt_app = None

timer_inicio = None
tiempo_total = 0

running = False
thread = None
alerta_ventana=None

def run_qt_overlay():
    global qt_overlay, qt_app
    qt_app = QtWidgets.QApplication(sys.argv)
    qt_overlay = filtro.StaticOverlay()
    qt_overlay.showFullScreen()
    qt_app.exec_()



def hacer_alerta():

    global alerta_ventana

    if alerta_ventana is not None:
        return
    
    alerta_ventana = tk.Toplevel()
    alerta_ventana.overrideredirect(True)
    alerta_ventana.attributes("-topmost", True)
    alerta_ventana.geometry("+850+200")

    img = Image.open("mono.png").resize((240, 240))
    tk_img = ImageTk.PhotoImage(img)

    canvas = tk.Canvas(alerta_ventana, width=250, height=250, highlightthickness=0, bg="yellow")
    canvas.pack()

    canvas.create_image(8, 20, anchor="nw", image=tk_img)
    canvas.image = tk_img 

    canvas.create_text(125, 25, text="ESTO ES UN TEXTO", font=("Arial", 12))

    def play_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("sonido.wav")
        pygame.mixer.music.play(-1)

    threading.Thread(target=play_sound, daemon=True).start()

    def close_app(event=None):

        global alerta_ventana
        if alerta_ventana:
            alerta_ventana.destroy()
            alerta_ventana=None
            pygame.mixer.music.stop()


    canvas.bind("<Button-1>", close_app)

def cerrar_alerta():
    if alerta_ventana:
        alerta_ventana.after(0, alerta_ventana.destroy)
        pygame.mixer.music.stop()
        globals()['alerta_ventana'] = None

def stop_qt_overlay():
    global qt_overlay, qt_app
    if qt_overlay:
        QtCore.QMetaObject.invokeMethod(qt_overlay, "close", QtCore.Qt.QueuedConnection)
    if qt_app:
        QtCore.QMetaObject.invokeMethod(qt_app, "quit", QtCore.Qt.QueuedConnection)

def correr_eyetracker():
    flag = None
    for data in eyetracker.correr_eyetracker(lambda:running):
        print("datos:", data)
        

        if qt_overlay:
            QtCore.QMetaObject.invokeMethod(
                qt_overlay, "update_eye_pos",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(float, data[0]),
                QtCore.Q_ARG(float, data[1])
            )    


        if (data[0] == -1 or data[0]<20 or data[0]>1900) and flag != 1:
            root.after(0, hacer_alerta)
            flag=1

        elif ((data[0]>=20 and data[0]<=1900)) and flag !=0:
            root.after(0, cerrar_alerta)
            flag=0


        if not running:
            break

##############################################################

def activar_eyetracker(event=None):
    global running, thread, start_button, qt_overlay, qt_app, timer_inicio, tiempo_total
    if not running:
        running = True
        start_button.config(text="Stop", bg="red")
        timer_inicio = time.time() #empieza timer

        qt_thread = threading.Thread(target=run_qt_overlay, daemon=True)
        qt_thread.start()

        thread = threading.Thread(target=correr_eyetracker, daemon=True)
        thread.start()
    else:
        running = False
        start_button.config(text="Start", bg="green")

        tiempo_transcurrido = time.time() - timer_inicio if timer_inicio else 0
        tiempo_total = tiempo_total + tiempo_transcurrido
        
        t=int(tiempo_transcurrido)
        m = t//60
        s = t % 60 
        tiempo_reciente.config(text=f"Duracion de la mas reciente sesion = {m}:{s}")
        
        t=int(tiempo_total)
        m = t//60
        s = t % 60 
        tiempo_total_texto.config(text=f"Tiempo total de lectura =  {m}:{s}")

        stop_qt_overlay()

def listen_global_hotkey():
    keyboard.add_hotkey('ctrl+alt+2', lambda: root.after(0, activar_eyetracker))
    keyboard.wait()  

hotkey_thread = threading.Thread(target=listen_global_hotkey, daemon=True)
hotkey_thread.start()


## AQUI TKINTER
root = tk.Tk() # Inicializar ventana tkinter
root.title("Ayudador de Lectura") # Nombre de ventana
root.geometry("450x450")  # tamaño de ventana

# Boton para activar/desactivar el eyetracker
start_button = tk.Button(root, text="Start", command=activar_eyetracker, bg="green")
start_button.pack(pady=(50, 10))

# Texto 1
tiempo_reciente = tk.Label(root, text="Duracion de la mas reciente sesion = ...")
tiempo_reciente.pack()

# Texto del tiempo (se actualiza despues de usar el eyetracker)
tiempo_total_texto = tk.Label(root,text="Tiempo total de lectura = ...")
tiempo_total_texto.pack(pady=(10, 10))

root.mainloop()