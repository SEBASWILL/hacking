
import pyperclip
import time

while True: 
    contenido_portapapeles = pyperclip.paste()  
    if contenido_portapapeles != '' : 
        print(contenido_portapapeles) 
    time.sleep(8)