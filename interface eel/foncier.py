# coding:utf-8

import eel
import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
import os
from fiona import listlayers
import geopandas as gpd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

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
def clean_data (gdf, *argv):    #Possibilité de garder certaines colonnes
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


def spatial_overlays(df1, df2, how='intersection', reproject=True):
    df1 = df1.copy()
    df2 = df2.copy()
    df1['geometry'] = df1.geometry.buffer(0)
    df2['geometry'] = df2.geometry.buffer(0)
    if df1.crs!=df2.crs and reproject:
        print('Data has different projections.')
        print('Converted data to projection of first GeoPandas DatFrame')
        df2.to_crs(crs=df1.crs, inplace=True)
    if how=='intersection':
        # Spatial Index to create intersections
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        pairs = df1['sidx'].to_dict()
        nei = []
        for i,j in pairs.items():
            for k in j:
                nei.append([i,k])
        pairs = gpd.GeoDataFrame(nei, columns=['idx1','idx2'], crs=df1.crs)
        pairs = pairs.merge(df1, left_on='idx1', right_index=True)
        pairs = pairs.merge(df2, left_on='idx2', right_index=True, suffixes=['_1','_2'])
        pairs['Intersection'] = pairs.apply(lambda x: (x['geometry_1'].intersection(x['geometry_2'])).buffer(0), axis=1)
        pairs = gpd.GeoDataFrame(pairs, columns=pairs.columns, crs=df1.crs)
        cols = pairs.columns.tolist()
        cols.remove('geometry_1')
        cols.remove('geometry_2')
        cols.remove('sidx')
        cols.remove('bbox')
        cols.remove('Intersection')
        dfinter = pairs[cols+['Intersection']].copy()
        dfinter.rename(columns={'Intersection':'geometry'}, inplace=True)
        dfinter = gpd.GeoDataFrame(dfinter, columns=dfinter.columns, crs=pairs.crs)
        dfinter = dfinter.loc[dfinter.geometry.is_empty==False]
        dfinter.drop(['idx1','idx2'], inplace=True, axis=1)
        return dfinter
    elif how=='difference':
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0),
                                 [x.geometry]+list(df2.iloc[x.sidx].geometry)) , axis=1)
        df1.geometry = df1.new_g
        df1 = df1.loc[df1.geometry.is_empty==False].copy()
        df1.drop(['bbox', 'sidx', 'new_g'], axis=1, inplace=True)
        return df1

## Fonction pour attribuer des paramètres par type de zone de la couche STRUCTURATION TERRTORIALE ##
@eel.expose
def structuration_territoriale(chemin, nom):
    print(chemin)
    print(nom)
    if chemin.endswith('gpkg'):
        structure = gpd.read_file(chemin, layer=nom)
    else:
        structure = gpd.read_file(chemin + '/' + nom)
    liste = [i for i in structure.columns]
    print(liste)
    return liste


# if x == 2:
#     mes_var[nom_variables[x]].columns = map(str.lower, mes_var[nom_variables[x]].columns)
#     # 1 - Choix du champ détenant l'information de la structuration du territoire par l'utilisateur
#     global struct_terr
#     struct_terr = Tk()
#     struct_terr.title('Choix du champs pour identifier la structuration territoriale')
#     global liste_champs
#     liste_champs = Listbox(struct_terr)
#     n = 1
#     for i in mes_var[nom_variables[x]].columns:
#         liste_champs.insert(n, i)
#         n += 1
#     def champs():
#         index3 = liste_champs.curselection()
#         global choix_du_champs
#         choix_du_champs = liste_champs.get(index3)
#         global enveloppe
#         col = choix_du_champs
#         mes_var[nom_variables[2]].columns = map(str.lower, mes_var[nom_variables[2]].columns)
#         if "typezone" in mes_var[nom_variables[2]].columns :
#             mes_var[nom_variables[2]] = mes_var[nom_variables[2]][mes_var[nom_variables[2]]["typezone"] == 'U']
#         else:
#             pass
#         enveloppe = Traitement.clean_data(mes_var[nom_variables[2]], col)
#         enveloppe["geometry"] = enveloppe.buffer(0)
#         enveloppe = enveloppe.dissolve(by=col).reset_index()
#         # Création de 4 champs correspondant aux paramètres à appliquer pour chaque zone. Ici les paramètre par défaut sont appliqué, mais sont modifiable dans le menu 'Paramètre'.
#         enveloppe.insert(1, "d_min_route", 50)# Distance minimale de la parcelle à la route (en m)
#         enveloppe.insert(2, "s_non_bati", 500)# Surface minimale de la parcelle non batie (en m²)
#         enveloppe.insert(3, "s_bati", 2000)# Surface minimale de la parcelle bati (en m²)
#         enveloppe.insert(4, "ces_max", 10)# CES maximum de la parcelle bati (en m²)
#         global D
#         D = {
#                0 : "d_min_route",
#                1 : "s_non_bati",
#                2 : "s_bati",
#                3 : "ces_max"}
#         struct_terr.destroy()
#
#     Button(struct_terr, text = 'Valider', width=15, command=champs, bg="orange").grid(row=2, column=1)
#     liste_champs.grid(row=1, column=1)
#     struct_terr.mainloop()

if __name__ == "__main__":
    eel.init('interface')
    eel.start('index.html', size=(1000, 800))
