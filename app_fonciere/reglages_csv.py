import csv

donnees = {
    "gpkg": {
        "nomGPKG": {},
        "layers": {}
        },
    "dossier": {
        "chemin": "C:/Users/Citadia/Dev/projet_foncier/foncier/data",
        "couches": {
            "Bâti": "BATI_region.shp",
            "Parcelles": "PARCELLE_region.shp",
            "Structuration territoriale": "ZONE U PLUi_ENNEZAT.shp"}
            },
    "paramètres": {
        "défauts": "vide",
        "perso": {
            "champs": "LIBELLE",
            "valeurs": {
                "UAa": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UAi": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UCv": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UE": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UG": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UJ": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8},
                "UR": {"non-batie": 400, "batie": 1000, "cesMax": 40, "test": 10, "bufBati": 8}
                }
            },
        "filtres": {}
        }
    }

def export_reglages_csv(data):
    with open('reglages.csv', 'w', newline='') as csvfile:
        fieldname = ['Source','non-batie', 'batie', 'cesMax', 'test', 'bufBati']
        thewriter = csv.DictWriter(csvfile, fieldnames=fieldname, delimiter=';',
                                quotechar = '|', quoting=csv.QUOTE_MINIMAL)
        thewriter.writeheader()
        if data["paramètres"]["défauts"] != "vide":

        if data["paramètres"]["défauts"] != "vide":
            thewriter.writerow({'non-batie' : data["paramètres"]['défauts']['non-batie'],
                                'batie' : data["paramètres"]['défauts']['batie'],
                                'cesMax' : data["paramètres"]['défauts']['cesMax'],
                                'test' : data["paramètres"]['défauts']['test'],
                                'bufBati' : data["paramètres"]['défauts']['bufBati'],
                                 'Source'})
