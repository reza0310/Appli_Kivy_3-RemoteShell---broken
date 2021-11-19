from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.graphics import Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color

import threading
import socket
import select
import os


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


__author__ = "reza0310"
HEADER_LENGTH = 10
layout = []
IP = get_ip()  # "192.168.1.97"
PORT = 88

os.sep = "/"
dc = ''


def recomposer_path(pseudopath):
    path = ""
    for x in pseudopath:
        path += x + os.sep
    return path[:-len(os.sep)]


def receive_message(client_socket):
    try:
        # Receive our "header" containing message length, it's size is defined and constant
        message_header = client_socket.recv(HEADER_LENGTH)
        # If we received no data, client gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            print("Ho no...")
            return False
        print("Header:", message_header)
        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())
        # Return an object of message header and message data
        data = client_socket.recv(message_length)
        return {'header': message_header, 'data': data}
    except Exception as e:
        print("Error:", e)
        print(client_socket.recv(100))
        # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
        # or just lost his connection
        # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
        # and that's also a cause when we receive an empty message
        return False


def envoyer(fichier, client_socket):
    message = fichier.split(os.sep)[-1].encode('utf-8')
    client_socket.send(message)
    a = client_socket.recv(2).decode('utf-8')
    if not a == "ok":
        print("Erreur")
    taille = os.path.getsize(fichier)
    message = str(taille).encode('utf-8')
    client_socket.send(message)
    a = client_socket.recv(2).decode('utf-8')
    if not a == "ok":
        print("Erreur")
    num = 1
    with open(fichier, "rb") as f:
        while num <= taille:
            if taille-num > 10000000:
                octet = f.read(10000000)
                client_socket.send(octet)
                num += 10000000
            elif taille-num > 1000000:
                octet = f.read(1000000)
                client_socket.send(octet)
                num += 1000000
            elif taille-num > 100000:
                octet = f.read(100000)
                client_socket.send(octet)
                num += 100000
            elif taille-num > 10000:
                octet = f.read(10000)
                client_socket.send(octet)
                num += 10000
            elif taille - num > 1000:
                octet = f.read(1000)
                client_socket.send(octet)
                num += 1000
            elif taille-num > 100:
                octet = f.read(100)
                client_socket.send(octet)
                num += 100
            else:
                octet = f.read(1)
                client_socket.send(octet)
                num += 1
            print("Paquet numéro", num - 1, "/", taille, "envoyé. Progression:", str(((num - 1) / taille) * 100), "%")
            a = client_socket.recv(2).decode('utf-8')
            if not a == "ok":
                print("Erreur")


def envoyer_dossier(path_env, client_socket):
    fichiers = [x for x in os.listdir(path_env) if os.path.isfile(path_env+os.sep+x)]
    print(fichiers)
    nbre_de_fichiers = str(len(fichiers))
    message = nbre_de_fichiers.encode('utf-8')
    client_socket.send(message)
    a = client_socket.recv(2).decode('utf-8')
    if a != "ok":
        print("Erreur")
    i = 0
    for nom_fichier in fichiers:
        i += 1
        message = nom_fichier.encode('utf-8')
        client_socket.send(message)
        a = client_socket.recv(2).decode('utf-8')
        if not a == "ok":
            print("Erreur")
        fichier = path_env+"\\"+nom_fichier
        taille = os.path.getsize(fichier)
        message = str(taille).encode('utf-8')
        client_socket.send(message)
        a = client_socket.recv(2).decode('utf-8')
        if not a == "ok":
            print("Erreur")
        num = 1
        with open(fichier, "rb") as f:
            while num <= taille:
                if taille-num > 10000000:
                    octet = f.read(10000000)
                    client_socket.send(octet)
                    num += 10000000
                elif taille-num > 1000000:
                    octet = f.read(1000000)
                    client_socket.send(octet)
                    num += 1000000
                elif taille-num > 100000:
                    octet = f.read(100000)
                    client_socket.send(octet)
                    num += 100000
                elif taille-num > 10000:
                    octet = f.read(10000)
                    client_socket.send(octet)
                    num += 10000
                elif taille - num > 1000:
                    octet = f.read(1000)
                    client_socket.send(octet)
                    num += 1000
                elif taille-num > 100:
                    octet = f.read(100)
                    client_socket.send(octet)
                    num += 100
                else:
                    octet = f.read(1)
                    client_socket.send(octet)
                    num += 1
                print("Fichier numéro",i,"sur",nbre_de_fichiers,". Paquet numéro", num - 1, "/", taille, "envoyé. Progression:", str(((num - 1) / taille) * 100), "%")
                a = client_socket.recv(2).decode('utf-8')
                if not a == "ok":
                    print("Erreur")


def traiter(requete):
    global dc
    requete = requete.split(" ")
    if requete[0] == "get":
        return str(recomposer_path(jeu.path))
    elif requete[0] == "ls":
        dc = "ls"
        return str(os.listdir(recomposer_path(jeu.path)))
    elif requete[0] == "cd" and len(requete) == 2:
        dc = "cd"
        if requete[1] == "..":
            print(jeu.path)
            jeu.path.pop()
            return "fait"
        else:
            try:
                os.listdir(recomposer_path(jeu.path+[requete[1]]))
                jeu.path.append(requete[1])
                return "fait"
            except Exception as e:
                return str(e)
    elif requete[0] == "dl" and len(requete) == 2:
        dc = "dl"
        return "Envoi de "+requete[1], requete[1]
    else:
        return "Mauvaise requête"


class HUD:

    def __init__(self):
        self.longueur, self.largeur = Window.size
        self.boutons = []

    def bind(self, emplacement, taille, action, type="Bouton"):
        print("Binding",action,'sur x variant de',(emplacement[0]-(taille[0]//2), emplacement[0]+(taille[0]//2)),'et y',(emplacement[1]-(taille[1]//2), emplacement[1]+(taille[1]//2)))
        self.boutons.append({"type": type, "x": (emplacement[0]-(taille[0]//2), emplacement[0]+(taille[0]//2)), "y": (emplacement[1]-(taille[1]//2), emplacement[1]+(taille[1]//2)), "action": action})

    def unbind(self, unbin="all"):
        if unbin == 'all':
            self.boutons = []
        else:
            for bouton in self.boutons:
                if bouton["action"] == unbin:
                    self.boutons.remove(bouton)

    def press(self, touch):
        for bouton in self.boutons:
            if bouton["x"][0] < touch.spos[0]*1000 < bouton["x"][1] and bouton["y"][0] < touch.spos[1]*1000 < bouton["y"][1]:
                print("Action:", bouton["action"])
                eval(bouton["action"])  # Handle joysticks

    def recoordonner(self, tupl):
        return int((tupl[0] / 1000) * self.longueur), int((tupl[1] / 1000) * self.largeur)

    def recoordonner_double(self, tupl):
        return int((tupl[0] / 1000) * self.longueur), int((tupl[1] / 1000) * self.largeur), int((tupl[2] / 1000) * self.longueur), int((tupl[3] / 1000) * self.largeur)

    def texte(self, x, y, texte, remove = True):
        label = CoreLabel(text=str(texte), font_size=20)
        label.refresh()
        text = label.texture
        rec = Rectangle(size=text.size, pos=self.recoordonner((x - (text.size[0]//2), y - (text.size[1]//2))), texture=text)
        layout.canvas.add(rec)
        if remove:
            def rmv(dt):
                layout.canvas.remove(rec)
            Clock.schedule_once(rmv, 1/30)

    def actualiser(self, dt):
        self.longueur, self.largeur = Window.size


class JEU:

    def initialiser(self):
        # Initialisation du serveur
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.clients = {}


        # Initialisation de l'app
        self.path = os.path.dirname(__file__).split(os.sep)
        print(self.path)


        # Initialisation de la fonction actualiser
        self.event = Clock.schedule_interval(self.actualiser, 1/0.5)  # 60 fps
        self.event = Clock.schedule_interval(self.afficher, 1/30)  # 60 fps

    def actualiser(self, dt):
        # Serveur:
        thread = threading.Thread(target=self.serveur)
        thread.start()
        thread.join()

    def afficher(self, dt):
        # Affichage:
        if len(self.clients) == 0:
            hud.texte(500, 540, "IP: "+IP)
            hud.texte(500, 500, "En attente de connexion")
        else:
            hud.texte(500, 540, "IP: "+IP)
            hud.texte(500, 500, "Connecté")
            hud.texte(500, 460, "Path actuel: "+str(recomposer_path(jeu.path)))
            hud.texte(500, 420, "Dernière commande: "+dc)

    def serveur(self):
        envoye = False
        read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                client_socket, client_address = self.server_socket.accept()
                self.sockets_list.append(client_socket)
                self.clients[client_socket] = {'header': len(client_address), 'adresse': client_address}
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print('Closed connection from: {}'.format(self.clients[notified_socket]['adresse']))
                    self.sockets_list.remove(notified_socket)
                    del self.clients[notified_socket]
                    continue

                user = self.clients[notified_socket]
                print("User:", user)
                reponse = traiter(message["data"].decode("utf-8"))
                if len(reponse) == 2:
                    envoye = True
                    reponses = reponse[0].encode('utf-8')
                else:
                    reponses = reponse.encode('utf-8')
                message_header = f"{len(reponses):<{HEADER_LENGTH}}".encode('utf-8')
                notified_socket.send(message_header + reponses)
                if envoye:
                    print(reponse)
                    if reponse[1] == "file":
                        envoyer_dossier(recomposer_path(self.path), notified_socket)
                    else:
                        envoyer(recomposer_path(self.path)+os.sep+reponse[1], notified_socket)


hud = HUD()
jeu = JEU()


class Layout(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def add_entity(self, entity):
        self.entities.add(entity)
        self.canvas.add(entity.image)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)
            self.canvas.remove(entity.image)

    def on_touch_down(self, touch):
        hud.press(touch)


class RemoteShellApp(App):
    def build(self):
        global layout
        Window.clearcolor = (0, 0, 0, 1)
        self.title = 'RemoteShell'
        layout = Layout()
        jeu.initialiser()
        return layout


RemoteShellApp().run()