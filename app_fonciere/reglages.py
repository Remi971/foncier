from docx import Document
#from docx.shared import Inches POUR les images

def exportReglages(data):
    document = Document()
    # TITRE
    document.add_heading('Réglages', 0)
    #Nom de la source de donnée et noms des couches utilisées
    if data["gpkg"]["nomGPKG"] != {}:
        document.add_heading(f'Base de données Geopackage : {data["gpkg"]["nomGPKG"]}', level=2)
        for layer in data["gpkg"]["layers"]:
            document.add_paragraph(f'{layer} : {data["gpkg"]["layers"][layer]}', style='List Bullet')

    if data["dossier"]["chemin"] != {}:
        document.add_heading(f'Base de données dans le dossier : {data["dossier"]["chemin"]}', level=2)
        for couche in data["dossier"]["couches"]:
            document.add_paragraph(f'{couche} : {data["dossier"]["couches"][couche]}', style='List Bullet')
    #Paramètres
    document.add_heading('Paramètres', 1)
    table = document.add_table(rows=1, cols=6)
    table.style = 'LightGrid-Accent1'
    hdr_cells = table.rows[0].cells
    if data["paramètres"]["perso"] != 'vide':
        hdr_cells[0].text = data["paramètres"]["perso"]["champs"]
    else:
        hdr_cells[0].text ='Enveloppe'
    hdr_cells[1].text = "Surface minimal de la parcelle non bâtie"
    hdr_cells[2].text = "Surface minimale de la parcelle bâtie"
    hdr_cells[3].text = "CES maximum de la parcelle divisible"
    hdr_cells[4].text = "Distance du buffer pour le test"
    hdr_cells[5].text = "Distance du buffer autour du bâti"
    #import pdb; pdb.set_trace()
    if data["paramètres"]["perso"] != 'vide':
        for k, v in data["paramètres"]["perso"]["valeurs"].items():
            row_cells = table.add_row().cells
            row_cells[0].text = k
            row_cells[1].text = str(v["non-batie"])
            row_cells[2].text = str(v["batie"])
            row_cells[3].text = str(v["cesMax"])
            row_cells[4].text = str(v["test"])
            row_cells[5].text = str(v["bufBati"])
    else:
        row_cells = table.add_row().cells
        row_cells[0].text = 'Enveloppe'
        row_cells[1].text = str(data["paramètres"]["défauts"]["non-batie"])
        row_cells[2].text = str(data["paramètres"]["défauts"]["batie"])
        row_cells[3].text = str(data["paramètres"]["défauts"]["cesMax"])
        row_cells[4].text = str(data["paramètres"]["défauts"]["test"])
        row_cells[5].text = str(data["paramètres"]["défauts"]["bufBati"])

    document.add_picture('/interface/images/Logo_Citadia.png')

    document.save('reglages.docx')
