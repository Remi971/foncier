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

//Objet JSON qui va contenir le nom des sources de données, des couches, leur chemin et leurs paramètres pour chacune des variables
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
//Fonction qui lire la courche de structuration territoriale
async function listeColumns(chemin, nom){
  listeStructuration = await eel.structuration_territoriale(chemin, nom)();
}
//Fonction qui va lister les champs de la couche structuration territoriale
async function listeValues(champs){
  listeValeurs = await eel.unique_values(champs)();
}
//fonction qui va récupérer les paramètres définis pour chaque type de la couche structuration territoriale
function recupDonnees(){
  if(document.querySelector('.on')){
  document.querySelector('.on').addEventListener('click', function() {
    let nomColumn = $("tr.titre th:first-child").html();
    console.log(nomColumn);
    mesVar.paramètres.perso.champs = nomColumn;
    const tr = document.querySelectorAll("tr.donnees");
    for (const item of tr) {
      let nodes = item.querySelectorAll('td');
      let first = nodes[0].innerHTML
      let inputs = item.querySelectorAll('input')
      let value0 = parseInt(inputs[0].value);
      let value1 = parseInt(inputs[1].value);
      let value2 = parseInt(inputs[2].value);
      let value3 = parseInt(inputs[3].value);
      let value4 = parseInt(inputs[4].value);
      let value5 = parseInt(inputs[5].value);
      mesVar.paramètres.perso.valeurs[first] = {
          "d_min_route" : value0,
          "non-batie" : value1,
          "batie" : value2,
          "cesMax" : value3,
          "test" : value4,
          "bufBati" : value5,
        }
      };
    mesVar.paramètres.défauts = 'vide';
    console.log(mesVar.paramètres.perso);
    })
  }
}
//Fonction qui va remplir le tableau avec les paramètres de la structuration territoriale avec les valeurs par défaut
function valeursTable(liste){
  const container = document.querySelector("#container1");
  const route = container.querySelector("#route").value;
  const nonBatie = container.querySelector("#non-batie").value;
  const batie = container.querySelector("#batie").value;
  const cesMax = container.querySelector("#cesMax").value;
  const test = container.querySelector("#test").value;
  const bufBati = container.querySelector("#bufBati").value;
  for (const valeur of liste) {
     $('<tr class="donnees" id='+valeur+'><td>'+valeur+'</td><td><input type="number" class="d_min_route" value='+route+'>m</td><td><input type="number" class="non-batie" value='+nonBatie+'>m</td><td><input type="number" class="batie" value='+batie+'>m</td><td><input type="number" class="cesMax" value='+cesMax+'>m</td><td><input type="number" class="test" value='+test+'>m</td><td><input type="number" class="bufBati" value='+bufBati+'>m</td></tr>').appendTo('#table-env');
  }
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
    //Bouton de suppression de filtre
    $(".group .remove").on('click', function(){
      let parent = $(this).parent();
      nom = $(parent).children(".btn-test").html();
      delete mesVar.gpkg.layers[nom];
      delete mesVar.dossier.couches[nom];
      $(this).parent().remove();
    })
  })
  //Bouton de validation de la source de donnée (Dossier ou GPKG)
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
//Fonction qui va attribuer la donnée sélectionnée à la variable associée aux boutons
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
    let exportCes = document.getElementById("ces_check").checked
    if (mesVar.paramètres['défauts'] === "vide" && mesVar.paramètres['perso'] === "vide") {
      let answer = window.confirm("Vous n'avez pas valider les paramètres! Etes vous sûre de lancer le traitement avec les paramètres par défaut?")
      if (answer) {
        eel.lancement(mesVar, exportCes)()
      }
      else {
        return;
      }
    }
    else {
        eel.lancement(mesVar, exportCes)()
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
    mesVar.paramètres.défauts["non-batie"] = paramNonBatie;
    let paramBatie = $("#batie").val();
    mesVar.paramètres.défauts["batie"] = paramBatie;
    let paramCES = $("#cesMax").val();
    mesVar.paramètres.défauts["cesMax"] = paramCES;
    let paramTest = $("#test").val();
    mesVar.paramètres.défauts["test"] = paramTest;
    let paramBufBati = $("#bufBati").val();
    mesVar.paramètres.défauts["bufBati"] = paramBufBati;
    mesVar.paramètres.perso = 'vide'
  })
  $(".off").on('click', function(){
    $("ul#columns").empty();
    listeStructuration.forEach(column => {
      $('<li class="columns"></li>').html(column).appendTo(ulColumns);
      })
    $('#param-confirm').css('visibility', 'visible');
    $('.columnChoice').css('visibility', 'visible');
    this.className = 'btn-test on';
    mesVar.paramètres["perso"] = {
      champs : '',
      valeurs : {},
    };
    recupDonnees();
    $('li.columns').on('click', function(){
      $(this).siblings().removeClass("classLi");
      $(this).toggleClass("classLi");
      let selectColumns = $(".columns.classLi").html();
      $('#table-env').empty();
      $('<tr class="titre"><th>'+selectColumns+'</th><th>Distance minimal à la route</th><th>Surface minimale de la parcelle non bâtie</th><th>Surface minimale de la parcelle bâtie</th><th>CES maximum de la parcelle divisible</th><th>Distance du buffer pour le test</th><th>Distance du buffer autour du bâti</th></tr>').appendTo('#table-env');
      listeValues(selectColumns);
    })
  })
  $('#param-confirm').on('click', function(){
    valeursTable(listeValeurs);
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
