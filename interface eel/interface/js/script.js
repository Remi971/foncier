function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }

// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

//Objet qui va contenir les noms des variables
const nomVariables = {
  0 : 'Unité foncière',
  1 : 'Parcelles',
  2 : 'Bati',
  3 : 'Structuration territoriale'
}

//Objet qui va contenir un shape pour chacune des variables comprise dans l'objet nomVariables
const mesVar = {}

// Choix de l'utilisateur pour importer les données à partir d'un dossier ou d'une base de données Geopackage
let data = ''
//Fonction qui récupère le nom du dossier de data
async function pickFolder() {
            let choixDossier = await eel.selectionDossier()();
            console.log(choixDossier);
            data = choixDossier;
          }
//Fonction qui récupère le nom du fichier de data gpkg
async function pickGpkg(){
            let choixGpkg = await eel.selectionBDgpkg()();
            console.log(choixGpkg);
            data = choixGpkg;
          }

//Valider le choix de la source de donnée
$(document).ready(function(){
  $("#btn-valid").on('click', function(){
    if ($("select")[0].value === "dossier"){
      pickFolder();
      $("#selection").html("<h3>DOSSIER</h3>");
    }
  else if ($("select")[0].value === "BDgpkg"){
      pickGpkg();
      $("#selection").html("<h3>DOSSIER</h3>");
    }
  })
})
