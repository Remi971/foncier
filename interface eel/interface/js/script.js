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
let liste = []
//Fonction qui récupère le nom du dossier de data
async function pickFolder() {
    data = await eel.selectionDossier()();
    console.log('Dossier sélectionné : ', data);
  }
//Fonction qui récupère le nom du fichier de data gpkg
async function pickGpkg(){
    data = await eel.selectionBDgpkg()();
    console.log('BD séléctionné : ', data);
  }
//Valider le choix de la source de donnée
$(document).ready(function(){
  $("#btn-valid").on('click', function(){
    if ($("select.dossier").val() === "dossier"){
      pickFolder();
      $("#selection").html("<h3>DOSSIER</h3>");
    }
  else if ($("select.dossier").val() === "BDgpkg"){
      pickGpkg();
      $("#selection").html("<h3>GEOPACKAGE</h3>");
    }
  })
})

//Fonction qui va lister les données du dossier ou de la BD gpkg
async function listingData(){
    liste = await eel.liste_data(data)();
    console.log('Liste des données : ', liste)
}

//Lister les données
//Créer un li dans le ul pour chaque éléments de la liste et incrémenter l'élément dans le li
$(document).ready(function(){
  $("#btn-liste").on('click', function(){
    listingData();
    for (let i = 0; i < liste.length; i++){
      let ul = $("ul.data")
      let li = ul.append("<li></li>")
    }
    $("ul.data").html("<li></li>")
    }

  })
})
var names = [ "Jon", "Nick", "Bill", "Tom" ];
$('#names-list li').each(function (index) {
    $(this).text(names[index]);
});
