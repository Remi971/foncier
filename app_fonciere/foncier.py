import eel
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
from fiona import listlayers
from fiona import _shim, schema
from pyproj import _datadir, datadir
import geopandas as gpd
#from geofeather import to_geofeather, from_geofeather, to_shp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TKAgg')
from time import process_time, strftime, localtime
import json
import warnings
import pprint
from source import explode, clean_data, coeffEmpriseSol, selectionParcelles, test_emprise_vide, test_emprise_batie, routeCadastrees, voiesFerrees, filtre
from reglages import exportReglages, export_reglages_csv
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
        type = str(couche["geometry"][0].geom_type)
        print(type)
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
    # structure.insert(len(structure.columns), "d_min_route", 100)
    structure.insert(len(structure.columns), "non-batie", 400)
    structure.insert(len(structure.columns), "batie", 1000)
    structure.insert(len(structure.columns), "cesMax", 40)
    structure.insert(len(structure.columns), "test", 10)
    structure.insert(len(structure.columns), "bufBati", 4)
    return liste

@eel.expose
def unique_values(champs):
    global enveloppe
    enveloppe = clean_data(structure, champs, ["non-batie", "batie", "cesMax", "test", "bufBati"])
    enveloppe.geometry = enveloppe.buffer(0)
    enveloppe = enveloppe.dissolve(by=champs).reset_index()
    liste_valeur = list(enveloppe[champs])
    enveloppe = enveloppe.set_index(champs, drop=False)
    # enveloppe.insert(len(enveloppe.columns), "d_min_route", 100)
    enveloppe.insert(len(enveloppe.columns), "non-batie", 400)
    enveloppe.insert(len(enveloppe.columns), "batie", 1000)
    enveloppe.insert(len(enveloppe.columns), "cesMax", 40)
    enveloppe.insert(len(enveloppe.columns), "test", 10)
    enveloppe.insert(len(enveloppe.columns), "bufBati", 4)
    return liste_valeur

@eel.expose
def lancement(donnees):
    global reglages
    reglages = donnees
    t0 = process_time()
    def timing(t, intitule):
        temps = process_time() - t
        if temps <=60:
            unite = 'secondes'
            temps = round(temps, 1)
        else:
            temps = round(temps / 60, 1)
            unite = 'minutes'
        print("\n   #####   {} {} {}  #####   \n".format(intitule,temps,unite))
    print('\n   ##### Lancement du traitement #####   \n'+ '\n' + strftime("%a, %d %b %Y %H:%M:%S", localtime())+ '\n' + '\n   ##   Prise en compte de la structuration territoriale   ##   \n')
    eel.progress(90/7)
    if "Structuration territoriale" in donnees["dossier"]["couches"] or "Structuration territoriale" in donnees["gpkg"]["layers"]:
        if donnees['paramètres']['perso'] == 'vide':
            param = donnees["paramètres"]["défauts"]
            global enveloppe
            enveloppe = clean_data(structure, ["non-batie", "batie", "cesMax", "test", "bufBati"])
            enveloppe["geometry"] = enveloppe.buffer(0)
            # enveloppe['d_min_route'] = param['d_min_route']
            enveloppe['non-batie'] = int(param['non-batie'])
            enveloppe['batie'] = int(param['batie'])
            enveloppe['cesMax'] = int(param['cesMax'])
            enveloppe['test'] = int(param['test'])
            enveloppe['bufBati'] = int(param['bufBati'])
        else:
            param = donnees["paramètres"]["perso"]["valeurs"]
            liste = list(param.keys()) # nom des lignes
            champs = donnees["paramètres"]["perso"]["champs"]
            # l_route = [item["d_min_route"] for item in param.values()]
            l_non_batie = [item["non-batie"] for item in param.values()]
            l_batie = [item["batie"] for item in param.values()]
            l_ces = [item["cesMax"] for item in param.values()]
            l_test = [item["test"] for item in param.values()]
            l_buf_bati = [item["bufBati"] for item in param.values()]
            d = {
                champs : liste,
                # "d_min_route" : l_route,
                "non-batie" : l_non_batie,
                "batie" : l_batie,
                "cesMax" : l_ces,
                "test" : l_test,
                "bufBati" : l_buf_bati
            }
            df = pd.DataFrame(d)
            df = df.set_index(champs)
            enveloppe.update(df,overwrite=True)

    #Récupération des couches sélectionnées dans l'interface
    print("\n   ##   Récupération des couches   ##   \n")
    couches = ["Parcelles", "Bâti", "Routes", "Voies ferrées"]
    chemins = {}
    for couche in couches:
        print(f"\n   - Récupération de la couche {couche}")
        ti = process_time()
        if couche in donnees["dossier"]["couches"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
        elif couche in donnees["gpkg"]["layers"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
        timing(ti, f'{couche} récupéré en')
    #Selection des parcelles qui touchent l'enveloppe
    parcelle = chemins["Parcelles"]
    try:
        parcelle_intersect = gpd.overlay(parcelle, enveloppe, how='intersection')
        parcelle_intersect.crs = enveloppe.crs
    except NameError:
        param = donnees["paramètres"]["défauts"]
        parcelle['non-batie'] = int(param['non-batie'])
        parcelle['batie'] = int(param['batie'])
        parcelle['cesMax'] = int(param['cesMax'])
        parcelle['test'] = int(param['test'])
        parcelle['bufBati'] = int(param['bufBati'])

    timing(ti, 'Prise en compte de la structuration territoriale terminée en')
    #Calcul du CES
    eel.progress(90/7)
    ti = process_time()
    global ces
    try:
        ces = coeffEmpriseSol(chemins["Bâti"], parcelle_intersect)
    except UnboundLocalError:
        ces = coeffEmpriseSol(chemins["Bâti"], parcelle)
    timing(ti, 'Calcul du CES terminé en')
    #Sélection des parcelles
    eel.progress(90/7)
    ti = process_time()
    selection = selectionParcelles(ces)
    selection_initiale = selection.copy()
    timing(ti, 'Sélection des parcelles terminé en')
    global exclues
    #Prise en compte des routes cadastrées
    if "Routes" in chemins:
        eel.progress(90/7)
        ti = process_time()
        route = chemins["Routes"]
        try:
            routes_in_enveloppe = gpd.overlay(route, enveloppe, how='intersection')
            routes_in_enveloppe = routes_in_enveloppe[routes_in_enveloppe.geometry.notnull()]
            selection1, exclues = routeCadastrees(routes_in_enveloppe, selection)
            timing(ti, 'Exclusion des routes cadastrées terminée en')
        except NameError:
            selection1, exclues = routeCadastrees(route, selection)
            timing(ti, 'Exclusion des routes cadastrées terminée en')
        except IndexError:
            print("MESSAGE : Les routes n'intersectent pas les parcelles!")
            chemins.pop("Routes")
        #potentiel = routeDesserte(routes_in_enveloppe, potentiel)
        #timing(ti, 'Prise en compte de la proximité à la route terminée en')
        #ti = process_time()

    else:
        eel.progress(90/7)
    #Prise en compte des voies ferrées si renseignées
    if "Voies ferrées" in chemins:
        eel.progress(90/7)
        if "Routes" in chemins:
            try:
                selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection1, exclues)
            except NameError:
                selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection1)
        else:
            try:
                selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection, exclues)
            except NameError:
                selection, exclues = voiesFerrees(chemins["Voies ferrées"], selection)
    else:
        eel.progress(90/7)
    #Prise en compte des Filtres
    eel.progress(90/7)
    for couche in donnees["dossier"]["couches"]:
        if couche not in couches and couche != 'Structuration territoriale':
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
            try:
                selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche, exclues)
            except NameError:
                selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche)
    for couche in donnees["gpkg"]["layers"]:
        if couche not in couches and couche != 'Structuration territoriale':
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
            try:
                selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche, exclues)
            except NameError:
                selection, exclues = filtre(selection, chemins[couche], int(donnees["paramètres"]["filtres"][couche]), couche)
    #Test des parcelles vides identifiées
    eel.progress(90/7)
    ti = process_time()
    parcelle_vide = selection[selection["Potentiel"] == "Dents creuses"]
    try:
        emprise_vide, exclues = test_emprise_vide(parcelle_vide, exclues)
    except NameError:
        emprise_vide = test_emprise_vide(parcelle_vide)
    #Test des parcelles baties identifiées
    parcelle_batie = selection[selection["Potentiel"] == "Division parcellaire"]
    global boundingBox
    try:
        emprise_batie, boundingBox, exclues = test_emprise_batie(parcelle_batie, chemins["Bâti"], exclues)
    except NameError:
        emprise_batie, boundingBox = test_emprise_batie(parcelle_batie, chemins["Bâti"])
    timing(ti, 'Test des parcelles terminé en')
    global potentiel_emprise
    parcelle_vide = parcelle_vide.loc[parcelle_vide['id_par'].isin(i for i in emprise_vide['id_par'])]
    liste_id_vide = [ i for i in emprise_vide['id_par']]
    potentiel_emprise = pd.concat([emprise_batie, selection_initiale.loc[selection_initiale['id_par'].isin(set(liste_id_vide))]])
    potentiel_emprise = explode(potentiel_emprise)
    boundingBox = pd.concat([boundingBox, parcelle_vide])
    boundingBox.reset_index(inplace=True)
    boundingBox.loc[boundingBox['id_par'].isnull(), "id_par"] = boundingBox["id_par_1"]
    boundingBox = boundingBox[boundingBox["geometry"].is_valid]
    boundingBox = boundingBox[boundingBox["geometry"].notnull()]
    #boundingBox["Surf"] = round(boundingBox.geometry.area, 2)
    boundingBox.drop("id_par_1", axis=1)
    global potentiel
    liste_id = [i for i in emprise_vide["id_par"]] + [i for i in boundingBox["id_par_1"]]
    potentiel = selection_initiale.loc[selection_initiale['id_par'].isin(set(liste_id))]
    try:
        exclues = exclues.loc[~exclues['id_par'].isin(set(liste_id + [i for i in emprise_batie["id_par"]]))]
        exclues.loc[exclues.geometry.isna(), "test_emprise"]
    except NameError:
        pass

    def ajout_champs(couche):
        try:
            couche.insert(len(couche.columns), "Surf",round(couche.geometry.area, 2))
        except ValueError:
            couche["Surf"] = round(couche.geometry.area, 2)
        try:
            couche.insert(len(couche.columns), "Commune",'')
        except ValueError:
            couche.insert(len(couche.columns), "Commune1",'')
        try:
            couche.insert(len(couche.columns), "Comment",'')
        except ValueError:
            couche.insert(len(couche.columns), "Comment1",'')
        couche.insert(len(couche.columns), "Date",strftime("%d-%m-%Y %H:%M:%S", localtime()))
        couche.insert(len(couche.columns), "Suppr",'')

    ajout_champs(potentiel)
    ajout_champs(potentiel_emprise)
    ajout_champs(boundingBox)
    try:
        ajout_champs(exclues)
    except NameError:
        pass
    timing(t0, 'Traitement terminé! en')
    print('\n' + strftime("%a, %d %b %Y %H:%M:%S", localtime()))
    #CHARTS and MAPS
    #ces.plot(column='ces', cmap='Reds', legend=True)
    #chemins["Voies ferrées"].plot(ax=ax, color='black', linestyle='dashed', legend=True)
    #routes_in_enveloppe.plot(ax=ax, color='red', linewidth=0.1, legend=True)
    #potentiel_emprise.plot(column='type', legend=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    potentiel.plot(ax=ax, column='Potentiel', legend=True)
    # Pie chart of potentiel parcelle complète
    potentiel_sum = potentiel.groupby("Potentiel").sum()
    batie = round(potentiel_sum["surf_par"][0] / 10000, 0)
    vide = round(potentiel_sum["surf_par"][1] / 10000, 0)
    sizes = [batie, vide]
    labels = 'Dents creuses ({} ha)'.format(batie), 'Division parcellaire ({} ha)'.format(vide)
    somme = round((potentiel_sum["surf_par"][0] + potentiel_sum["surf_par"][1]) / 10000, 0)
    colors = ['#1f77b4', '#17becf']
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.set_title("Répartition du potentiel foncier estimé à : {} ha".format(somme))
    plt.show()

@eel.expose
def dataviz(couche):
    # Pie chart of potentiel emprise mobilisable
    potentiel_emprise_sum = potentiel_emprise.groupby("Potentiel").sum()
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

@eel.expose
def export(exportCes):
    err = False
    try:
        print(f'\nLe potentiel foncier concerne {len(potentiel)} parcelles\n')
    except NameError:
        err = True
        print("Il n'y a pas de potentiel à exporter. Veuillez lancer un traitement.")
        return err
    else:
        root = tk.Tk()
        dossier = askdirectory()
        #root.withdraw()
        root.destroy()
        potentiel.crs =  "EPSG:2154"
        date = strftime("%d%m%Y_%H-%M-%S", localtime())
        nom_sortie = f"{date}resultats.gpkg"
        potentiel.to_file(dossier + '/' + nom_sortie, layer='potentiel_parcelle', driver="GPKG")
        potentiel_emprise.crs = {'init': 'epsg:2154'}
        potentiel_emprise.to_file(dossier + '/' + nom_sortie, layer='potentiel_emprise', driver="GPKG")
        try:
            exclues.crs = "EPSG:2154"
            exclues.to_file(dossier + '/' + nom_sortie, layer='parcelles_exlues', driver="GPKG")
        except NameError:
            pass
        boundingBox.crs = "EPSG:2154"
        boundingBox.to_file(dossier + '/' + nom_sortie, layer='boundingBox', driver="GPKG")
        exportReglages(reglages, dossier, date)
        export_reglages_csv(reglages, dossier, date)
        if exportCes:
            ces.crs = "EPSG:2154"
            ces.to_file(dossier + '/' + nom_sortie,layer='ces', driver='GPKG')
        print('\nExport terminé !\n')
        return err

## Erosion-Dilatation : définition de l'enveloppe Brut
@eel.expose
def enveloppe_urbaine(donnees, surf_bati_min, dilatation, erosion, bufbati_env):
    ## Récupération de la donnée
    couches = ["Parcelles", "Bâti", "Routes", "Voies ferrées"]
    chemins = {}
    dossier = donnees["dossier"]["chemin"]
    for couche in couches:
        print(f"\n   - Récupération de la couche {couche}")
        ti = process_time()
        if couche in donnees["dossier"]["couches"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
        elif couche in donnees["gpkg"]["layers"]:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    for couche in donnees["dossier"]["couches"]:
        if couche not in couches:
            chemins[couche] = clean_data(gpd.read_file(donnees["dossier"]["chemin"] + '/' + donnees["dossier"]["couches"][couche]))
    for couche in donnees["gpkg"]["layers"]:
        if couche not in couches:
            chemins[couche] = clean_data(gpd.read_file(donnees["gpkg"]["nomGPKG"], layer=donnees["gpkg"]["layers"][couche]))
    #extraction du bati dont la superficie est superieure à [seuil utilisateur]
    print("\n 1 - Erosion-Dilatation : définition de l'enveloppe Brut\n")
    bati = chemins['Bâti']
    bati = clean_data(bati)
    surf_bati_min = int(surf_bati_min)
    bati_tri = bati[bati.geometry.area >= surf_bati_min]
    bati_dilatation = bati_tri.copy()
    dilatation = int(dilatation)
    bati_dilatation.geometry = bati_dilatation.buffer(dilatation)
    bati_dilatation.insert(1,"diss",1)
    dissolve = bati_dilatation.dissolve("diss", as_index=False)
    erosion = int(erosion)
    bati_erosion = dissolve.copy()
    bati_erosion.geometry = dissolve.buffer(erosion)
    enveloppe_brut = clean_data(bati_erosion)
    enveloppe_brut.to_file(dossier + '/enveloppe.gpkg', layer='1_enveloppe_brut', driver='GPKG')
    print("Couche '1_envelope_brut' exportée!")

    print("\n 2 - Dissoudre le buffer +50-30 du bati avec : terrains de sport, surfaces d'activités et cimetières (BD topo)\n")
    dissolution = enveloppe_brut.copy()
    for couche in chemins.keys():
        if couche not in couches:
            dissolution = pd.concat([dissolution, chemins[couche]])
    dissolution.reset_index(inplace=True)
    dissolution.insert(len(dissolution.columns), "commun", "1")
    dissolution = dissolution.dissolve(by='commun').reset_index()
    dissolution = clean_data(dissolution)
    dissolution.to_file(dossier + '/enveloppe.gpkg', layer='2_dissolution', driver='GPKG')
    print("Couche '2_dissolution' exportée!")

    print("\n 3 - Emprise de l'enveloppe par rapport à la parcelle\n")
    parcelle_enveloppe = chemins["Parcelles"].copy()
    parcelle_enveloppe.insert(0,"id_par",range(1,1+len(parcelle_enveloppe)))
    parcelle_enveloppe.insert(len(parcelle_enveloppe.columns), "surf_par", parcelle_enveloppe.geometry.area)
    intersection = gpd.overlay(parcelle_enveloppe, dissolution, how='intersection')
    intersection.insert(len(intersection.columns), "surf_env", intersection.geometry.area)
    liste_par_env = [i for i in intersection["id_par"]]
    parcelles_entieres = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_par_env)]
    parcelles_entieres.to_file(dossier + '/enveloppe.gpkg', layer='3_parcelles_entieres', driver='GPKG')
    print("Couche '3_parcelles_entieres' exportée!")

    print("\n 4 - Seuil fort/faible")
    intersection["emprise"] = intersection["surf_env"] / intersection["surf_par"] *100
    faible = intersection[intersection["emprise"] <= 50]
    liste_faible = [i for i in faible["id_par"]]
    emprise_faible = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_faible)]
    emprise_faible.to_file(dossier + '/enveloppe.gpkg', layer='4_emprise_faible', driver='GPKG')
    print("Couche '4_emprise_faible' exportée!")
    forte = intersection[intersection["emprise"] > 50]
    liste_forte = [i for i in intersection["id_par"]]
    emprise_forte = parcelle_enveloppe.loc[parcelle_enveloppe["id_par"].isin(liste_forte)]
    emprise_forte.to_file(dossier + '/enveloppe.gpkg', layer='4_emprise_forte', driver='GPKG')
    print("Couche '4_emprise_forte' exportée!")

    print("\n 5 - Intersection emprise faible et buffer autour du bâti")
    bati_buffer = chemins["Bâti"].copy()
    bufbati_env = int(bufbati_env)
    bati_buffer.geometry = bati_buffer.buffer(bufbati_env)
    bati_buffer = clean_data(bati_buffer)
    intersection2 = gpd.overlay(emprise_faible,bati_buffer, how='intersection')
    intersection2.insert(1, "id_bat", range(1,1+len(intersection2)))
    intersection2.to_file(dossier + '/enveloppe.gpkg', layer='5_empriseFaible_batiBuf', driver='GPKG')
    print("Couche '5_empriseFaible_batiBuf' exportée!")

    try:
        print(len(enveloppe_brut))
    except NameError:
        return False
    return True

if __name__ == "__main__":
    eel.init('interface')
    eel.start('index.html', size=(1000, 900))
