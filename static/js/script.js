function onFastSearchSubmit(){
    let date1 = document.getElementById('date-du').value
    let date2 = document.getElementById('date-au').value

    let resultAffiche = document.getElementById("result-fast-search")
    let apiUrl = `/api/contrevenants?du=${date1}&au=${date2}`;
    console.log(apiUrl)
    fetch(apiUrl)
        .then(response => response.json())
        .then(response => {
            console.log(response)
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        })

}

function traiterJson(response){


}


function countContraventions(contraventions) {
    let occurenceEtablissements = {};

    contraventions.forEach(contravention => {
        let etablissement = contravention.etablissement;
        if (occurenceEtablissements.hasOwnProperty(etablissement)) {
            occurenceEtablissements[etablissement]++;
        } else {
            occurenceEtablissements[etablissement] = 1;
        }
    });

    return occurenceEtablissements;
}

document.getElementById('fast-search').addEventListener("click", onFastSearchSubmit);
