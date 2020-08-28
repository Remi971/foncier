function ready(fn) {
  if (document.readyState != 'loading'){
    fn();
  }else {
    document.addEventListener('DOMContentLoaded', fn);
  }
}

async function exportResultat(mesVar, batiMin, dilatation, erosion, bufbati_env, callback) {
  result = await eel.enveloppe_urbaine(mesVar, batiMin, dilatation, erosion, bufbati_env)();
  callback(result);
}
function avertissement(valeur) {
  if (valeur === true){
    alert("Données exportées dans le geopackage app_fonciere/data/resultats.gpkg");
    $("#calcul_env").css('background-color', '#aaf2b6');
  }else{
    alert("Aucune donnée, veuillez lancer un traitement")
    $("#calcul_env").css('background-color', 'red')
  }
}

ready(function() {
  el = document.getElementById("calcul_env");
  el.addEventListener('click', function(callback) {
    const batiMin = document.querySelector("#min-bati").value;
    const dilatation = document.querySelector('#dilatation').value;
    const erosion = document.querySelector('#erosion').value;
    const bufbati_env = document.querySelector('#bufbati_env').value;
    exportResultat(mesVar, batiMin, dilatation, erosion, bufbati_env, avertissement);
  })
})
