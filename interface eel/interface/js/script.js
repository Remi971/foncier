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
    défauts:{},
    perso: {},
  },
}
// Choix de l'utilisateur pour importer les données à partir d'un dossier ou d'une base de données Geopackage
let data = ''
let liste = []
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

//Valider le choix de la source de donnée
$(document).ready(function(){
  $("#btn-addFilter").on('click', function(){
    let name = prompt("Indiquez le nom du filtre : ")
    $('<div class="group"><button style= "background-color: #8e1f31"  class="btn-test" id='+name+'>'+name+'</button><button class="remove">X</button><span id="vf-canvas" class="data-info"></span></div>').appendTo('.btn-base');
    $(".group").on('click',".btn-test", function(){
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
    if (key === "Structuration territoriale"){
      listeColumns(data, select);
    }
    //mesVar[key] = chemin;
    //eel.add_data(key, chemin)
    //eel.lecture_sig(mesVar);
  })
})

//PARAMETRES
let ulColumns = $("ul#columns")
$(document).ready(function(){
  $("#valid-param").on("click", function(){
    let paramRoute = $("#route").val();
    mesVar.paramètres.défauts["d_min_route"] = paramRoute;
    let paramNonBatie = $("#non-batie").val();
    mesVar.paramètres.défauts["surf_non_batie"] = paramNonBatie;
    let paramBatie = $("#batie").val();
    mesVar.paramètres.défauts["surf_min_batie"] = paramBatie;
    let paramCES = $("#ces").val();
    mesVar.paramètres.défauts["ces_max"] = paramCES;
  })
  $("#param-perso").on('click', function(){
    $('li.columns').remove();
    listeStructuration.forEach(column => {
      $('<li class="columns"></li>').html(column).appendTo(ulColumns);
      })
    $('#param-confirm').css('visibility', 'visible')
    $('li.columns').on('click', function(){
      $(this).siblings().removeClass("classLi");
      $(this).toggleClass("classLi");
    })
  })
  $('#param-confirm').on('click', function(){
    //fonction python pour lister les valeurs uniques du champs correspondant
  })
})
