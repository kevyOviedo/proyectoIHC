import tkinter as tk
import eyetracker
import threading
from PIL import Image, ImageTk
import pygame
import filtro
import sys
from PyQt5 import QtWidgets, QtCore

qt_overlay = None
qt_app = None


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

    img = Image.open("character.png").resize((240, 240))
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

def activar_eyetracker(event=None):
    global running, thread, start_button, qt_overlay, qt_app
    if not running:
        running = True
        start_button.config(text="Stop")

        qt_thread = threading.Thread(target=run_qt_overlay, daemon=True)
        qt_thread.start()

        thread = threading.Thread(target=correr_eyetracker, daemon=True)
        thread.start()
    else:
        running = False
        start_button.config(text="Start")

        stop_qt_overlay()

root = tk.Tk()
root.title("Ayudador de Lectura")
root.geometry("250x100") 

start_button = tk.Button(root, text="Start", command=activar_eyetracker)

start_button.pack(expand=True)

# Start the GUI event loop
root.mainloop()