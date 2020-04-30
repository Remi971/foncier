# coding:utf-8

import eel
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
from fiona import listlayers
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import warnings
from source import clean_data, coeffEmpriseSol, selectionParcelles, test_emprise_vide, test_emprise_batie, routeDesserte, routeCadastrees, voiesFerrees, filtre
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore', 'GeoSeries.notna', UserWarning)

eel.init('interface')

## TODO: Fusionner les deux fonctions en une seule!!
@eel.expose
def selectionDossier():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askdirectory()
    #root.withdraw()
    root.destroy()
    return choix_du_dossier

@eel.expose
def selectionBDgpkg():
    root = tk.Tk()
    global choix_du_dossier
    choix_du_dossier = askopenfilename(title="Sélectionner la Base de donnée", filetypes=[("geopackage files", "*.gpkg")])
    #root.withdraw()
    root.destroy()
    return choix_du_dossier

@eel.expose
def liste_data(chemin):
    '''Liste les données comprises dans le dossier ou le fichier correspondant au chemin indiqué'''
    donnee = []
    def ajoutShape(file):
        if file.endswith('.shp') or file.endswith('.geojson'):
            donnee.append(file)
    if chemin.endswith('.gpkg'):
        for layerName in listlayers(chemin):
            donnee.append(layerName)
    else:
        for folderName, subfolders, filenames in os.walk(chemin):
            ajoutShape(folderName)
            for subfolder in subfolders:
                ajoutShape(subfolder)
            for filename in filenames:
                ajoutShape(filename)
    return donnee

dict_sig = {}
@eel.expose
def add_data(cle, chemin, *argv):
    if argv:
        if type(chemin) == list():
            dict_sig[cle] = clean_data(gpd.read_file(chemin[0], layer = chemin[1]), argv)
        else:
            dict_sig[cle] = clean_data(gpd.read_file(chemin), argv)
    else:
        if type(chemin) == list():
            dict_sig[cle] = clean_data(gpd.read_file(chemin[0], layer = chemin[1]))
        else:
            dict_sig[cle] = clean_data(gpd.read_file(chemin))

#Fonction qui va inspecter la couche SIG et renvoyer le type de géométrie
@eel.expose
def geometryType(chemin, nom):
    if chemin.endswith('gpkg'):
        couche = gpd.read_file(chemin, layer=nom)
    else:
        couche = gpd.read_file(chemin + '/' + nom)
    if len(couche) == 0:
        return "Couche vide"
    else:
        print(str(couche["geometry"][0].geom_type))
        type = str(couche["geometry"][0].geom_type)
        return type

## Fonction pour attribuer des paramètres par type de zone de la couche STRUCTURATION TERRTORIALE ##
@eel.expose
def structuration_territoriale(chemin, nom):
    global structure
    if chemin.endswith('gpkg'):
        structure = gpd.read_file(chemin, layer=nom)
    else:
        structure = gpd.read_file(chemin + '/' + nom)
    for i in structure.columns:
        if structure[i].dtypes == 'object':
            structure[i].fillna('Valeur nulle', inplace = True)
        else:
            structure[i].fillna(0, inplace = True)
    liste = [i for i in structure.columns]
    structure.insert(len(structure.columns), "d_min_route", 100)
    structure.insert(len(structure.columns), "non-batie", 400)
    structure.insert(len(structure.columns), "batie", 1000)
    structure.insert(len(structure.columns), "cesMax", 40)
    structure.insert(len(structure.columns), "test", 10)
    structure.insert(len(structure.columns), "bufBati", 4)
    return liste

@eel.expose
def unique_values(champs):
    global enveloppe
    enveloppe = clean_data(structure, champs, ["d_min_route", "non-batie", "batie", "cesMax", "test", "bufBati"])
    enveloppe["geometry"] = enveloppe.buffer(0)
    enveloppe = enveloppe.dissolve(by=champs).reset_index()
    liste_valeur = list(enveloppe[champs])
    enveloppe = enveloppe.set_index(champs, drop=False)
    enveloppe.insert(len(enveloppe.columns), "d_min_route", 100)
    enveloppe.insert(len(enveloppe.columns), "non-batie", 400)
    enveloppe.insert(len(enveloppe.columns), "batie", 1000)
    enveloppe.insert(len(enveloppe.columns), "cesMax", 40)
    enveloppe.insert(len(enveloppe.columns), "test", 10)
    enveloppe.insert(len(enveloppe.columns), "bufBati", 4)
    return liste_valeur

@eel.expose
def lancement(donnees, exportCes):
    t0 = time.process_time()
    def timing(t, intitule):
        temps = time.process_time() - t
        if temps <=60:
            unite = 'secondes'
            temps = round(temps, 1)
        else:
            temps = round(temps / 60, 1)
            unite = 'minutes'
        print("\n   #####   {} {} {}  #####   \n".format(intitule,temps,unite))
    print('\n### Lancement du traitement ### \n\n ## Prise en compte de la structuration territoriale ##')
    ti = time.process_time()
    if donnees['paramètres']['perso'] == 'vide' and donnees['paramètres']['défauts'] != 'vide':
        param = donnees["paramètres"]["défauts"]
        global enveloppe
        enveloppe = clean_data(structure, ["d_min_route", "non-batie", "batie", "cesMax", "test", "bufBati"])
        enveloppe["geometry"] = enveloppe.buffer(0)
        enveloppe['d_min_route'] = param['d_min_route']
        enveloppe['non-batie'] = param['non-batie']
        enveloppe['batie'] = param['batie']
        enveloppe['cesMax'] = param['cesMax']
        enveloppe['test'] = param['test']
        enveloppe['bufBati'] = param['bufBati']
    elif donnees['paramètres']['perso'] != 'vide' and donnees['paramètres']['défauts'] == 'vide':
        param = donnees["paramètres"]["perso"]["valeurs"]
        liste = list(param.keys()) # nom des lignes
        champs = donnees["paramètres"]["perso"]["champs"]
        #col = list(list(param.values())[0].keys())
        l_route = [item["d_min_route"] for item in param.values()]
        l_non_batie = [item["non-batie"] for item in param.values()]
        l_batie = [item["batie"] for item in param.values()]
        l_ces = [item["cesMax"] for item in param.values()]
        l_test = [item["test"] for item in param.values()]
        l_buf_bati = [item["bufBati"] for item in param.values()]
        d = {
            champs : liste,
            "d_min_route" : l_route,
            "non-batie" : l_non_batie,
            "batie" : l_batie,
            "cesMax" : l_ces,
            "test" : l_test,
            "bufBati" : l_buf_bati
        }
        df = pd.DataFrame(d)
        df = df.set_index(champs)
        enveloppe.update(df,overwrite=True)
    else:
        enveloppe = structure
    #Récupération des couches sélectionnées dans l'interface
    couches = ["Parcelles", "Bâti", "Routes", "Voies ferrées"]
    chemins = {}
    for couche in couches:
        if couche in donnees["dossier"]["couches"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
        elif couche in donnees["gpkg"]["layers"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    #Selection des parcelles qui touchent l'enveloppe
    parcelle = chemins["Parcelles"]
    parcelle_intersect = gpd.overlay(parcelle, enveloppe, how='intersection')
    parcelle_intersect.crs = enveloppe.crs
    timing(ti, 'Prise en compte de la structuration territoriale terminée en')
    #Calcul du CES
    ti = time.process_time()
    ces = coeffEmpriseSol(chemins["Bâti"], parcelle_intersect, exportCes)
    timing(ti, 'Calcul du CES terminé en')
    #Sélection des parcelles
    ti = time.process_time()
    selection = selectionParcelles(ces)
    timing(ti, 'Sélection des parcelles terminé en')
    #Prise en compte de la proximité à la routes
    if "Routes" in chemins:
        ti = time.process_time()
        route = chemins["Routes"]
        routes_in_enveloppe = gpd.clip(route, enveloppe)
        routes_in_enveloppe = routes_in_enveloppe[routes_in_enveloppe["geometry"].notnull()]
        #potentiel = routeDesserte(routes_in_enveloppe, potentiel)
        timing(ti, 'Prise en compte de la proximité à la route terminée en')
        ti = time.process_time()
        selecion = routeCadastrees(routes_in_enveloppe, selection)
        timing(ti, 'Exclusion des routes cadastrées terminée en')
    #Prise en compte des voies ferrées si renseignées
    if "Voies ferrées" in chemins:
        selection = voiesFerrees(chemins["Voies ferrées"], selection)
    #Prise en compte des Filtres
    for couche in donnees["dossier"]["couches"]:
        if couche not in couches and couche != 'Structuration territoriale':
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
            selection = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]))
    for couche in donnees["gpkg"]["layers"]:
        if couche not in couches and couche != 'Structuration territoriale':
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
            selection = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]))
    #Test des parcelles vides identifiées
    ti = time.process_time()
    parcelle_vide = selection[selection["type"] == "parcelle vide"]
    test_vide, emprise_vide = test_emprise_vide(parcelle_vide)
    #Test des parcelles baties identifiées
    parcelle_batie = selection[selection["type"] == "parcelle batie"]
    test_batie, emprise_batie = test_emprise_batie(parcelle_batie, chemins["Bâti"])
    potentiel = pd.concat([test_vide, test_batie])
    potentiel_emprise = pd.concat([emprise_vide, emprise_batie])
    timing(ti, 'Test des parcelles terminé en')

    timing(t0, 'Traitement terminé! en')
    #CHARTS and MAPS
    #ces.plot(column='ces', cmap='Reds', legend=True)
    #chemins["Voies ferrées"].plot(ax=ax, color='black', linestyle='dashed', legend=True)
    #routes_in_enveloppe.plot(ax=ax, color='red', linewidth=0.1, legend=True)
    potentiel_emprise.plot(column='type', legend=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    potentiel.plot(ax=ax, column='type', legend=True)
    # Pie chart of potentiel parcelle complète
    potentiel_sum = potentiel.groupby("type").sum()
    batie = round(potentiel_sum["surf_par"][0] / 10000, 0)
    vide = round(potentiel_sum["surf_par"][1] / 10000, 0)
    sizes = [batie, vide]
    labels = 'Parcelle batie ({} ha)'.format(batie), 'Parcelle vide ({} ha)'.format(vide)
    somme = round((potentiel_sum["surf_par"][0] + potentiel_sum["surf_par"][1]) / 10000, 0)
    colors = ['#1f77b4', '#17becf']
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title("Répartition du potentiel foncier estimé à : {} ha".format(somme))

    # Pie chart of potentiel emprise mobilisable
    potentiel_emprise_sum = potentiel_emprise.groupby("type").sum()
    batie2 = round(potentiel_emprise_sum["surf_par"][0] / 10000, 0)
    vide2 = round(potentiel_emprise_sum["surf_par"][1] / 10000, 0)
    sizes2 = [batie2, vide2]
    labels2 = 'Emprise des parcelles baties ({} ha)'.format(batie2), 'Emprise des parcelles vides ({} ha)'.format(vide2)
    somme2 = round((potentiel_emprise_sum["surf_par"][0] + potentiel_emprise_sum["surf_par"][1]) / 10000, 0)
    colors2 = ['#1f77b4', '#17becf']
    fig2, ax2 = plt.subplots()
    ax2.pie(sizes2, labels=labels2, colors=colors2, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax2.set_title("Répartition du foncier mobilisable estimé à : {} ha".format(somme2))

    plt.show()
if __name__ == "__main__":
    eel.init('interface')
    eel.start('index.html', size=(1000, 800))
