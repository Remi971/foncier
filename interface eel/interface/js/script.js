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

//A REVOIR =>

$(document).ready(function(){
  $("#btn-folder").on('click', function(){
    eel.selectionDossier();
    $("#selection").html("<h3>DOSSIER</h3>");
  })
})

$(document).ready(function(){
  $("#btn-gpkg").on('click', function(){
    eel.selectionBDgpkg();
    $("#selection").html("<h3>GEOPACKAGE</h3>");
  })
})
// $(document).ready(function(){
//   $("#valider").on('click', function(){
//     if (document.getElementById("choix").value === "dossier"){
//       $(document).ready(function(){
//         eel.selectionDossier();
//       })
//     }else if (document.getElementById("choix").value === "BDgpkg"){
//       $(document).ready(function(){
//         eel.sectionBDgpkg();
//       })
//     }
//   })
// })
//
// if (document.getElementById("choix").value === 'dossier'){
//   $(document).ready(function(){
//     $("#selection").html("<h3>DOSSIER</h3>")
//   })
// }else if (document.getElementById("choix").value === "BDgpkg"){
//   $(document).ready(function(){
//     $("#selection").html("<h3>Geopackage</h3>")
//   })
// }
//


//
// $(document).ready(function(){
//   $("#valider").on('click', function(){
//     if (document.getElementById("choix").value === "dossier"){
//       eel.selectionDossier()().then(function (value) {
//         const source = value;
//         const divImage = document.createElement("div");
//         divImage.id = "folder";
//         $("#sourceName").text(source);
//         const createDiv = document.getElementById("selection").appendChild(divImage);
//   })
//     }else if (document.getElementById("choix").value === "BDgpkg"){
//
//
//
//       eel.selectionBDgpkg()().then(function (value){
//         const source = value;
//         const divImage = document.createElement("div");
//         divImage.id = "folder";
//         $("#sourceName").text(source);
//         const createDiv = document.getElementById("selection").appendChild(divImage);
//         })}
//   })
// })


/*
// function importDonnees(){
//   if (document.getElementById("choix").value === "dossier"){
//     eel.selectionDossier()().then(function (value) {
//       const source = value;
//       const divImage = document.createElement("div");
//       divImage.id = "folder";
//       $("#sourceName").text(source);
//       const createDiv = document.getElementById("selection").appendChild(divImage);
//     })
//   } else if (document.getElementById("choix").value === "BDgpkg"){
//     const source = eel.selectionBDgpkg();
//     window.divImage = document.createElement("div");
//     divImage.id = "database";
//     document.getElementById("selection").appendChild(divImage);
// }
// }*/
