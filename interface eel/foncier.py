# coding:utf-8

import eel
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename

eel.init('interface')

# @eel.expose
# def test(parametre):
#     print("Voila le text :", parametre)
#     return'It seems to work'

@eel.expose
def selectionDossier():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askdirectory()
    #root.withdraw()
    root.destroy()
    print("dossier séléctionné : {}").format(choix_du_dossier)
    return choix_du_dossier

@eel.expose
def selectionBDgpkg():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askopenfilename(title="Sélectionner la Base de donnée", filetypes=[("geopackage files", "*.gpkg")])
    root.withdraw()
    root.destroy()
    print("dossier séléctionné : {}").format(choix_du_dossier)
    return choix_du_dossier


### TODO: Fonction pour lister les données du dossier ou du Geopackage dans le div dédié!
@eel.expose
def liste_data(chemin):


if __name__ == "__main__":
    eel.init('interface')
    eel.start('index2.html', size=(800, 600))
