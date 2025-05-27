import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import threading
import random

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Sistema de Monitoreo de Atención Visual")
ventana.geometry("950x700")
ventana.configure(bg="#e8edf1")  # Fondo más profesional

# Variable para forma del overlay
forma_overlay = tk.StringVar(master=ventana, value="círculo")

# Estado del monitoreo
monitoreando = False

# Estilo visual profesional
style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", font=('Segoe UI', 11, 'bold'), padding=10)
style.configure("TButton", font=('Segoe UI', 10), background="#1f2937", foreground="white")
style.map("TButton", background=[("active", "#111827")])
style.configure("TLabel", font=('Segoe UI', 10), background="#e8edf1")
style.configure("Inicio.TFrame", background="#e8edf1")
style.configure("Control.TFrame", background="#f0f2f5")
style.configure("Visual.TFrame", background="#ffffff")

# Crear pestañas
tabControl = ttk.Notebook(ventana)
tab_inicio = ttk.Frame(tabControl, style="Inicio.TFrame")
tab_control = ttk.Frame(tabControl, style="Control.TFrame")
tab_visual = ttk.Frame(tabControl, style="Visual.TFrame")

for i, tab in enumerate([tab_inicio, tab_control, tab_visual]):
    tabControl.add(tab, text=['Inicio', 'Control', 'Visualización'][i])
tabControl.pack(expand=1, fill="both")


################
###################3
###################3
###############3
#######################

# ========== Pestaña 1: Inicio ==========
frame_inicio = ttk.Frame(tab_inicio, padding=30, style="Inicio.TFrame")
frame_inicio.pack(fill=tk.BOTH, expand=True)

bienvenida = ttk.Label(frame_inicio, text="Bienvenido al sistema de monitoreo de atención visual.", font=('Segoe UI', 16, 'bold'))
bienvenida.pack(pady=15)

instrucciones = (
    "Este sistema utiliza un eyetracker para detectar si el usuario se encuentra distraído.\n\n"
    "Características principales:\n"
    "• Detección automática de distracciones.\n"
    "• Alertas visuales y auditivas.\n"
    "• Selección de forma del indicador en pantalla.\n"
    "• Visualización en tiempo real del punto de atención.\n"
    "\nAccede a estas funciones desde las pestañas superiores."
)
texto_instrucciones = ttk.Label(frame_inicio, text=instrucciones, font=('Segoe UI', 11), justify=tk.LEFT)
texto_instrucciones.pack(pady=10)

comandos = (
    "Comandos disponibles:\n\n"
    "Ctrl + Alt + 2 .......... Iniciar / Detener monitoreo\n"
    "Click en alerta .......... Detener sonido / cerrar alerta\n"
    "Botón 'Iniciar Monitoreo' ....... Comienza seguimiento de mirada\n"
    "Botón 'Generar Reporte Visual' .... Muestra mapa de calor\n"
    "Selección de forma .... Cambia entre círculo y rectángulo"
)
texto_comandos = ttk.Label(frame_inicio, text=comandos, font=('Segoe UI', 10), justify=tk.LEFT, foreground="#333")
texto_comandos.pack(pady=(20, 10))

# ========== Pestaña 2: Control ==========
frame_control = ttk.Frame(tab_control, padding=30, style="Control.TFrame")
frame_control.pack(fill=tk.BOTH, expand=True)

estado_label = ttk.Label(frame_control, text="Estado: Inactivo", font=('Segoe UI', 11, 'bold'))
estado_label.pack(pady=10)

def alternar_monitoreo():
    global monitoreando
    monitoreando = not monitoreando
    estado_label.config(text=f"Estado: {'Monitoreando' if monitoreando else 'Inactivo'}")
    if monitoreando:
        threading.Thread(target=simular_monitoreo, daemon=True).start()

def generar_alerta():
    winsound.Beep(1000, 500)
    messagebox.showwarning("Alerta", "¡Usuario distraído!")

def simular_monitoreo():
    tiempo_distraccion = 0
    while monitoreando:
        atencion = random.choice([True] * 9 + [False])
        if not atencion:
            tiempo_distraccion += 1
        else:
            tiempo_distraccion = 0
        if tiempo_distraccion >= 5:
            generar_alerta()
            tiempo_distraccion = 0
        ventana.after(500)

boton_monitoreo = ttk.Button(frame_control, text="Iniciar / Detener Monitoreo", command=alternar_monitoreo)
boton_monitoreo.pack(pady=20)

forma_label = ttk.Label(frame_control, text="Forma del indicador en pantalla:", font=('Segoe UI', 10, 'bold'))
forma_label.pack(pady=(30, 10))
forma_frame = ttk.Frame(frame_control, style="Control.TFrame")
forma_frame.pack()
ttk.Radiobutton(forma_frame, text="Círculo", variable=forma_overlay, value="círculo").pack(side=tk.LEFT, padx=10)
ttk.Radiobutton(forma_frame, text="Rectángulo", variable=forma_overlay, value="rectángulo").pack(side=tk.LEFT, padx=10)

# ========== Pestaña 3: Visualización ==========
frame_visual = ttk.Frame(tab_visual, padding=10, style="Visual.TFrame")
frame_visual.pack(fill=tk.BOTH, expand=True)

overlay_canvas = tk.Canvas(frame_visual, bg="#ffffff")
overlay_canvas.pack(fill=tk.BOTH, expand=True)

def actualizar_overlay(x, y):
    overlay_canvas.delete("all")
    if x != -1:
        screen_x = x * 900
        screen_y = y * 650
        if forma_overlay.get() == "círculo":
            overlay_canvas.create_oval(
                screen_x - 10, screen_y - 10,
                screen_x + 10, screen_y + 10,
                fill='#0078D4', outline=''
            )
        else:
            overlay_canvas.create_rectangle(
                screen_x - 10, screen_y - 10,
                screen_x + 10, screen_y + 10,
                fill='#0078D4', outline=''
            )

ventana.mainloop()