#!/usr/bin/env python3
# coding: utf-8

#import pandas as pd
import geopandas as gpd
import fiona
import numpy as np
import os
import os.path
from functools import reduce
import tkinter as tk
from tkinter import Button, Entry, Label, Canvas, StringVar, IntVar, Checkbutton, Menu, OptionMenu, Frame, Scrollbar, Listbox, Tk
#from tkinter import Canvas, Button, StringVar, Entry, Checkbutton, Label, IntVar, Menu, Frame, OptionMenu, Scrollbar, Tk, Listbox
#from tkinter import filedialog
from tkinter.filedialog import askdirectory, askopenfilename
#from tkinter.messagebox import *
from tkinter import ttk
import time
#import Enveloppes_urbaines.py as env

# Exporter toutes les fonctions dans un deuxième script

#Class pour les couches SIG à la place des dictionnaires à développer :
'''
class CoucheSIG:
    def __init__(self, nom, chemin):
        self.nom = nom
        self.chemin = chemin
        mes_var[self.nom] = clean_data(gpd.read_file(self.chemin))
        
        

'''


class Appli(tk.Tk):
    ''' Class regroupant tous les éléments composant l'interface graphique '''
    # Fenêtre principale
    def __init__(self):
        ''' Les différents widget qui composent l'interface sont initialisés ici. L'utilisation de "global" sur certaines variables, permet de les réutiliser ou les modifier dans d'autres fonctions '''
        super().__init__()
        
        # Ajout du titre
        self.title("Identification du potentiel foncier")
        self.tabControl = ttk.Notebook(self)                     # Création du Tab Control
        global tab1
        tab1 = ttk.Frame(self.tabControl)                        # Création d'un 1er onglet
        self.tabControl.add(tab1, text="Import des données") 
        # Ajout du 1er onglet
        global tab2
        tab2 = ttk.Frame(self.tabControl)                        # Création d'un 2e onglet
        self.tabControl.add(tab2, text="Paramètre par défaut")   # Ajout du 2e onglet

        self.tabControl.pack(expand=1, fill='both') 
        # LabelFrame using tab1 as a the parent
        mighty = ttk.LabelFrame(tab1, text="DATA")
        mighty.grid(column=0, row=0, padx=8, pady=4)
        
        #Bouton et canvas de la section du dossier utilisateur
        self.canvas_dossier = Canvas(tab1, bg = 'white', height = 20, width = 500)
        self.canvas_dossier.grid(row=1, column=2)
        txt_file = self.canvas_dossier.create_text(250, 10, text = 'Choix du dossier', fill = 'grey', tags='label')
        
        bt_dossier = Button(tab1, text = 'Sélection du dossier', background = 'blue', width = 20,command = self.dossier)
        bt_dossier.grid(row=1,column=1)
        
        bt_gpkg = Button(tab1, text = 'Sélection du Geopackage', background = 'green', width = 20,command = self.geopackage)
        bt_gpkg.grid(row=1,column=3)
       
        #Bouton pour lister les données
        bt_lister = Button(tab1, text = "Lister les données", bg = 'white', width = 20,command = self.lister)
        bt_lister.grid(row=2,column=1, sticky = 'n')

        #Bouton et canvas pour l'export des données
        global canvas_export
        canvas_export = Canvas(tab1, bg = 'white', height = 20, width = 500)
        canvas_export.grid(row = 18, column = 2)
        bt_export = Button(tab1, text = 'Export des données', bg = 'white', width = 20, command = self.dossier_export)
        bt_export.grid(row = 18, column = 1)
        
        # Bouton de lancement du script foncier 
        bt_lancer = Button(tab1, text = 'Lancer le traitement', bg = 'red', width = 20, command = Traitement.script)
        bt_lancer.grid(row = 19, column = 1)
        
        # Bouton de lancement du calcul de l'enveloppe urbaine
        bt_enveloppe = Button(tab1, text="Calcul de l'enveloppe urbaine", bg = 'yellow', width = 25)
        bt_enveloppe.grid(row=19, column=2)
        
        #Ensemble des variables avec des identifiants
        global nom_variables
        nom_variables = {
                0 : 'Parcelles',
                1 : 'Bati',
                2 : 'Structuration territoriale',
                3 : 'Routes',
                4 : 'Voies ferrees'}

        # Association des couches shapes avec la fonction boutons
        global mes_var
        mes_var = {} # Dictionnaire qui va stocker les couches shape associé aux identifiants des variables du dictionnaire nom_variables sous la forme {id : chouche shape}
        global labels
        labels = {}        
        global my_button
        my_button = {}

        global param
        param = {}
        
        global paramEntry
        paramEntry = {}
        
        global r
        r = 14
        
        for i in nom_variables:
            my_button[nom_variables[i]] = Button(tab1, text = nom_variables[i], bg = 'grey', activebackground='white', width = 20, command=lambda x = i: self.bouton(x))
            my_button[nom_variables[i]].grid(row=4+i, column=1, sticky = 'n')
         
  
        def creationFiltre():
            global filtre
            filtre = StringVar()
            filtre.set('Nom de filtre')
            global AjoutFiltre
            AjoutFiltre = Entry(tab1, textvariable=filtre, width=20)
            AjoutFiltre.grid(row=15, column=1)
            
        creationFiltre()
        
        def creationButton():
            nom_variables[len(nom_variables)] = filtre.get()
            my_button[filtre.get()] = Button(tab1, text = filtre.get(), bg = 'grey', activebackground='white', width = 20, command=lambda x = len(nom_variables)-1: self.bouton(x))
            my_button[filtre.get()].grid(row=3+len(nom_variables), column=1, sticky = 'n')
            AjoutFiltre.destroy()
            creationFiltre()
            
#            menu = self.popupMenu['menu']
#            menu.delete(0, 'end')
#            for data in list(nom_variables.values()):
#                menu.add_command(label=data, command=lambda data = data : self.popupMenu.set(data))
#            choices = {data for data in list(nom_variables.values())}
#            self.popupMenu = OptionMenu(mainframe, tkvar, *choices)
        
            
        bt_test = Button(tab1, text="Ajouter un filtre", width=20, command = creationButton)
        bt_test.grid(row=15, column=2, sticky='w')  
        
        #Bouton d'annulation des choix des filtres
        bouton_cancel = Button(tab1, text = 'Annuler', bg = 'orange', width = 20, command = self.cancel)
        bouton_cancel.grid(row=16, column=1)
        
        # Bouton pour quitter l'application
        bouton_quit = Button(tab1, text = 'Quitter', bg = 'white', width = 20,command = self.destroy)
        bouton_quit.grid(row=17,column=1)
        
        # Checkbutton pour choisir de sauvegarder la couche des CES
        global enregistrer_ces
        enregistrer_ces=False
        option_ces = Checkbutton(tab1, text="Sauvegarder la couche du Coefficient d'Emprise au Sol (CES)", command=self.save_ces)
        option_ces.grid(row = 16, column = 2)

        ### Configuration (dans la Tab2) ####
        label_potentiel = Label(tab2, text='Dents creuses')
        label_potentiel.grid(row=4, column=4, columnspan=2)

        label1 = Label(tab2, text = 'Distance minimale de la parcelle à la route (en m):')
        label1.grid(row=5, column=4)
        global value1
        value1 = IntVar()
        value1.set(50)
        entree1 = Entry(tab2, textvariable=value1, width=10)
        entree1.grid(row=5, column=5)

        label2 = Label(tab2, text = 'Surface minimale de la parcelle non batie (en m²):')
        label2.grid(row=6, column=4)
        global value2
        value2 = IntVar()
        value2.set(500)
        entree2 = Entry(tab2, textvariable=value2, width=10)
        entree2.grid(row=6, column=5)

        label_potentiel2 = Label(tab2, text='Divisions parcellaires')
        label_potentiel2.grid(row=7, column=4, columnspan=2)

        label3 = Label(tab2, text = 'CES maximum de la parcelle bati (en %):')
        label3.grid(row=8, column=4)
        global value3
        value3 = IntVar()
        value3.set(10)
        entree3 = Entry(tab2, textvariable=value3, width=10)
        entree3.grid(row=8, column=5)

        label4 = Label(tab2, text = 'Surface minimale de la parcelle bati (en m²):')
        label4.grid(row=9, column=4)
        global value4
        value4 = IntVar()
        value4.set(2000)
        entree4 = Entry(tab2, textvariable=value4, width=10)
        entree4.grid(row=9, column=5)
        
        
        
        # Bouton de validation des paramètres par défaut
        bt_valider = Button(tab2, text='Valider les paramètres', command=self.defaut_ok, width=20)
        bt_valider.grid(row=11, column=4)


        # Création de la barre de menu
        menubar = Menu(self) #Création de la barre de menu
        menu = Menu(menubar, tearoff=0)
        menu.add_command(label="Seuil du potentiel", command=self.param)
        menu.add_separator()
        menu.add_command(label="Calcul de l'enveloppe", command=self.tabEnveloppe)
        #menu1.add_command(label='Quitter', command=self.win.destroy())
        menubar.add_cascade(label="Paramètres", menu=menu)
        
        self.config(menu=menubar)
        
        #Ajout d'un DropDown pour indiquer quelle couche des filtres corespond aux routes
        global mainframe
        mainframe = Frame(tab2)
        mainframe.grid(row=5, column=6, sticky=('N', 'W', 'E', 'S'))
        
        tkvar = StringVar()
        choices = {data for data in list(nom_variables.values())}
        self.popupMenu = OptionMenu(tab2, tkvar, *choices)
        Label(mainframe, text="Sélectionnez la donnée correspondante aux routes").grid(row=5, column=6)
        self.popupMenu.grid(row=6, column=6)
        tkvar.set('Données des routes')
        
        def change_dropdown(*args):
            print(tkvar.get())
            
        tkvar.trace('w', change_dropdown)
#        global mainframe
#        mainframe = Frame(tab2)
#        mainframe.grid(row=5, column=6, sticky=(N, W, E, S))
        
#        tkvar = StringVar()
#        choices = {data for data in list(nom_variables.values())}
#        self.popupMenu = OptionMenu(tab2, tkvar, *choices)
#        Label(mainframe, text="Sélectionnez la donnée correspondante aux routes").grid(row=5, column=6)
#        self.popupMenu.grid(row=6, column=6)
#        tkvar.set('Données des routes')
#        
#        def change_dropdown(*args):
#            print(tkvar.get())
#            
#        tkvar.trace('w', change_dropdown)

    #Fonction lister les données récupérées dans le dossier utilisateur
    def lister(self):
        def ajoutShape(file):
            if file.endswith('.shp'):
                donnee.append(file)
        
        if choix_du_dossier.endswith('.gpkg'):
            for layerName in fiona.listlayers(choix_du_dossier):
                donnee.append(layerName)
        else:
            for folderName, subfolders, filenames in os.walk(choix_du_dossier):
                ajoutShape(folderName)
    
                for subfolder in subfolders:
                    ajoutShape(subfolder)
    
                for filename in filenames:
                    ajoutShape(filename)

        # Association des fichiers à un numéro (index)
        i = 1
        y = 0
        for shp in donnee:  # Création de la liste d'index du dictionnaire
            index.append(i)
            i += 1
        for x in index:  # La liste des couches shape sera contenu dans le dictionnaire dict_shp dont chaque fichier shape sera associé à un index
            dict_shp[x] = donnee[y]
            y += 1

        # ScrollBar
        yDefilB = Scrollbar(tab1, orient='vertical')
        yDefilB.grid(row=3, column=3, sticky='ns')

        len_liste = len(dict_shp)
        global liste_shp
        liste_shp = Listbox(tab1, width = 80,height = 8, yscrollcommand=yDefilB.set)
        n = 1
        while True:
            for i in dict_shp:
                liste_shp.insert(n, dict_shp[n])
                n += 1
            break
        liste_shp.grid(row=2,column=2, rowspan = 2)
        yDefilB['command'] = liste_shp.yview

        #Fonction initialisation du dossier utilisateur
    def dossier(self):
        # Constantes de la fonction dossier() qui seront réutilisé dans les sous-fonctions
        global donnee
        donnee = []     #Liste contenant les fichiers shape
        global dict_shp
        dict_shp = {}   # Dictionnaire qui va contenir les données accessible par un index
        global enregistrer_ces
        enregistrer_ces = False     #Variable relative à la Checkbox "*sauvegarder la couche CES"
        global index
        index = []
        global choix_du_dossier
        choix_du_dossier = True
        choix_du_dossier = askdirectory()   # définition du dossier utilisateur
        print('Initialisation du dossier de donnée : {}'.format(choix_du_dossier))
        
        self.canvas_dossier.delete('label')
        txt_file2 = self.canvas_dossier.create_text(250, 10, text = choix_du_dossier, tags='label')

    def geopackage(self):
        # Constantes de la fonction dossier() qui seront réutilisé dans les sous-fonctions
        global donnee
        donnee = []     #Liste contenant les fichiers shape
        global dict_shp
        dict_shp = {}   # Dictionnaire qui va contenir les données accessible par un index
        global enregistrer_ces
        enregistrer_ces = False     #Variable relative à la Checkbox "*sauvegarder la couche CES"
        global index
        index = []
        global choix_du_dossier
        choix_du_dossier = True
        choix_du_dossier = askopenfilename()   # définition du dossier utilisateur
        print('Initialisation du dossier de donnée : {}'.format(choix_du_dossier))
        
        self.canvas_dossier.delete('label')
        txt_file2 = self.canvas_dossier.create_text(250, 10, text = choix_du_dossier, tags='label')

    def dossier_export(self):
        global export
        export = True
        export = askdirectory()
        txt_export = canvas_export.create_text(250, 10, text = export)

    
     # Fonction d'annulation de l'asociation des shapes aux boutons
    def cancel(self):
        keys = ['Parcelles', 'Bati', 'Structuration territoriale', 'Routes', 'Voies Ferrees']
        global nom_variables
        nom_variables = {k: nom_variables[k] for k in range(0, 4)}
        for k in list(my_button):
            if k not in keys:
                my_button[k].destroy()
        global mes_var
        mes_var = {k: mes_var[k] for k in keys}
        for k in my_button:
            if k not in keys:
                labels[k].destroy()
    # Option d'enregistrement du CES
    def save_ces(self):
        global enregistrer_ces
        enregistrer_ces = True
    
    # Fonction pour la création des boutons
    def bouton(self, x):
        index2 = liste_shp.curselection()
        name = liste_shp.get(index2)
        if choix_du_dossier.endswith('.gpkg'):
            mes_var[nom_variables[x]] = gpd.read_file(choix_du_dossier, layer = name)
        else:
            mes_var[nom_variables[x]] = gpd.read_file(choix_du_dossier + '/' + name)#Le recours au dictionnaire permet de stocker toutes les couches sans les enregistrer individuellement dans des variables
        tmp = Label(tab1, text = 'La variable {} correspond à la donnée suivante : {}'.format(nom_variables[x], name))
        tmp.grid(row=4+x, column=2, sticky ='w')# Un texte s'affiche à côté de chaque bouton pour info
        labels[nom_variables[x]] = tmp
        if Traitement.typeGeom(mes_var[nom_variables[x]]) == 'LineString' and nom_variables[x] != 'Routes':
            label4 = Label(tab2, text = 'Paramètre de la donnée : {}'.format(nom_variables[x]))
            global r
            label4.grid(row=r, column=4, sticky = 'w')
            param[nom_variables[x]] = IntVar()
            param[nom_variables[x]].set(0)
            paramEntry[nom_variables[x]] = Entry(tab2, textvariable=param[nom_variables[x]], width=10)
            paramEntry[nom_variables[x]].grid(row=r, column=5)
            r += 1
            
            
        if x == 2:
            mes_var[nom_variables[x]].columns = map(str.lower, mes_var[nom_variables[x]].columns)
            # 1 - Choix du champ détenant l'information de la structuration du territoire par l'utilisateur
            global struct_terr
            struct_terr = Tk()
            struct_terr.title('Choix du champs pour identifier la structuration territoriale')
            global liste_champs
            liste_champs = Listbox(struct_terr)
            n = 1
            for i in mes_var[nom_variables[x]].columns:
                liste_champs.insert(n, i)
                n += 1
            def champs():
                index3 = liste_champs.curselection()
                global choix_du_champs
                choix_du_champs = liste_champs.get(index3)
                global enveloppe
                col = choix_du_champs
                mes_var[nom_variables[2]].columns = map(str.lower, mes_var[nom_variables[2]].columns)
                if "typezone" in mes_var[nom_variables[2]].columns :
                    mes_var[nom_variables[2]] = mes_var[nom_variables[2]][mes_var[nom_variables[2]]["typezone"] == 'U']
                else:
                    pass
                enveloppe = Traitement.clean_data(mes_var[nom_variables[2]], col)
                enveloppe["geometry"] = enveloppe.buffer(0)
                enveloppe = enveloppe.dissolve(by=col).reset_index()
                # Création de 4 champs correspondant aux paramètres à appliquer pour chaque zone. Ici les paramètre par défaut sont appliqué, mais sont modifiable dans le menu 'Paramètre'.
                enveloppe.insert(1, "d_min_route", 50)# Distance minimale de la parcelle à la route (en m)
                enveloppe.insert(2, "s_non_bati", 500)# Surface minimale de la parcelle non batie (en m²)
                enveloppe.insert(3, "s_bati", 2000)# Surface minimale de la parcelle bati (en m²)
                enveloppe.insert(4, "ces_max", 10)# CES maximum de la parcelle bati (en m²)
                global D
                D = {
                       0 : "d_min_route",
                       1 : "s_non_bati",
                       2 : "s_bati",
                       3 : "ces_max"}
                struct_terr.destroy()

            Button(struct_terr, text = 'Valider', width=15, command=champs, bg="orange").grid(row=2, column=1)
            liste_champs.grid(row=1, column=1)
            struct_terr.mainloop()
        else:
            mes_var[nom_variables[x]] = Traitement.clean_data(mes_var[nom_variables[x]], False)
        
            
    # Tab de la Personnalisation
    def param(self):
        tab3 = ttk.Frame(self.tabControl)                    # Création d'un 3e onglet
        self.tabControl.add(tab3, text='Personnalisation')   # Ajout du 3e onglet
        n = 0
        Label(tab3, text = 'Nom de la zone').grid(row=1, column=2)
        Label(tab3, text = 'Distance minimale de la \n parcelle à la route (en m)').grid(row=1, column=3)
        Label(tab3, text = 'Surface minimale de la \n parcelle non batie (en m²)').grid(row=1, column=4)
        Label(tab3, text = 'CES maximum de la \n parcelle bati (en m²)').grid(row=1, column=5)
        Label(tab3, text = 'Surface minimale de la \n parcelle bati (en m²)').grid(row=1, column=6)
        global E
        E = {}      #Le dictionnaire E, va correspondre aux Entry
        global V
        V = {}      #LE dictionnaire V, va correspondre aux Values dans les Entry
        for i in list(enveloppe.index): #Rows
            Label(tab3, text = i).grid(row=2+n, column=1)
            Label(tab3, text = enveloppe[choix_du_champs][i]).grid(row=2+n, column=2)
            V[i] = []
            E[i] = []
            n += 1
            for j in range(4):
                V[i].append(IntVar())
                V[i][j].set(0)
                E[i].append(Entry(tab3, textvariable=V[i][j], width = 10))
                E[i][j].grid(row=1+n, column=j+3)
        # Fonction paramètres par défaut
        def defaut():
            enveloppe.is_copy = False
            for i in list(enveloppe.index):
                V[i][0].set(value1.get())
                V[i][1].set(value2.get())
                V[i][2].set(value3.get())
                V[i][3].set(value4.get())
                for j in D:
                    enveloppe.loc[i, D[j]] = V[i][j].get()
        # Validation des Paramètres personnalisés
        def param_ok():
            enveloppe.is_copy = False
            for i in list(enveloppe.index):
                for j in range(4):
                    enveloppe.loc[i, D[j]] = V[i][j].get()
                    
        # Boutons de la Tab3
        Button(tab3, text='Par défaut', bg = 'grey', command=defaut).grid(row = len(V)+2, column=2)
        Button(tab3, text='Valider', bg = 'orange', command= param_ok).grid(row = len(V)+2, column=3)
        
    
        
    def tabEnveloppe(self):
        tab4 = ttk.Frame(self.tabControl)                    # Création d'un 4e onglet
        self.tabControl.add(tab4, text="Calcul de l'enveloppe urbaine")   # Ajout du 4e onglet
        
        def param_enveloppe():
            global surf_min_AU
            surf_min_AU = value5.get()
            global TamponBati
            TamponBati = value6.get()
            global TailleMiniEnv
            TailleMiniEnv = value7.get()
            
        label5 = Label(tab4, text = 'Taille des trous de l''enveloppe à combler (en m²):')
        label5.grid(row=2, column=2)
        global value5
        value5 = IntVar()
        value5.set(2000)
        entree5 = Entry(tab4, textvariable=value5, width=10)
        entree5.grid(row=2, column=3)

        label6 = Label(tab4, text = 'Choix de la taille du tampon autour du bati isolé (en m²):')
        label6.grid(row=3, column=2)
        global value6
        value6 = IntVar()
        value6.set(30)
        entree6 = Entry(tab4, textvariable=value6, width=10)
        entree6.grid(row=3, column=3)
         
        label7 = Label(tab4, text = 'Choix de la taille minimale des enveloppes à selectionner (en m²):')
        label7.grid(row=4, column=2)
        global value7
        value7 = IntVar()
        value7.set(30)
        entree7 = Entry(tab4, textvariable=value7, width=10)
        entree7.grid(row=4, column=3)
        
        # Boutons de la Tab4
        Button(tab4, text='Valider', bg = 'orange', command = param_enveloppe).grid(row = 6, column=2)
   
   
    # Validation des paramètres par défaut appliqués à toutes les zones
    def defaut_ok(self):
        for i in enveloppe.index:
            enveloppe.loc[i, 'd_min_route'] = value1.get()
            enveloppe.loc[i, 's_non_bati'] = value2.get()
            enveloppe.loc[i, 's_bati'] = value3.get()
            enveloppe.loc[i, 'ces_max'] = value4.get()
            global desserte
            desserte = value1.get()
#        for i in list(nom_variables):
#            if Traitement.typeGeom(mes_var[i]) == 'LineString':
#                param[i] = param[nom_varialbes[i].get()]
      
    
        
class Traitement:
    '''Classe qui va contenir toutes les fonctions du traitements '''
    def __init__(self):
        pass
    
    #Fonction intersection
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

    # ces function to calculate percentage of parcel dedicated to building
    def coeffEmpriseSol(bati, parcelle, *argv) :
        bati = bati.copy()
        parcelle = parcelle.copy()
        parcelle.insert(0, "id_par", range(1, 1 + len(parcelle)))
        intersection = Traitement.spatial_overlays(parcelle, bati, how='intersection')
        dissolve = intersection.dissolve(by="id_par").reset_index()
        dissolve.insert(len(dissolve.columns), "surf_bat", dissolve["geometry"].area)
        dissolve.drop("geometry", axis=1, inplace=True)
        coeff = parcelle.merge(dissolve, how='left', on="id_par", suffixes=('', '_y'))
        coeff.insert(1, "surf_par", coeff["geometry"].area)
        coeff['ces'] = coeff['surf_bat']/coeff['surf_par']*100
        coeff = coeff.fillna(0)
        coeff.insert(len(coeff.columns), "shape", ((coeff.boundary.length)/(2*np.sqrt(np.pi*coeff["surf_par"]))))
        coeff.insert(len(coeff.columns), "shape2", ((coeff.boundary.length)/(np.sqrt(coeff["surf_par"]))))
        for i in list(coeff.columns):
             if i not in ['id_par','surf_par', 'surf_bat', 'ces','shape', 'shape2', 'geometry'] and i not in argv:
                coeff = coeff.drop(i, axis=1)   
        coeff.crs = ('+init=epsg:2154')
        if enregistrer_ces == True:
            coeff.to_file(export + '/' + 'ces.shp')
            print('CES exporté')
        else:
            pass
        return(coeff)
        
    #Sélection des parcelles
    def selectionParcelles(ces):
        parcelle_batie = ces.copy()
        parcelle_vide = ces.copy()
        parcelle_vide = parcelle_vide[(parcelle_vide["ces"] < 0.5) & (parcelle_vide["surf_par"] >= parcelle_vide["s_non_bati"]) & (parcelle_vide["shape"] < 2.5) & (parcelle_vide["shape2"] < 8)]
        parcelle_vide.insert(len(parcelle_vide.columns), "nature", "1")
        parcelle_vide = parcelle_vide[["id_par", choix_du_champs, "ces_max","nature"]]
        parcelle_batie = parcelle_batie[(parcelle_batie["ces"] < parcelle_batie["ces_max"]) & (parcelle_batie["ces"] >= 0.5) & (parcelle_batie["surf_par"] >= parcelle_batie["s_bati"])]
        return(parcelle_vide, parcelle_batie)
  
        
    def positionBati(parcelleBati, parcelleVide, bati, ces, choix_du_champs):
        centroid = parcelleBati.copy()
        centroid["geometry"] = centroid.geometry.centroid
        centroid["geometry"] = centroid.geometry.buffer(1)
        bati_buffer = bati.copy()
        bati_buffer["geometry"] = bati_buffer.geometry.buffer(5)
        intersection = Traitement.spatial_overlays(centroid, bati_buffer, how='intersection')
        intersection = intersection[["id_par"]]
        intersection.insert(len(intersection.columns), "intersect", "1")
        parcelleBati = parcelleBati.merge(intersection, how='left', on='id_par')
        parcelleBati = parcelleBati.fillna('0')
        parcelleBati = parcelleBati[parcelleBati["intersect"] == '0']
        parcelleBati = parcelleBati.set_geometry("geometry")
        parcelleBati = parcelleBati.drop("intersect", axis=1)
        parcelleBati.insert(len(parcelleBati.columns), "nature2", "1")
        parcelleBati = parcelleBati[["id_par", "nature2", choix_du_champs]]
        global potentiel
        potentiel = ces.copy()
        potentiel = potentiel.merge(parcelleBati, how='left', on='id_par')
        potentiel = potentiel.merge(parcelleVide, how='left', on='id_par')
        potentiel = potentiel[(potentiel["nature2"] == "1") | (potentiel["nature"] == "1")]

        potentiel["nature"] = potentiel["nature"].replace('1','parcelle vide')
        potentiel["nature"] = potentiel["nature"].replace(np.nan,'parcelle batie')
        return(potentiel)
   
    # Détection du type de géométrie des filtres
    def typeGeom(filtre):
        echantillon = filtre.loc[0, 'geometry']
        return echantillon.geom_type
        
    
    # Suppression des polygones qui intersectent une couche de filtre
    def suppr_filtre(reference,filtre):
        ref = reference.copy()
        ref.insert(len(ref.columns), "id_temp", range(1, 1 + len(ref)))

        #filtre1 = Traitement.clean_data(filtre)
        filtre1 = filtre.copy()
        filtre1["geometry"] = filtre1.geometry.centroid
        filtre1 = filtre1.set_geometry("geometry")
        filtre1["geometry"] = filtre1.geometry.buffer(1)
        filtre1 = filtre1.set_geometry("geometry").reset_index()

        intersection1 = Traitement.spatial_overlays(filtre1, ref, how='intersection')
        intersection1 = intersection1[["id_temp"]]
        intersection1.insert(1, "intersect", "1")

        ref = ref.merge(intersection1, how='left', on='id_temp')
        ref = ref.fillna('0')
        ref = ref[ref["intersect"] == '0']
        ref = ref.set_geometry("geometry")
        ref = ref.drop("intersect", axis=1)
        ref = ref.drop("id_temp", axis=1)
        return(ref) 

    # Conservation du potentiel à proximité des routes et exclusion des routes cadastrées 
#    def routeDesserte(data):
#            buffer_route = data.copy()
#            buffer_route["geometry"] = buffer_route.geometry.buffer(desserte)
#            buffer_route.insert(0, "desserte",'1')
#            buffer_route = buffer_route.dissolve("desserte", as_index=False)
#            buffer_route = Traitement.clean_data(buffer_route, "desserte")
#            global potentiel
#            potentiel.crs = {'init' : 'epsg:2154'}
#            buffer_route.crs = {'init' : 'epsg:2154'}
#            intersection = Traitement.spatial_overlays(potentiel, buffer_route, how='intersection')
#            intersection = intersection[["id_par", "desserte"]]
#            potentiel = potentiel.merge(intersection, how='left', on='id_par', suffixes=('', '_y'))
#
#            # ### #10 Calcul du ces route
#            # buffer de 5m sur les routes
#            data["geometry"] = data.buffer(5)
#            data = data.set_geometry("geometry")
#            parcelle = mes_var['Parcelles'].copy()
#            parcelle.insert(0, "id_par", range(1, 1 + len(parcelle)))
#            parcelle.insert(1, "surf_par", parcelle["geometry"].area)
#    
#            # CES des routes sur potentiel
#            data.crs = {'init' : 'epsg:2154'}
#            intersection = Traitement.spatial_overlays(data, parcelle, how='intersection')
#            dissolve = intersection.dissolve(by='id_par').reset_index()
#            dissolve.insert(2, "surf_route", dissolve["geometry"].area)
#            dissolve["surf_route"] = dissolve["geometry"].area
#            dissolve.drop("geometry", axis=1, inplace=True)
#            ces_route = parcelle.merge(dissolve, how='left', on='id_par', suffixes=('', '_y'))
#            ces_route['ces_route'] = ces_route['surf_route']/ces_route['surf_par']*100
#            ces_route = ces_route.fillna(0)
#            ces_route = ces_route[['id_par', 'surf_par', 'ces_route', 'geometry']]
           
    def routeDesserte(data, potentiel):
        buffer_route = data.copy()
        buffer_route["geometry"] = buffer_route.geometry.buffer(desserte)
        buffer_route.insert(0, "desserte",'1')
        buffer_route = buffer_route.dissolve("desserte", as_index=False)
        buffer_route = Traitement.clean_data(buffer_route, "desserte")
        print('Buffer autour des routes :OK!\n')
        #global intersection
        intersection = Traitement.spatial_overlays(potentiel, buffer_route, how='intersection')
        print('Intersection entre le potentiel et le buffer des routes : OK!\n')
        intersection = intersection[["id_par", "d_min_route"]]
        potentiel = potentiel.merge(intersection, how='left', on='id_par', suffixes=('', '_y'))
        print("Merge entre l'intersection et le potentiel : OK!\n")
    
        # ### #10 Calcul du ces route
        # buffer de 5m sur les routes
        data["geometry"] = data.buffer(5)
        data = data.set_geometry("geometry")
        parcelle = mes_var['Parcelles'].copy()
        parcelle.insert(0, "id_par", range(1, 1 + len(parcelle)))
        parcelle.insert(1, "surf_par", parcelle["geometry"].area)
    
        # CES des routes sur potentiel
        intersection = Traitement.spatial_overlays(data, parcelle, how='intersection')
        dissolve = intersection.dissolve(by='id_par').reset_index()
        dissolve.insert(2, "surf_route", dissolve["geometry"].area)
        dissolve["surf_route"] = dissolve["geometry"].area
        dissolve.drop("geometry", axis=1, inplace=True)
        ces_route = parcelle.merge(dissolve, how='left', on='id_par', suffixes=('', '_y'))
        ces_route['ces_route'] = ces_route['surf_route']/ces_route['surf_par']*100
        ces_route = ces_route.fillna(0)
        ces_route = ces_route[['id_par', 'surf_par', 'ces_route', 'geometry']]
    
        # Selection de la voirie cadastrée (ces_route >= 40%)
        ces_route = ces_route[(ces_route["ces_route"] >= 40)]
        ces_route.crs = {'init': 'epsg:2154'}
    
        #Suppression du cadastre d'étude de  la voirie cadastrée sélectionnée
        potentiel = gpd.overlay(potentiel, ces_route, how = 'difference')
        return potentiel    
    
#    def Filtrage(potentiel, contrainte) :
#        intersection = Traitement.spatial_overlays(potentiel, contrainte, how='intersection')
#        intersection = intersection[intersection["geometry"].area>1]#Exclusion des surfaces intersectées inférieur à 1m²
#        intersection.insert(len(intersection.columns)
#        
    
    def filtrage(potentiel, contrainte):
        potentiel.crs = {'init': 'epsg:2154'}
        contrainte.crs = {'init': 'epsg:2154'}
        intersection = Traitement.spatial_overlays(potentiel, contrainte, how='intersection')
        intersection = intersection[intersection["geometry"].area > 10]
        liste_id = [i for i in intersection["id_par"]]
        potentiel = potentiel[~potentiel["id_par"].isin(liste_id)]
        return potentiel
            
    
#    def Filtrage(potentiel):
#        allFiltrePoly = []
#        for data in list(mes_var):
#            if data not in ["Parcelles", "Bati", "Structuration territoriale", "Routes", "Voies ferrees"]:
#                if Traitement.typeGeom(mes_var[data]) == 'Polygon' or Traitement.typeGeom(mes_var[data]) == 'MultiPolygon':
#                    allFiltrePoly.append(mes_var(data))
#            else:
#                return "Pas de filtres de type Polygon renseignés."
#        combinePoly = gpd.GeoDataFrame(pd.concat(allFiltrePoly, ignore_index= False, sort=True))
#        combinePoly.crs = allFiltrePoly[0].crs
#        potentiel = Traitement.suppr_filtre(potentiel,combinePoly)
#        print('Traitements des filtres de type Polygon terminé')
#        return potentiel
#        if data not in ["Parcelles", "Bati", "Structuration territoriale", "Routes", "Voies ferrees"]:
#            # Supression des parcelles intersectant les filtres de type Polygon
#            if Traitement.typeGeom(mes_var[data]) == 'Polygon' or Traitement.typeGeom(mes_var[data]) == 'MultiPolygon':
#                allFiltrePoly = [mes_var[i] for i in list(mes_var)]
#                combinePoly = gpd.GeoDataFrame(pd.concat(allFiltrePoly, ignore_index= False, sort=True))
#                combinePoly.crs = allFiltrePoly[0].crs
#                potentiel = Traitement.suppr_filtre(potentiel,combinePoly)
#                print('Traitements des filtres de type Polygon terminé')
#                return potentiel
#                elif typeGeom(mes_var[data]) == 'LineString':
#                    filtreLine = mes_var[data].copy()
#                    filtreLine["geometry"] = filtreLine.buffer(param[data])
#                    potentiel = potentiel[potentiel.disjoint(data.unary_union)]
#                    return potentiel
    
     #Suppression des parcelles intersectant des voies ferrées
    def voiesFerrees(data):
        voie_ferree = mes_var['Voies ferrees'].copy()
        voie_ferree = voie_ferree.copy()
        voie_ferree["geometry"] = voie_ferree.buffer(1)
        #voie_ferree = Traitement.clean_data(voie_ferree)
        data = data[data.disjoint(voie_ferree.unary_union)]
        return data
    
    #Finalisation 
    def finalisation(data):
        #data = Traitement.explodePoly(data)
        data2 = data[(data["nature"] == "parcelle batie") & (data["geometry"].area >= data["s_bati"]) | (data["nature"] == "parcelle vide") & (data["geometry"].area >= data["s_non_bati"])]
        data2["d_min_route"] = data2["d_min_route"].replace(np.nan, 0)
        #data2["desserte"] = data2["desserte"].fillna(0)
        data["d_min_route"] = data["d_min_route"].replace(np.nan, 0)
        data2 = data2[["id_par", "surf_par", "surf_bat", "ces", "shape", "shape2", "d_min_route", "nature", "geometry"]].reset_index()
        data2.crs = {'init': 'epsg:2154'}
        data2.reset_index(drop=True)
        return data2
    
    # Script foncier
    def script():
        t0 = time.process_time()
        print('Lancement du traitement\n')
        
        # ### #6 Prise en compte des zones U
        print("Prise en compte de l'enveloppe Urbaines : ")
        enveloppe_urbaine = Traitement.spatial_overlays(enveloppe, mes_var['Parcelles'], how='intersection')
        enveloppe_urbaine.crs = {'init': 'epsg:2154'}
        #enveloppe_urbaine =  enveloppe_urbaine[enveloppe_urbaine["geometry"].area>=enveloppe_urbaine['s_non_bati']]
        print('OK\n')
        
        # ### #7 Calcul du CES
        print('Calcul du CES : ')
        global ces
        enveloppe_urbaine.crs = {'init': 'epsg:2154'}
        ces = Traitement.coeffEmpriseSol(mes_var['Bati'],enveloppe_urbaine,choix_du_champs, 'd_min_route', 's_non_bati', 'ces_max', 's_bati')
        print('OK\n')
        
        # ### #8 Sélection parcelles
        print('Sélection des parcelles : ')
        parcelle_vide, parcelle_batie = Traitement.selectionParcelles(ces)
        parcelle_vide.crs = {'init': 'epsg:2154'}
        parcelle_batie.crs = {'init': 'epsg:2154'}
        print('OK \n')
        
        # Position du bâti au sein de la parcelle
        print('Position du bâti au sein de la parcelle : ')
        parcelle_batie.crs = {'init': 'epsg:2154'}
        parcelle_vide.crs = {'init': 'epsg:2154'}
        potentiel = Traitement.positionBati(parcelle_batie, parcelle_vide, mes_var['Bati'], ces, choix_du_champs)
        potentiel.crs = {'init': 'epsg:2154'}
        print('OK \n')
        
        # Conservation du potentiel à proximité des routes et exclusion des routes cadastrées
        print('Marquage des parcelles à proximité de la voirie')
        potentiel_2 = Traitement.routeDesserte(mes_var['Routes'], potentiel)
        potentiel_2.crs = {'init': 'epsg:2154'}
        potentiel = potentiel_2
        print('OK \n')
        
        #Filtrage des parcelles à partir des données en entrée
        print('Filtrage des parcelles en fonction des données renseignées :')
        for data in list(mes_var):
            if data not in ["Parcelles", "Bati", "Structuration territoriale", "Routes", "Voies ferrees"]:
                potentiel = Traitement.filtrage(potentiel, mes_var[data])
            else:
                print('Pas de donnée filtre indiquée en entrée')
        potentiel = Traitement.routeDesserte(mes_var['Routes'], potentiel)
        print('OK \n')
        
        # Suppression des parcelles intersectant des voies ferrées
        if 'Voies ferrees' in list(mes_var):
            print('Prise en compte des voies ferrées')
            potentiel.crs = {'init': 'epsg:2154'}
            potentiel = Traitement.voiesFerrees(potentiel)
            print('OK \n')
#            if len(mes_var) > 5 :
#                potentiel.crs = {'init': 'epsg:2154'}
#                print('Prise en compte des filtres techniques : ')
#                Traitement.Filtrage(potentiel)
#                print('OK \n')
#        else:
#            if len(mes_var) > 4 :
#                potentiel.crs = {'init': 'epsg:2154'}
#                print('Prise en compte des filtres techniques : ')
#                Traitement.Filtrage(potentiel)
#                print('OK \n')
            
        # make the geometry a multipolygon if it's not already
        print('Finalisation')
        
        potentiel = Traitement.finalisation(potentiel)    
        potentiel.to_file(export + '/' + "potentiel.shp")
        
        temps = (time.process_time() - t0)/60
        print(" \n Traitement terminé en {} min".format(round(temps, 2)))
        #print("\n Traitement terminé en {min} min et {sec} s! \n ".format(min =round(temps, 2), sec=(round(temps,4) - min)*60))
        temps = time.process_time() - t0
        print("\n Traitement terminé en {} min! \n ".format(round(temps/60, 2)))
        
oop = Appli()
oop.mainloop()
