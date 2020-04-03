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
warnings.simplefilter(action='ignore', category=FutureWarning)

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

##Fonction explode
def explodePoly(gdf):
    gs = gdf.explode()
    gdf2 = gs.reset_index().rename(columns={0: 'geometry'})
    gdf_out = gdf2.merge(gdf.drop('geometry', axis=1), left_on='level_0', right_index=True)
    gdf_out = gdf_out.set_index(['level_0', 'level_1']).set_geometry('geometry')
    gdf_out = gdf_out[["geometry"]]
    gdf_out.crs = gdf.crs
    return gdf_out
#Cleaning des couches SIG
def clean_data(gdf, *argv):    #Possibilité de garder certaines colonnes
    gdf = gdf[gdf["geometry"].is_valid]
    gdf = gdf[gdf["geometry"].notnull()]
    gdf = gdf.to_crs({'init': 'epsg:2154'})
    gdf.explode()
    gdf.reset_index(drop=True)
    gdf = gdf.set_geometry("geometry")
    for i in list(gdf.columns):
        if i == "geometry":
            pass
        elif i not in argv:
            gdf = gdf.drop(i, axis=1)
    if not argv:
        gdf = gdf[["geometry"]]
    return gdf

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
    print("Nombre de couche en mémoire : ", len(dict_sig))

# def spatial_overlays(df1, df2, how='intersection', reproject=True):
#     df1 = df1.copy()
#     df2 = df2.copy()
#     df1['geometry'] = df1.geometry.buffer(0)
#     df2['geometry'] = df2.geometry.buffer(0)
#     if df1.crs!=df2.crs and reproject:
#         print('Data has different projections.')
#         print('Converted data to projection of first GeoPandas DatFrame')
#         df2.to_crs(crs=df1.crs, inplace=True)
#     if how=='intersection':
#         # Spatial Index to create intersections
#         spatial_index = df2.sindex
#         df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
#         df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
#         pairs = df1['sidx'].to_dict()
#         nei = []
#         for i,j in pairs.items():
#             for k in j:
#                 nei.append([i,k])
#         pairs = gpd.GeoDataFrame(nei, columns=['idx1','idx2'], crs=df1.crs)
#         pairs = pairs.merge(df1, left_on='idx1', right_index=True)
#         pairs = pairs.merge(df2, left_on='idx2', right_index=True, suffixes=['_1','_2'])
#         pairs['Intersection'] = pairs.apply(lambda x: (x['geometry_1'].intersection(x['geometry_2'])).buffer(0), axis=1)
#         pairs = gpd.GeoDataFrame(pairs, columns=pairs.columns, crs=df1.crs)
#         cols = pairs.columns.tolist()
#         cols.remove('geometry_1')
#         cols.remove('geometry_2')
#         cols.remove('sidx')
#         cols.remove('bbox')
#         cols.remove('Intersection')
#         dfinter = pairs[cols+['Intersection']].copy()
#         dfinter.rename(columns={'Intersection':'geometry'}, inplace=True)
#         dfinter = gpd.GeoDataFrame(dfinter, columns=dfinter.columns, crs=pairs.crs)
#         dfinter = dfinter.loc[dfinter.geometry.is_empty==False]
#         dfinter.drop(['idx1','idx2'], inplace=True, axis=1)
#         return dfinter
#     elif how=='difference':
#         spatial_index = df2.sindex
#         df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
#         df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
#         df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0),
#                                  [x.geometry]+list(df2.iloc[x.sidx].geometry)) , axis=1)
#         df1.geometry = df1.new_g
#         df1 = df1.loc[df1.geometry.is_empty==False].copy()
#         df1.drop(['bbox', 'sidx', 'new_g'], axis=1, inplace=True)
#         return df1

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
    return liste

@eel.expose
def unique_values(champs):
    global enveloppe
    enveloppe = clean_data(structure, champs, ["d_min_route", "non-batie", "batie", "cesMax"])
    enveloppe["geometry"] = enveloppe.buffer(0)
    enveloppe = enveloppe.dissolve(by=champs).reset_index()
    liste_valeur = list(enveloppe[champs])
    enveloppe = enveloppe.set_index(champs, drop=False)
    enveloppe.insert(len(enveloppe.columns), "d_min_route", 100)
    enveloppe.insert(len(enveloppe.columns), "non-batie", 400)
    enveloppe.insert(len(enveloppe.columns), "batie", 1000)
    enveloppe.insert(len(enveloppe.columns), "cesMax", 40)
    print(enveloppe)
    return liste_valeur

def coeffEmpriseSol(bati, parcelle) :
    bati = bati.copy()
    parcelle = parcelle.copy()
    parcelle[['d_min_route', 'non-batie', 'batie', 'cesMax']] = parcelle[['d_min_route', 'non-batie', 'batie', 'cesMax']].apply(pd.to_numeric)
    parcelle.insert(len(parcelle.columns), "id_par", range(1, 1 + len(parcelle)))
    intersection = gpd.overlay(parcelle, bati, how='intersection')
    dissolve = intersection.dissolve(by="id_par").reset_index()
    dissolve.insert(len(dissolve.columns), "surf_bat", dissolve["geometry"].area)
    dissolve.drop("geometry", axis=1, inplace=True)
    coeff = parcelle.merge(dissolve, how='left', on="id_par", suffixes=('', '_y'))
    coeff.insert(len(coeff.columns), "surf_par", coeff["geometry"].area)
    coeff['ces'] = coeff['surf_bat']/coeff['surf_par']*100
    coeff = coeff.fillna(0)
    for i in list(coeff.columns):
         if i not in ['id_par','surf_par', 'surf_bat', 'ces', 'geometry', 'd_min_route', 'non-batie', 'batie', 'cesMax']:
            coeff = coeff.drop(i, axis=1)
    coeff.crs = ('+init=epsg:2154')
    # if enregistrer_ces == True:
    #     coeff.to_file(export + '/' + 'ces.shp')
    #     print('CES exporté')
    # else:
    #     pass
    return(coeff)

def selectionParcelles(ces):
    selection = ces.copy()
    selection = selection[(selection["ces"] < 0.5) & (selection["geometry"].area >= selection["non-batie"]) | (selection["ces"] >= 0.5) & (selection["ces"] < selection["cesMax"]) & (selection["geometry"].area >= selection["batie"])]
    selection.loc[selection['ces']>= 0.5, 'type'] = "parcelle batie"
    selection.loc[selection['ces']< 0.5, 'type'] = "parcelle vide"

    #selection[["type"]] = selection["ces"].apply(lambda x: "parcelle vide" if x < 0.5 else "parcelle batie")
    return selection

@eel.expose
def lancement(donnees):
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
        enveloppe = clean_data(structure, ["d_min_route", "non-batie", "batie", "cesMax"])
        enveloppe["geometry"] = enveloppe.buffer(0)
        enveloppe['d_min_route'] = param['d_min_route']
        enveloppe['non-batie'] = param['non-batie']
        enveloppe['batie'] = param['batie']
        enveloppe['cesMax'] = param['cesMax']
    elif donnees['paramètres']['perso'] != 'vide'and donnees['paramètres']['défauts'] == 'vide':
        param = donnees["paramètres"]["perso"]["valeurs"]
        liste = list(param.keys()) # nom des lignes
        champs = donnees["paramètres"]["perso"]["champs"]
        #col = list(list(param.values())[0].keys())
        l_route = [item["d_min_route"] for item in param.values()]
        l_non_batie = [item["non-batie"] for item in param.values()]
        l_batie = [item["batie"] for item in param.values()]
        l_ces = [item["cesMax"] for item in param.values()]
        d = {
        champs : liste,
        "d_min_route" : l_route,
        "non-batie" : l_non_batie,
        "batie" : l_batie,
        "cesMax" : l_ces
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
    timing(ti, 'Prise en compte de la structuration territoriale terminé en')

    print("\n   ##   Calcul du CES   ##   \n")
    ti = time.process_time()
    ces = coeffEmpriseSol(chemins["Bâti"], parcelle_intersect)
    print(ces.columns)
    print(ces.describe())
    ces.plot(column='ces', cmap='Reds', legend=True)
    timing(ti, 'Calcul du CES terminé en')

    print("\n   ## Sélection des parcelles   ##   \n")
    ti = time.process_time()
    selection = selectionParcelles(ces)
    timing(ti, 'Sélection des parcelles terminée en')
    selection.plot(column='type', legend=True)
    plt.show()
    timing(t0, 'Traitement terminé! en')

if __name__ == "__main__":
    eel.init('interface')
    eel.start('index.html', size=(1000, 800))
