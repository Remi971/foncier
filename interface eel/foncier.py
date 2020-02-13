# coding:utf-8

import eel
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
from fiona import listlayers

eel.init('interface')

# @eel.expose
# def test(parametre):
#     print("Voila le text :", parametre)
#     return'It seems to work'

## TODO: Fusionner les deux fonctions en une seule!!
@eel.expose
def selectionDossier():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askdirectory()
    #root.withdraw()
    root.destroy()
    print('Dossier séléctionné : ', choix_du_dossier)
    return choix_du_dossier

@eel.expose
def selectionBDgpkg():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askopenfilename(title="Sélectionner la Base de donnée", filetypes=[("geopackage files", "*.gpkg")])
    root.withdraw()
    root.destroy()
    print("dossier séléctionné : ", choix_du_dossier)
    return choix_du_dossier



@eel.expose
def liste_data(chemin):
    '''Liste les données comprises dans le dossier ou le fichier correspondant au chemin indiqué'''
    donnee = []
    def ajoutShape(file):
        if file.endswith('.shp'):
            donnee.append(file)

    if chemin.endswith('.gpkg'):
        for layerName in listlayers(chemin):
            donnee.append(layerName)
        print(donnee)
    else:
        for folderName, subfolders, filenames in os.walk(chemin):
            ajoutShape(folderName)

            for subfolder in subfolders:
                ajoutShape(subfolder)

            for filename in filenames:
                ajoutShape(filename)
    return donnee


if __name__ == "__main__":
    eel.init('interface')
    eel.start('index2.html', size=(1000, 600))
