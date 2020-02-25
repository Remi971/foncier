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

//Objet JSON qui va contenir le nom des sources de données, des couches et leur chemin pour chacune des variables
const mesVar = {
  gpkg:
  {
    nomGPKG:
    {},
    layers:
    {},
  },
  dossier:
  {
    chemin:
    {},
    couches:
    {},
  },
}

// Choix de l'utilisateur pour importer les données à partir d'un dossier ou d'une base de données Geopackage
let data = ''
let liste = []
//Fonction qui récupère le nom du dossier de data
async function pickFolder() {
    data = await eel.selectionDossier()();
    mesVar.dossier.chemin = data;
  }
//Fonction qui récupère le nom du fichier de data gpkg
async function pickGpkg(){
    data = await eel.selectionBDgpkg()();
    mesVar.gpkg.nomGPKG = data;
  }

//Valider le choix de la source de donnée
$(document).ready(function(){
  $("#btn-valid").on('click', function(){
    if ($("select.dossier").val() === "dossier"){
      pickFolder();
      $('#selection').html("<img src='/images/folder.png'>");
    }
  else if ($("select.dossier").val() === "BDgpkg"){
      pickGpkg();
      $('#selection').html("<img src='/images/database.png'>");
    }
  })
  $("#btn-addFilter").on('click', function(){
    let name = prompt("Indiquez le nom du filtre : ")
    $('<div class="group"><button class="btn-test" id='+name+'>'+name+'</button><span id="vf-canvas" class="data-info"></span><button class="remove">X</button></div>').appendTo('.filtres');
    $(".group .remove").on('click', function(){
      $(this).parent().remove();
    })
  })
})

//Fonction qui va lister les données du dossier ou de la BD gpkg
//ET Permettre la sélection de la donnée à attribuer à une variable
let ul = $("ul.data")
async function listingData(){
  liste = [];
  $('li').remove();
  liste = await eel.liste_data(data)();
  liste.forEach(shp => {
    $('<li></li>').html(shp).appendTo(ul);
    })
  $('li').on('click', function(){
    $(this).siblings().removeClass("classLi");
    $(this).toggleClass("classLi");
  })
}

//Fonction qui va attribuer la donnée sélectionnée à la variable associé au boutons
$(document).ready(function(){
  $("#btn-liste").on('click', function(){
    listingData();
  })
  $(".group button").on('click', function(){
    let select = $(".classLi").html();
    let divParent = $(this).parent();
    $(divParent).children("span").html(select);
    let key = $(this).html();
    if (data.endsWith(".gpkg")){
      delete mesVar.dossier.couches[key];
      mesVar.gpkg.layers[key] = select;
    }else{
      delete mesVar.gpkg.layers[key];
      mesVar.dossier.couches[key] = select;
    }
    //mesVar[key] = chemin;
    //eel.add_data(key, chemin)
    //eel.lecture_sig(mesVar);
  })
})
