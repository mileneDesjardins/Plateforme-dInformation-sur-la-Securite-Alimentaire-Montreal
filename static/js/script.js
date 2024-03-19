
function onFastSearchSubmit(){
    console.log("ok")
    let date1 = document.getElementById('date-du')
    let date2 = document.getElementById('date-au')
    let resultsText = document.getElementById("result-fast-search")
    let apiUrl = `/api/contrevenants?date1=${date1}&date2=${date2}`;
    fetch(apiUrl)
        .then(response => response.json())
        .then(response => {
            console.log(response)
            let test = JSON.parse(response)
            console.log(test)
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        })

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

document.getElementById('fast-search').addEventListener("click",onFastSearchSubmit())
