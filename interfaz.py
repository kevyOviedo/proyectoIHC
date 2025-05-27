import tkinter as tk
from tkinter import *
from tkinter import ttk
import eyetracker
import threading
from PIL import Image, ImageTk
import pygame
import filtro
import sys
from PyQt5 import QtWidgets, QtCore
import keyboard
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy.ndimage import gaussian_filter

matplotlib.use('TkAgg')

datos_eyetracker_x = []
datos_eyetracker_y = []
sin_mirar = 0

qt_overlay = None
qt_app = None

timer_inicio = None
tiempo_total = 0

running = False
thread = None
alerta_ventana=None
comando_ventana=None

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

    canvas.create_text(125, 25, text="!!!!!!!!!!!", font=("Arial", 12))

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
        print("cerrando overlay")
        QtCore.QMetaObject.invokeMethod(qt_overlay, "close", QtCore.Qt.QueuedConnection)
    if qt_app:
        print("cerrando QT APP")
        QtCore.QMetaObject.invokeMethod(qt_app, "quit", QtCore.Qt.QueuedConnection)


def mostrar_comando():

    global comando_ventana

    if comando_ventana is not None:
        return

    comando_ventana = tk.Toplevel()
    comando_ventana.overrideredirect(True)
    comando_ventana.attributes("-topmost", True)
    comando_ventana.geometry("+1500+100")

    canvas = tk.Canvas(comando_ventana, width=250, height=50, highlightthickness=0, bg="red")
    canvas.pack()

    canvas.create_text(125, 25, text="Desactivar:\nCtrl+Alt+2", font=("Arial", 12))

    def close_app1(event=None):

        global comando_ventana
        if comando_ventana:
            comando_ventana.destroy()
            comando_ventana=None


    canvas.bind("<Button-1>", close_app1)

def cerrar_comando():
    if comando_ventana:
        comando_ventana.after(0, comando_ventana.destroy)
        globals()['comando_ventana'] = None

def correr_eyetracker():
    global datos_eyetracker_x
    global datos_eyetracker_y
    global sin_mirar
    flag = None
    for data in eyetracker.correr_eyetracker(lambda:running):
        print("datos:", data)
        
        if(data[0]!=-1):
            datos_eyetracker_x.append(data[0])
            datos_eyetracker_y.append(data[1])
        else:
            sin_mirar = sin_mirar+1

        if qt_overlay:
            QtCore.QMetaObject.invokeMethod(
                qt_overlay, "update_eye_pos",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(float, data[0]),
                QtCore.Q_ARG(float, data[1])
            )

            

        root.after(0, mostrar_comando)

        if ( data[0]<20 or data[0]>1900) and flag != 1:
            root.after(0, hacer_alerta)
            flag=1

        elif ((data[0]>=20 and data[0]<=1900)) and flag !=0:
            root.after(0, cerrar_alerta)
            flag=0


        if not running:
            root.after(0,cerrar_comando)
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
        root.after(0,cerrar_comando)
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
        root.after(0,cerrar_comando)

def listen_hotkey():
    keyboard.add_hotkey('ctrl+alt+2', lambda: root.after(0, activar_eyetracker))
    keyboard.wait()  

def graficar():
    global datos_eyetracker_x, datos_eyetracker_y, sin_mirar
    gaze_x = datos_eyetracker_x
    gaze_y = datos_eyetracker_y

    porcentaje_sin_mirar = sin_mirar/(sin_mirar+len(datos_eyetracker_x))
    tiempo_sin_mirar = (tiempo_total*porcentaje_sin_mirar)/100

    screen_width = 1920
    screen_height = 1080

    heatmap, xedges, yedges = np.histogram2d(gaze_x, gaze_y, bins=[192, 108], range=[[0, screen_width], [0, screen_height]])

    heatmap = gaussian_filter(heatmap, sigma=3)

    plt.imshow(
        heatmap.T,        
        origin='lower',   
        cmap='jet',       
        extent=[0, screen_width, 0, screen_height]
    )
    plt.title('Heatmap eyetracking')
    
    #s_no = int(tiempo_sin_mirar) % 60
    #m_no = int(tiempo_sin_mirar) // 60
    #s_t = int(tiempo_total) % 60
    #m_t = int(tiempo_total) // 60
    plt.xlabel(f'Miraste la pantalla un {100-tiempo_sin_mirar}% del tiempo')
    plt.show()

def hacerGrafica():
    global datos_eyetracker_x, datos_eyetracker_y
    if len(datos_eyetracker_x) > 1:
        texto_grafica.config(text="")
        graficar()
    else:
        texto_grafica.config(text=f"No hay datos para graficar!")
        

hotkey_thread = threading.Thread(target=listen_hotkey, daemon=True)
hotkey_thread.start()


## AQUI TKINTER
root = tk.Tk() # Inicializar ventana tkinter
root.title("Ayudador de Lectura") # Nombre de ventana
root.geometry("550x550")  # tamaño de ventana
root.configure(bg="#e8edf1") 

# Estilo visual profesional
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", font=('Segoe UI', 11, 'bold'), padding=10)
style.configure("TButton", font=('Segoe UI', 10), background="#1f2937", foreground="white")
style.map("TButton", background=[("active", "#111827")])
style.configure("TLabel", font=('Segoe UI', 10), background="#e8edf1")
style.configure("Info.TFrame", background="#e8edf1")
style.configure("Main.TFrame", background="#f0f2f5")
style.configure("Datos.TFrame", background="#ffffff")
#######

## para tabs
tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl, style="Info.TFrame")
tab2 = ttk.Frame(tabControl, style="Main.TFrame")
tab3 = ttk.Frame(tabControl, style="Datos.TFrame")

tabControl.add(tab1, text='Info')
tabControl.add(tab2, text='Main')
tabControl.add(tab3, text='Datos')

tabControl.pack(expand=1, fill="both")

###
# TAB 1
###
frame_info = ttk.Frame(tab1, padding=15, style="Info.TFrame")
frame_info.pack(fill=tk.BOTH, expand=True)

bienvenida = ttk.Label(frame_info, text="Bienvenido al ayudador de lectura", font=('Segoe UI', 12, 'bold'))
bienvenida.pack(pady=5)

instrucciones = (
    "Este sistema utiliza un eyetracker para detectar si el usuario se encuentra \ndistraído mientras lee.\n\n"
    "Instrucciones:\n"
    "• Abre un documento pdf o material de lectura.\n"
    "• Ajustar el material de lectura para que quede en el centro.\n"
    "• Mover esta ventana para que no bloquee el texto.\n"
    "• Ajusta tu camara al nivel de tus ojos.\n"
    "• Activar el programa desde la tab Main.\n"
    "• Al salir una alerta, debes ajustar la posición de tu cabeza o camara.\n"
)
texto_instrucciones = ttk.Label(frame_info, text=instrucciones, font=('Segoe UI', 8), justify=tk.LEFT)
texto_instrucciones.pack(pady=2)

notas_adicionales = (
    "Notas adicionales:\n\n"
    "1. Puedes visualizar resultados de tu lectura en la tab Datos.\n"
    "2. Se puede seguir utilizando el mouse y teclado \n"
    '3. Programa puede ser activado y desactivado con "Ctrl+Alt+2" \n'
)
notas_adicionales = ttk.Label(frame_info, text=notas_adicionales, font=('Segoe UI', 8), justify=tk.CENTER, foreground="#333")
notas_adicionales.pack(pady=1)

###
# TAB 2
###

frame_main = ttk.Frame(tab2, padding=10, style="Main.TFrame")
frame_main.pack(fill=tk.BOTH, expand=True)

# Boton para activar/desactivar el eyetracker
start_button = tk.Button(frame_main, text="Start", command=activar_eyetracker, bg="green")
start_button.pack(pady=(20, 10))
# Texto 1
tiempo_reciente = tk.Label(frame_main, text="Duracion de la más reciente sesion = ...")
tiempo_reciente.pack()
# Texto del tiempo (se actualiza despues de usar el eyetracker)
tiempo_total_texto = tk.Label(frame_main,text="Tiempo total de lectura = ...")
tiempo_total_texto.pack(pady=(10, 10))

###
# TAB 3
###
frame_datos = ttk.Frame(tab3, padding=10, style="Datos.TFrame")
frame_datos.pack(fill=tk.BOTH, expand=True)

button_grafica = Button(frame_datos, text="Graficar", command=hacerGrafica)
button_grafica.pack(pady=(50, 10))

texto_grafica = tk.Label(frame_datos, text="")
texto_grafica.pack()

root.mainloop()
if qt_overlay:
    QtCore.QMetaObject.invokeMethod(qt_overlay, "close", QtCore.Qt.QueuedConnection)
if qt_app:
    QtCore.QMetaObject.invokeMethod(qt_app, "quit", QtCore.Qt.QueuedConnection)