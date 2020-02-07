
# coding: utf-8

# ## Paramètres

# In[1]:


# -*- coding: utf-8 -*-
"""
Tentative d'élaboration d'une enveloppe urbaine
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import time
from functools import reduce

t0 = time.process_time()
get_ipython().magic('matplotlib notebook')

# ## passer en GPK countries_gdf = geopandas.read_file("package.gpkg", layer='countries')

# ## ajotouter input 'taille mini des enveloppes' ?

# ## Paramètres INPUT
# 

# In[2]:


# =============================================================================
# buffer_dilatation=float(input("Buffer 1 : dilatation du bati : "))
# buffer_erosion=float(input("Buffer 2 : erosion du bati : "))
# surface_batie_minimale=float(input("Indiquer une surface batie minimale : "))
# surface_creux_a_combler=float(input("Indiquer la surface minimale des creux à combler en mètres carrés : "))
# =============================================================================
# =============================================================================
# 
# buffer_dilatation=+50
# buffer_erosion=-30
# surface_batie_minimale=30
# seuil_emprise=50
# =============================================================================

surf_min_AU = input('Merci d indiquer la taille des trous à combler en m²(ce qui ne sera pas comblé sera potentiellement une zones AU):(Si tu sais pas, met 2000m²) ')


# In[3]:


TamponBati = input ('choix de la taille du tampon autour du bati isolé (par défaut = 30m.)')


# In[4]:


TailleMiniEnv = input('Choix de la taille minimale des enveloppes a selectionner (mettre 0 pour toutes les garder, ou mettre 20000m² si tu ne sais pas)')


# ## Import des fonctions Citadia

# In[5]:


# Fonction nettoyage de la donnée
def clean_data (data):
    data = data[["geometry"]]
    data = data[data["geometry"].is_valid]
    data = data[data["geometry"].notnull()]
    data = explodePoly(data)
    data = data.to_crs({'init': 'epsg:2154'})
    data.reset_index(inplace=True)
    data = data[["geometry"]]
    return data

# Fonction index_spatial
def index_spatial(ref_geom, target_geom):
    target_geom = target_geom.unary_union
    spatial_index = ref_geom.sindex #index spatial sur les parcelles
    possible_index = list(spatial_index.intersection(target_geom.bounds)) #récupération de l'index des parcelles qui intersecte la bounding box du bati
    possible = ref_geom.iloc[sorted(possible_index)]
    precise = possible[possible.intersects(target_geom)] #récupération des parcelles qui intersecte le bati
    return precise

# fonction intersection
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
        t = time.process_time()
        spatial_index = df2.sindex
        print("Spatial_index Terminé. {} min \n".format(round((time.process_time() - t)/60), 2))
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        print(" bbox Terminé. {} min \n".format(round((time.process_time() - t)/60), 2))
        df1['sidx']=df1.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        print("sidx Terminé. {} min \n".format(round((time.process_time() - t)/60), 2))
        df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0), 
                                 [x.geometry]+list(df2.iloc[x.sidx].geometry)) , axis=1)
        df1.geometry = df1.new_g
        print("new_g Terminé. {} min \n".format(round((time.process_time() - t)/60), 2))
        df1 = df1.loc[df1.geometry.is_empty==False].copy()
        df1.drop(['bbox', 'sidx', 'new_g'], axis=1, inplace=True)
        return df1
    elif how=='symmetric_difference':
        df1['idx1'] = df1.index.tolist()
        df2['idx2'] = df2.index.tolist()
        df1['idx2'] = np.nan
        df2['idx1'] = np.nan
        dfsym = df1.merge(df2, on=['idx1','idx2'], how='outer', suffixes=['_1','_2'])
        dfsym['geometry'] = dfsym.geometry_1
        dfsym.loc[dfsym.geometry_2.isnull()==False, 'geometry'] = dfsym.loc[dfsym.geometry_2.isnull()==False, 'geometry_2']
        dfsym.drop(['geometry_1', 'geometry_2'], axis=1, inplace=True)
        dfsym = gpd.GeoDataFrame(dfsym, columns=dfsym.columns, crs=df1.crs)
        spatial_index = dfsym.sindex
        dfsym['bbox'] = dfsym.geometry.apply(lambda x: x.bounds)
        dfsym['sidx'] = dfsym.bbox.apply(lambda x:list(spatial_index.intersection(x)))
        dfsym['idx'] = dfsym.index.values
        dfsym.apply(lambda x: x.sidx.remove(x.idx), axis=1)
        dfsym['new_g'] = dfsym.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0), 
                         [x.geometry]+list(dfsym.iloc[x.sidx].geometry)) , axis=1)
        dfsym.geometry = dfsym.new_g
        dfsym = dfsym.loc[dfsym.geometry.is_empty==False].copy()
        dfsym.drop(['bbox', 'sidx', 'idx', 'idx1','idx2', 'new_g'], axis=1, inplace=True)
        return dfsym
    elif how=='union':
        dfinter = spatial_overlays(df1, df2, how='intersection')
        dfsym = spatial_overlays(df1, df2, how='symmetric_difference')
        dfunion = dfinter.append(dfsym)
        dfunion.reset_index(inplace=True, drop=True)
        return dfunion
    elif how=='identity':
        dfunion = spatial_overlays(df1, df2, how='union')
        cols1 = df1.columns.tolist()
        cols2 = df2.columns.tolist()
        cols1.remove('geometry')
        cols2.remove('geometry')
        cols2 = set(cols2).intersection(set(cols1))
        cols1 = list(set(cols1).difference(set(cols2)))
        cols2 = [col+'_1' for col in cols2]
        dfunion = dfunion[(dfunion[cols1+cols2].isnull()==False).values]
        return dfunion

# Fonction explode pour convertir des multiploygones en pomygone unique
def explodePoly(gdf):
    gs = gdf.explode()
    gdf2 = gs.reset_index().rename(columns={0: 'geometry'})
    gdf_out = gdf2.merge(gdf.drop('geometry', axis=1), left_on='level_0', right_index=True)
    gdf_out = gdf_out.set_index(['level_0', 'level_1']).set_geometry('geometry')
    gdf_out = gdf_out[["geometry"]]
    gdf_out.crs = gdf.crs
    return gdf_out    


# ## Import des données

# In[6]:

print("Initialisation des données :")
source = r"C:\Users\remi_\Documents\Data Science\Python\Foncier\data\foncier_draga.gpkg"
parcelle = gpd.read_file(source, layer = 'parcelle')
bati = gpd.read_file(source, layer = 'bati')
cimetiere = gpd.read_file(source, layer = 'cimetieres')
contour = gpd.read_file(source, layer = 'commune')
activite = gpd.read_file(source, layer = 'activite')
sport = gpd.read_file(source, layer = 'terrains')

print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))
# ## Nettoyage de la donnée

# In[7]:

print("Nettoyage de la donnée :")
parcelle = clean_data(parcelle)
bati = clean_data(bati)
cimetiere = clean_data(cimetiere)
contour = clean_data(contour)
activite = clean_data(activite)
sport = clean_data(sport)
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Calcul du bati

# In[8]:


#extraction du bati dont la superficie est superieure à 30 m²
print("Extraction du bâti dont la superficie est supérieur : ")
bati_30m2 = bati[bati["geometry"].area>=30]
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Dilatation et érosion

# In[9]:

print("Dilatation / Erosion :")
bati_dilatation = bati_30m2.copy()
bati_dilatation['geometry'] = bati_dilatation.buffer(50)
bati_dilatation.insert(1,"diss",1)
dissolve = bati_dilatation.dissolve("diss", as_index=False)
bati_erosion=dissolve.copy()
bati_erosion['geometry']=bati_erosion.buffer(-30)
bati_erosion = clean_data(bati_erosion)
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Dissoudre le buffer +50-30 du bati avec : terrains de sport, surfaces d'activités et cimetières (BD topo)

# In[10]:

print("Dissoudre le buffer +50-30 avec les terrains de sport, les surfaces d'activités et les cimetières : ")
bati_fusion = gpd.GeoDataFrame(pd.concat([bati_erosion,sport,cimetiere,activite],ignore_index=True))
bati_fusion = bati_fusion.set_geometry("geometry").reset_index()
bati_fusion.crs = {'init' :'epsg:2154'}
bati_fusion = clean_data(bati_fusion)
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Emprise de l'enveloppe par rapport à la parcelle

# In[11]:


# preparation
print("Découper l'enveloppe par rapport aux parcelles : ")
parcelle_enveloppe = parcelle.copy()
parcelle_enveloppe.insert(0,"id_env",range(1,1+len(parcelle)))
parcelle_enveloppe.insert((len(parcelle_enveloppe.columns)-1),"surf_par",parcelle_enveloppe["geometry"].area)

#decouper l'enveloppe par rapport aux parcelles
intersection = spatial_overlays(parcelle_enveloppe, bati_fusion, how='intersection')
#intersection.to_file("test.shp")

dissolve2 = intersection.dissolve(by='id_env').reset_index()
dissolve2.insert((len(dissolve2.columns)-1),"surf_env",dissolve2["geometry"].area)
dissolve2=dissolve2.reset_index()
dissolve2 = dissolve2[['id_env', 'surf_env', 'surf_par','geometry']]
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

#dissolve2.head()

# Récupérer les parcelles intersectant l'enveloppe-tampon tout en gardant les infos de surfaces calculées 
print("Rcupérer les parcelles intersectant l'enveloppe-tampon tout en gardant les infos de surfaces calculées :")
intersection = spatial_overlays(parcelle_enveloppe, dissolve2, how='intersection')
intersection.rename(columns={'id_env_1' : 'id_env'}, inplace=True)
intersection = intersection[["id_env","surf_env"]]
intersection.insert(1, "intersect", "1")

parcelles_entieres = parcelle_enveloppe.merge(intersection, how='left', on='id_env')
parcelles_entieres = parcelles_entieres.fillna('0')
parcelles_entieres = parcelles_entieres[parcelles_entieres["intersect"] == '1']
parcelles_entieres = parcelles_entieres.set_geometry("geometry")
#parcelles_entieres 
#parcelles_entieres.plot()
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Calcul de l'emprise

# In[12]:

print("calcul de l'emprise : ")
emprise=parcelles_entieres.copy()
emprise['emprise'] = emprise['surf_env']/emprise['surf_par']*100
#emprise.to_file("C:\data_local\Data_pamiers\emprise.shp")
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ## Seuil fort/faible

# In[13]:

print("Séléction de l'emprise forte : ")
# selectionner une emprise forte et une emprise faible
emprise_forte = emprise.copy()
emprise_forte["geometry"] = emprise_forte.buffer(0)
emprise_forte = emprise_forte[emprise_forte["emprise"]>50]
#emprise_forte.to_file("emprise_forte.shp")
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

print("Séléction de l'emprise forte : ")
emprise_faible = emprise.copy()
emprise_faible["geometry"] = emprise_faible.buffer(0)
emprise_faible = emprise_faible[emprise_faible["emprise"]<50]
#emprise_faible.to_file("emprise_faible.shp")
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ### Enveloppe "forte"

# In[14]:


emprise_forte.insert(1,"commun",1)
#emprise_forte = emprise_forte.dissolve("commun", as_index=False)
emprise_forte = emprise_forte.to_crs('+init=epsg:2154')



# ### Enveloppe "faible"

# In[15]:


# Buffer de 30 m autour du bati 
print("Emprise de 30m autour du bâti : ")
bati_buff30m = bati.copy()
bati_buff30m["geometry"] = bati_buff30m.buffer(float(TamponBati))
bati_buff30m = bati_buff30m[bati_buff30m["geometry"].notnull()]
bati_buff30m = bati_buff30m[bati_buff30m["geometry"].is_valid]
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

#intersecter l'emprise faible avec le buffer +30 autour des batis
print("Intersection de l'emprise faible avec le buffer +30m autour du bâti : ")
intersection2 = spatial_overlays(emprise_faible,bati_buff30m,how='intersection')
intersection2.insert(1,"id_bat",range(1,1+len(intersection2)))

# Centroide bati

# bati_centroide = bati.copy()
# bati_centroide['geometry'] = bati.centroid
# bati_centroide["geometry"]=bati_centroide.buffer(1)
intersection3 = spatial_overlays(intersection2,bati,how='intersection')

intersection2=intersection2.copy()
intersection2=intersection2.merge(intersection3,how="left",on="id_bat")
intersection2=intersection2.set_geometry("geometry_x")

intersection2=intersection2[intersection2["intersect_y"]=="1"]

intersection4=intersection2.copy()
intersection4.rename(columns={'geometry_x' : 'geometry'}, inplace=True)
intersection4=intersection4.set_geometry("geometry")
intersection4.crs=("+init=epsg:2154")
intersection4=clean_data(intersection4)

#intersection4.to_file("intersection4.shp")

#dissoudre le résultat par "commun"
emprise_faible=intersection4.copy()
emprise_faible.insert(1, "commun", "1")
emprise_faible = emprise_faible.dissolve("commun", as_index=False)
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))


# ### Assembler les emprises

# ## a améliorer: difference de faible par forte, avant le merge ?

# In[16]:

print("Assemblage des emprises : ")
#merge emprise faible avec emprise forte 
merge_tampon = gpd.GeoDataFrame(pd.concat([emprise_faible,emprise_forte],ignore_index=True))
merge_tampon = merge_tampon.set_geometry("geometry").reset_index()
merge_tampon.crs = {'init' :'epsg:2154'}
merge_tampon = clean_data(merge_tampon)
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))
#merge_tampon.to_file("merge.shp")


# ### Calcul de l'emprise route

# In[17]:


emprise_route = gpd.read_file(source, layer='emprise_route')
#emprise_route=gpd.overlay(contour,parcelle,how='difference')
#emprise_route.crs=("+init=epsg:2154")
#emprise_route=clean_data(emprise_route)
#emprise_route["geometry"] = emprise_route.buffer(1)

#emprise_route.to_file("emprise_route.shp")


# ## integration des routes dans l'enveloppe

# In[18]:


print("Intégration des routes dans l'enveloppe : ")
#buffer +50m
enveloppe_50m=merge_tampon.copy()
enveloppe_50m["geometry"] = enveloppe_50m.buffer(50)
enveloppe_50m = enveloppe_50m[enveloppe_50m["geometry"].notnull()]
enveloppe_50m = enveloppe_50m[enveloppe_50m["geometry"].is_valid]

#enveloppe_60m.to_file("env1.shp")

#buffer -30 m
enveloppe_30m=enveloppe_50m.copy()
enveloppe_30m["geometry"] = enveloppe_30m.buffer(-35)
enveloppe_30m = enveloppe_30m[enveloppe_30m["geometry"].notnull()]
enveloppe_30m = enveloppe_30m[enveloppe_30m["geometry"].is_valid]

#enveloppe_30m.to_file("enveloppe_30m.shp")

#découper les routes par rapport à l'enveloppe 2 ---> clip ?
route1=spatial_overlays(enveloppe_30m,emprise_route,how='intersection')
route1.crs=("+init=epsg:2154")
route1=route1.reset_index()
route1=clean_data(route1)
#route1.to_file("route1.shp")

#Assembler route et tampon
enveloppe_1=gpd.GeoDataFrame(pd.concat([route1,merge_tampon],ignore_index=True))
enveloppe_1.crs=("+init=epsg:2154")
enveloppe_1 = enveloppe_1.reset_index()
enveloppe_1=clean_data(enveloppe_1)

#enveloppe_1.to_file("enveloppe_1.shp")
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# In[20]:


#route1.to_file("C:\data_local\Data_pamiers\\routes.shp")


# ## Combler les creux

# In[19]:

print("Combler les creux : ")
enveloppe_2=enveloppe_1.copy()
enveloppe_2["geometry"] = enveloppe_2.geometry.buffer(0.01)
enveloppe_2 = enveloppe_2[enveloppe_2["geometry"].notnull()]
enveloppe_2 = enveloppe_2[enveloppe_2["geometry"].is_valid]
enveloppe_2.insert (1,"commun","1")
enveloppe_2 = enveloppe_2.reset_index()
enveloppe_2 = enveloppe_2[enveloppe_2["geometry"].area > 0]
#enveloppe_2.to_file("C:/Users/Citadia/Dev/draga//enveloppe2.shp")
enveloppe_2 = enveloppe_2.dissolve("commun", as_index=False)
enveloppe_2.crs = {'init' :'epsg:2154'}
enveloppe_2 = clean_data(enveloppe_2)
enveloppe_2["geometry"] = enveloppe_2.geometry.buffer(0)
enveloppe_2 = clean_data(enveloppe_2)

#Combler les creux (surface minimale à indiquer dans les paramètres input)
trous =  gpd.overlay(contour,enveloppe_2,how='difference')
trous.crs = contour.crs
trous = clean_data(trous)
#trous.to_file("C:/Users/Citadia/Dev/draga/trous.shp")
trous_expl = explodePoly(trous)
trous_expl = trous_expl[trous_expl["geometry"].area<= float(surf_min_AU)]

trous_expl["geometry"] = trous_expl.geometry.buffer(1)

trous_expl =trous_expl[trous_expl["geometry"].area>=1]

union = gpd.overlay(trous_expl, enveloppe_2, how='union')
union.insert(1,"diss",1)
dissolve = union.dissolve("diss", as_index=False)
dissolve = explodePoly(dissolve)
dissolve = dissolve[dissolve["geometry"].area>2000]
dissolve.insert (1,"surf_env", dissolve["geometry"].area)
enveloppe = dissolve
#enveloppe.to_file("C:\data_local\Data_pamiers\\enveloppe.shp")
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))

# ## supression des routes qui dépassent de l'enveloppe

# In[20]:


##supression des routes qui dépassent de l'enveloppe
print("Suppression des routes qui dépassent de l'enveloppe : ")
route2 = route1.copy()
route2["geometry"] = route2.buffer(30)
route2 = route2[route2["geometry"].notnull()]
route2 = route2[route2["geometry"].is_valid]
#route2.plot()

enveloppe_3 = emprise_forte.copy()
enveloppe_3["geometry"] = enveloppe_3.buffer(50)
enveloppe_3["geometry"] = enveloppe_3.buffer(-50)
enveloppe_3 = enveloppe_3[enveloppe_3["geometry"].notnull()]
enveloppe_3 = enveloppe_3[enveloppe_3["geometry"].is_valid]

#enveloppe_3.plot()
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))


# In[ ]:


# différencier route par enveloppes
print("Différenciation des routes par l'enveloppe : ")
route2["geometry"] = route2.geometry.buffer(0.01)
print("buffer de route2 : OK!")
enveloppe_3["geometry"] = enveloppe_3.geometry.buffer(0.01)
print("buffer de enveloppe_3 : OK!")
route2.to_file(r"C:\Users\remi_\Documents\Data Science\Python\Foncier\results\Enveloppe\route2.shp")
enveloppe_3.to_file(r"C:\Users\remi_\Documents\Data Science\Python\Foncier\results\Enveloppe\enveloppe_3.shp")
route2.insert(1,"diss",1)
route2 = route2.dissolve("diss", as_index=False)
route3 = spatial_overlays(route2, enveloppe_3, how='difference')
#route3 = route2[route2.disjoint(enveloppe_3.unary_union)]
#route3= gpd.overlay(route2,enveloppe_3,how='difference')
print("Difference entre route2 et enveloppe_3 : OK!")
route4 = route3[route3.disjoint(emprise_faible.unary_union)]
print("Terminé. {} min \n".format(round((time.process_time() - t0)/60, 2)))
#route4= gpd.overlay(route3,emprise_faible,how='difference')
print("Difference entre route3 et emprise_faible : OK!")
route3 = route4
route3.crs=("+init=epsg:2154")
route3=clean_data(route3)
print("clean_data de route3 : OK!")

#nettoyer couche route 3
route3 = route3[route3["geometry"].area>=10]
print("supression des entité < 10m² : OK!")
#route3.plot()
#route3.to_file("C:\data_local\Data_pamiers\\route3.shp")
print("Terminé. {min} min et {sec} s \n".format(min =round((time.process_time() - t0)/60, 2), sec = (round((time.process_time() - t0)/60, 4) - min)*60))

# In[25]:


#nettoyer couche enveloppe
enveloppe['geometry']=enveloppe.buffer(0.1)
enveloppe['geometry']=enveloppe.buffer(-0.1)

# différencier enveloppe 1 par route3 (routes qui débordent)
##enveloppeOK= gpd.overlay(enveloppe,route3,how='difference')
enveloppe.crs=("+init=epsg:2154")
#enveloppeOK=clean_data(enveloppeOK)
#enveloppeOK.plot()
#enveloppeOK.to_file("C:\data_local\Data_pamiers\\enveloppeMOINSlesRoutes.shp")

#selection grandes enveloppes 

EnveloppeFinal = enveloppe[enveloppe["geometry"].area> float(TailleMiniEnv)]
EnveloppeFinal.to_file(r"C:\Users\remi_\Documents\Data Science\Python\Foncier\results\EnveloppeFinal.shp")


# In[27]:


elapsed_time0 = time.process_time() - t0
"Export terminé ! Calcul effectué en {} minutes :) Sachant que tu aurais mis 10x plus de temps à le faire à la main, et qu'un ricard se boit en 5 minutes, tu peux aller boire {} verres. Santé ! ".format((round(elapsed_time0/60,2)),(round(elapsed_time0/60)*10/5)) 

