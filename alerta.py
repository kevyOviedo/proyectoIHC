import tkinter as tk
from PIL import Image, ImageTk
import threading
import pygame

def play_sound_loop():
    pygame.mixer.init()
    pygame.mixer.music.load("sonido.wav")  # cargar audio
    pygame.mixer.music.play(-1)  # loop infinito

image_path = "character.png"      
dialogue_text = "ESTO ES UN TEXTO"  
position_x = 500  
position_y = 200  

root = tk.Tk()
root.overrideredirect(True) 
root.attributes("-topmost", True) 
root.geometry(f"+{position_x}+{position_y}") 


img = Image.open(image_path)
img = img.resize((240, 240)) 
tk_img = ImageTk.PhotoImage(img)

canvas = tk.Canvas(root, width=250, height=250, highlightthickness=0, bg="yellow")
canvas.pack()

canvas.create_image(8, 20, anchor="nw", image=tk_img)

#Hace sonido
threading.Thread(target=play_sound_loop, daemon=True).start()

canvas.create_text(125, 25, text=dialogue_text, font=("Arial", 12))

def close_app(event):
    root.destroy()

canvas.bind("<Button-1>", close_app)

root.mainloop()