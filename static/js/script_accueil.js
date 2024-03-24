function onFastSearchSubmit() {
    let startDate = document.getElementById('start-date').value;
    let endDate = document.getElementById('end-date').value;

    if (!areValidDates('start-date', 'end-date')) {
        return;
    }
    let resultAffiche = document.getElementById("result-fast-search");
    resultAffiche.innerHTML = '';
    let apiUrl = `/api/contrevenants/start/${startDate}/end/${endDate}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableURL = `/search-by-dates/${startDate}/${endDate}`;
            return fetchTemplate(tableURL, data);
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('result-fast-search').innerHTML = htmlContent;
            document.querySelectorAll('#table-dates-results td').forEach(cell => {
                cell.addEventListener("click", function () {
                    console.log("ok");
                });
            });
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        });
}

function OnGetInfoEtablissementSubmit() {
    let etablissement = document.getElementById('select-etablissement').value;
    let apiUrl = `/api/info-etablissement/${etablissement}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let modalURL = `/modal`;
            return fetchTemplate(modalURL, data);
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('modal-content').innerHTML = htmlContent;
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        });
}


function fetchTemplate(URL, objectToSend) {
    return fetch(URL, {
        method: 'POST',  // Méthode POST pour envoyer des données JSON
        headers: {
            'Content-Type': 'application/json'  // Type de contenu JSON
        },
        body: JSON.stringify(objectToSend)  // Envoyer l'objet JSON dans le corps de la requête
    });
}


document.getElementById('btn-fast-search').addEventListener("click", onFastSearchSubmit);
document.getElementById('btn-info-etablissement').addEventListener("click", OnGetInfoEtablissementSubmit);


