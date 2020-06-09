# coding:utf-8

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPoint

def explode(indata):
    indf = indata.copy()
    outdf = gpd.GeoDataFrame(columns=indf.columns)
    for idx, row in indf.iterrows():
        if row["geometry"].geom_type in ['Polygon', 'LineString', 'Point']:
            outdf = outdf.append(row,ignore_index=True)
        if row["geometry"].geom_type in ['MultiPolygon', 'MultiPoint', 'MultiString']:
            multdf = gpd.GeoDataFrame(columns=indf.columns)
            recs = len(row["geometry"])
            multdf = multdf.append([row]*recs,ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom,'geometry'] = row["geometry"][geom]
            outdf = outdf.append(multdf,ignore_index=True)
    return outdf
#Cleaning des couches SIG (Elimination des geometries invalid et nulle et de mltipolygon à polgon)
def clean_data(gdf, *argv):    #Possibilité de garder certaines colonnes
    gdf = gdf[gdf["geometry"].is_valid]
    gdf = gdf[gdf["geometry"].notnull()]
    gdf = gdf.to_crs({'init': 'epsg:2154'})
    gdf = explode(gdf)
    gdf.reset_index(drop=True)
    gdf = gdf.set_geometry("geometry")
    for i in list(gdf.columns):
        if i == "geometry":
            pass
        elif i not in argv or not argv:
            gdf = gdf.drop(i, axis=1)
    gdf.insert(1, "id", range(1, 1 + len(gdf)))
    return gdf

#Calcul du coefficient de l'emprise au sol avec maintient des colonnes paramètres et sauvegarde ou pas de la couche
def coeffEmpriseSol(bati, parcelle) :
    print("\n   ##   Calcul du CES   ##   \n")
    bati = bati.copy()
    parcelle = parcelle.copy()
    #Maintien des colonnes paramètres et conversion en valeur nuérique
    parcelle[["d_min_route", "non-batie", "batie", "cesMax", "test", "bufBati"]] = parcelle[["d_min_route", "non-batie", "batie", "cesMax", "test", "bufBati"]].apply(pd.to_numeric)
    parcelle.insert(len(parcelle.columns), "id_par", range(1, 1 + len(parcelle)))
    intersection = gpd.overlay(parcelle, bati, how='intersection')
    dissolve = intersection.dissolve(by="id_par").reset_index()
    dissolve.insert(len(dissolve.columns), "surf_bat", dissolve.geometry.area)
    dissolve.drop("geometry", axis=1, inplace=True)
    coeff = parcelle.merge(dissolve, how='left', on="id_par", suffixes=('', '_y'))
    coeff.insert(len(coeff.columns), "surf_par", coeff.geometry.area)
    coeff['ces'] = coeff['surf_bat']/coeff['surf_par']*100
    coeff = coeff.fillna(0)
    for i in list(coeff.columns):
         if i not in ['id_par','surf_par', 'surf_bat', 'ces', 'geometry', "d_min_route", "non-batie", "batie", "cesMax", "test", "bufBati"]:
            coeff = coeff.drop(i, axis=1)
    coeff.crs = ('+init=epsg:2154')
    return(coeff)

#Sélection des parcelles en fonction des paramètres renseignées par l'utilisateur
def selectionParcelles(ces):
    print("\n   ## Sélection des parcelles   ##   \n")
    global selection
    selection = ces.copy()
    selection = selection[(selection["ces"] < 0.5) & (selection.geometry.area >= selection["non-batie"]) | (selection["ces"] >= 0.5) & (selection["ces"] < selection["cesMax"]) & (selection.geometry.area >= selection["batie"])]
    selection.loc[selection['ces']>= 0.5, 'type'] = "parcelle batie"
    selection.loc[selection['ces']< 0.5, 'type'] = "parcelle vide"
    selection["filtres"] = "0"
    #selection[["type"]] = selection["ces"].apply(lambda x: "parcelle vide" if x < 0.5 else "parcelle batie")
    return selection

#Test des emprises mobilisables des parcelles non bâtie
def test_emprise_vide(parcelles, exclues):
    print("\n   ## Test des parcelles vides   ##   \n")
    couche_buf = parcelles.copy()
    #Applique un buffer pour chaque entité suivant la valeur de la colonne "test" correspondante
    couche_buf['geometry'] = couche_buf.apply(lambda x: x.geometry.buffer(-x.test).buffer(x.test), axis=1)
    couche_buf = couche_buf[couche_buf.geometry.area >= couche_buf["non-batie"]]
    couche_buf["surf_par"] = couche_buf.geometry.area
    liste_id = [i for i in couche_buf['id_par']]
    #selection = selection.loc[~selection['id_par'].isin(liste_id)]
    exclues.loc[~exclues["id_par"].isin(liste_id), "test_emprise"] = 'echec du test dents creuses'
    return couche_buf, exclues

#Test des emprises mobilisables des parcelles bâtie
def test_emprise_batie(parcelles, bati, exclues):
    print("\n   ## Test des parcelles baties   ##   \n")
    bati_buf = bati.copy()
    parcelles.crs = bati.crs
    bati_buf = gpd.overlay(bati_buf, parcelles, how='intersection')
    bati_buf['geometry'] = bati_buf.apply(lambda x: x.geometry.buffer(x.bufBati), axis=1)
    emprise = gpd.overlay(parcelles, bati_buf, how='difference')
    emprise['geometry'] = emprise.apply(lambda x: x.geometry.buffer(-x.test).buffer(x.test), axis=1)
    #enregistrement des parcelles ne passant pas le test dans la couche exclues
    emprise_echec = emprise[emprise.geometry.area < emprise["non-batie"]]
    liste_id = [i for i in emprise_echec['id_par']]
    exclues.loc[exclues["id_par"].isin(liste_id), "test_emprise"] = 'echec du test division parcellaire'
    #Maintien des parcelles passant le test avec succès dans la couche emprise
    emprise = emprise[emprise.geometry.area >= emprise["non-batie"]]
    emprise["surf_par"] = emprise.geometry.area
    emprise = explode(emprise)
    #Calcul du Bounding Box des emprise disponibles en division parcellaire
    bbox = emprise.copy()
    bbox.crs = parcelles.crs
    bbox.geometry = bbox.geometry.apply(lambda geom: MultiPoint(list(geom.exterior.coords)))
    bbox.geometry = bbox.geometry.apply(lambda geom: geom.minimum_rotated_rectangle)
    #Intersection des bounding box avec les parcelles
    parc = parcelles.copy()
    for i in list(parc.columns):
        if i in ["geometry", "id_par"]:
            pass
        else:
            parc = parc.drop(i, axis=1)
    parc = parc.rename(columns={'id_par': 'id'})
    intersection = gpd.overlay(bbox, parc, how='intersection')
    liste_id2 = [i for i in bbox['id_par']]
    intersection = intersection.loc[intersection['id_par'].isin(liste_id2)]
    intersection = explode(intersection)
    return emprise, exclues, intersection
#INUTILE
def routeDesserte(route, potentiel):
    print("\n   ## Prise en compte de la proximité à la route   ##   \n")
    buffer_route = route.copy()
    buffer_route['geometry'] = buffer_route.apply(lambda x: x.geometry.buffer(x.d_min_route), axis=1)
    buffer_route.insert(0, "desserte",'1')
    buffer_route = buffer_route.dissolve("desserte", as_index=False)
    buffer_route = clean_data(buffer_route)
    print('\n - Buffer autour des routes :OK!\n')
    intersection = gpd.overlay(potentiel, buffer_route, how='intersection')
    print('\n - Intersection entre le potentiel et le buffer des routes : OK!\n')
    liste_id = [i for i in intersection['id_par']]
    couche = potentiel.loc[potentiel['id_par'].isin(liste_id)]
    return couche
    #potentiel = potentiel.merge(intersection, how='left', on='id_par', suffixes=('', '_y'))
    #print("Merge entre l'intersection et le potentiel : OK!\n")

def routeCadastrees(route, potentiel):
    print('\n   ##  Exclusion des routes cadastrées   ##   ')
    # buffer de 5m sur les routes
    route.geometry = route.buffer(5)
    route = route.set_geometry("geometry")
    parcelles = potentiel.copy()
    print('\n - Calcul du CES des routes')
    route.crs = parcelles.crs
    intersection = gpd.overlay(route, parcelles, how='intersection')
    dissolve = intersection.dissolve(by='id_par').reset_index()
    dissolve.insert(2, "surf_route", dissolve.geometry.area)
    dissolve["surf_route"] = dissolve.geometry.area
    dissolve.drop("geometry", axis=1, inplace=True)
    ces_route = parcelles.merge(dissolve, how='left', on='id_par', suffixes=('', '_y'))
    ces_route['ces_route'] = ces_route['surf_route']/ces_route['surf_par']*100
    ces_route = ces_route.fillna(0)
    ces_route = ces_route[['id_par', 'surf_par', 'ces_route', 'geometry']]
    # Selection de la voirie cadastrée (ces_route >= 40%)
    ces_route = ces_route[(ces_route["ces_route"] >= 40)]
    ces_route.crs = {'init': 'epsg:2154'}
    print("\n - Suppression du cadastre d'étude de  la voirie cadastrée sélectionnée")
    liste_id = [i for i in ces_route['id_par']]
    parcelles.loc[parcelles['id_par'].isin(liste_id), "filtres"] = 'routes'
    couche = potentiel.loc[~potentiel['id_par'].isin(liste_id)]
    return couche, parcelles

def voiesFerrees(voies, potentiel, exclues):
    print('\n   ##  Prise en compte des voies ferrées   ##   ')
    voie_ferree = voies.copy()
    voie_ferree.geometry = voie_ferree.buffer(1)
    #voie_ferree = Traitement.clean_data(voie_ferree)
    voie_ferree.crs = potentiel.crs
    exclues.loc[exclues.geometry.intersects(voie_ferree.geometry), "filtres"] = 'voies ferrees'
    couche = potentiel[potentiel.disjoint(voie_ferree.unary_union)]
    return couche, exclues

def filtre(potentiel, couche, buffer, nom, exclues):
    print('\n   ##  Prise en compte des filtres  ##   ')
    filtre = couche.copy()
    filtre.crs = potentiel.crs
    if buffer != 0:
        filtre.geometry = filtre.geometry.buffer(buffer)
    difference = gpd.overlay(potentiel, filtre, how='difference')
    intersection = potentiel[potentiel.geometry.intersects(filtre.geometry.any())]
    intersection.reset_index(drop=True)
    liste_id = [i for i in intersection['id_par']]
    exclues.loc[exclues['id_par'].isin(liste_id), "filtres"] = nom
    verification = selectionParcelles(difference)
    return verification, exclues
