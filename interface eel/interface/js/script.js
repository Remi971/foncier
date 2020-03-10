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
  paramètres:
  {
    défauts:"vide",
    perso: "vide",
  },
}
// Choix de l'utilisateur pour importer les données à partir d'un dossier ou d'une base de données Geopackage
let data = ''
let listeValeurs = []
let listeStructuration = []
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

async function listeColumns(chemin, nom){
  listeStructuration = await eel.structuration_territoriale(chemin, nom)();
}

async function listeValues(champs){
  listeValeurs = await eel.unique_values(champs)();
}

async function valeursTable(liste){
  await liste.forEach((valeur) => {
    $('<tr class="donnees" id='+valeur+'><td>'+valeur+'</td><td><input type="number" class="d_min_route" value="100">m</td><td><input type="number" class="non-batie" value="400">m</td><td><input type="number" class="batie" value="1000">m</td><td><input type="number" class="ces" value="40">m</td></tr>').appendTo('#table-env');
  })
}

async function recupDonnees() {
  let donnees = {
    champs : '',
    param : {
      id : '',
      valeurs : [],
    },
}
  let nomColumn = $("tr.titre th:first-child").html()
  donnees['champs'] = nomColumn;
  let row = $("tr.donnees");
  row.forEach(function(tr){
    donnees.param['id'] = tr.html();
    tr.children('td').forEach(function(element){
      donnees.param['valeurs'].push(element.html());
    })
  })
  console.log(donnees)
}

//Valider le choix de la source de donnée
$(document).ready(function(){
  $("#btn-addFilter").on('click', function(){
    let name = prompt("Indiquez le nom du filtre : ")
    $('<div class="group"><button style= "background-color: #8e1f31"  class="btn-test" id='+name+'>'+name+'</button><button class="remove">X</button><span id="vf-canvas" class="data-info"></span></div>').appendTo('.btn-base');
    $(".group").on('click',".btn-test", function(){
      let select = $(".donnees.classLi").html();
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
    })
    $(".group .remove").on('click', function(){
      let parent = $(this).parent();
      nom = $(parent).children(".btn-test").html();
      delete mesVar.gpkg.layers[nom];
      delete mesVar.dossier.couches[nom];
      $(this).parent().remove();
    })
  })
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
})

//Fonction qui va lister les données du dossier ou de la BD gpkg
//ET Permettre la sélection de la donnée à attribuer à une variable
let ul = $("ul.data")
async function listingData(){
  liste = [];
  $('li.donnees').remove();
  liste = await eel.liste_data(data)();
  liste.forEach(shp => {
    $('<li class="donnees"></li>').html(shp).appendTo(ul);
    })
  $('h4#listeCouches').html('Liste des '+liste.length+' couches')
  $('li.donnees').on('click', function(){
    $(this).siblings().removeClass("classLi");
    $(this).toggleClass("classLi");
  })
}

//Fonction qui va attribuer la donnée sélectionnée à la variable associé au boutons
$(document).ready(function(){
  $("#btn-liste").on('click', function(){
    listingData();
  })
  $(".group").on('click','.btn-test', function(){
    let select = $(".donnees.classLi").html();
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
    if (key === "Structuration territoriale"){
      listeColumns(data, select);
    }
    //mesVar[key] = chemin;
    //eel.add_data(key, chemin)
    //eel.lecture_sig(mesVar);
  })
})

$(document).ready(function() {
  $('#btn-script').on('click', function() {
    if (mesVar.paramètres['défauts'] === "vide" && mesVar.paramètres['perso'] === "vide") {
      let answer = window.confirm("Vous n'avez pas valider les paramètres! Etes vous sûre de lancer le traitement?")
      if (answer) {
        eel.lancement(mesVar['paramètres'])()
      }
      else {
        return;
      }
    }
    else {
      eel.lancement(mesVar['paramètres'])()
    }
  })
})

//PARAMETRES
let ulColumns = $("ul#columns")
$(document).ready(function(){
  $("#valid-param").on("click", function(){
    mesVar.paramètres["défauts"] = {};
    let paramRoute = $("#route").val();
    mesVar.paramètres.défauts["d_min_route"] = paramRoute;
    let paramNonBatie = $("#non-batie").val();
    mesVar.paramètres.défauts["surf_non_batie"] = paramNonBatie;
    let paramBatie = $("#batie").val();
    mesVar.paramètres.défauts["surf_min_batie"] = paramBatie;
    let paramCES = $("#ces").val();
    mesVar.paramètres.défauts["ces_max"] = paramCES;
    mesVar.paramètres.perso = 'vide'
  })
  $("#param-perso").on('click', function(){
    $("ul#columns").empty();
    listeStructuration.forEach(column => {
      $('<li class="columns"></li>').html(column).appendTo(ulColumns);
      })
    $('#param-confirm').css('visibility', 'visible');
    $('.columnChoice').css('visibility', 'visible');
    $('li.columns').on('click', function(){
      $(this).siblings().removeClass("classLi");
      $(this).toggleClass("classLi");
      let selectColumns = $(".columns.classLi").html();
      $('#table-env').empty();
      $('<tr class="titre"><th>'+selectColumns+'</th><th>Distance minimal à la route</th><th>Surface minimale de la parcelle non bâtie</th><th>Surface minimale de la parcelle bâtie</th><th>CES maximum de la parcelle divisible</th></tr>').appendTo('#table-env');
      listeValues(selectColumns);

    })
  })
  $('#param-confirm').on('click', function(){
    valeursTable(listeValeurs);
    recupDonnees();
  })
})

//VISUALISATION map
let mymap = L.map('mapid').setView([43.947991, 4.80875], 13);
let Esri_WorldImagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});
let OpenStreetMap_Mapnik = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});
Esri_WorldImagery.addTo(mymap);
$(document).ready(function() {
  $("#btn-map").on('click', function() {
    setTimeout(function() { mymap.invalidateSize()}, 1);
  })
})

function onMapClick(e) {
    alert("You clicked the map at " + e.latlng);
}

mymap.on('click', onMapClick);
