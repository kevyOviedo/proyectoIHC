import tkinter as tk
import eyetracker
import threading

running = False
thread = None

def correr_eyetracker():
    for data in eyetracker.correr_eyetracker(lambda:running):
        print("datos:", data)
        if not running:
            break

def activar_eyetracker():
    global running, thread, start_button
    if not running:
        running = True
        start_button.config(text="Stop")
        thread = threading.Thread(target=correr_eyetracker, daemon=True)
        thread.start()
    else:
        running = False
        start_button.config(text="Start")

root = tk.Tk()
root.title("Ayudador de Lectura")
root.geometry("200x100") 

start_button = tk.Button(root, text="Start", command=activar_eyetracker)
start_button.pack(expand=True)

# Start the GUI event loop
root.mainloop()