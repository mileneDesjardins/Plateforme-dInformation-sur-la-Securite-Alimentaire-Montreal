function onFastSearchSubmit() {
    let startDate = document.getElementById('start-date').value;
    let endDate = document.getElementById('end-date').value;

    if (!areValidDates('start-date', 'end-date')) {
        return;
    }
    document.getElementById("result-fast-search").innerHTML = '';
    let apiUrl = `/api/contrevenants/start/${startDate}/end/${endDate}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableURL = `/search-by-dates/${startDate}/${endDate}`;
            return sendPost(tableURL, data);
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('result-fast-search').innerHTML = htmlContent;
            addEventListenersOnCells();
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
            return sendPost(modalURL, data);
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('modal-content').innerHTML = htmlContent;
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        });
}

function OnSaveModificationSubmit() {
    contrevenant = getInfoContrevenant();
    contrevenantToSend = JSON.stringify(contrevenant);
    idBusiness = document.getElementById('modif-id-business').value;

    if (!isObjectEmpty(contrevenant)) {
        let modifContrevenantURL = `/api/contrevenant/${idBusiness}`;
        sendPatch(modifContrevenantURL, contrevenant)
            .then(response => {

            })
    }

    contraventions = getInfoContravention();
    contraventionsToSend = JSON.stringify(contraventions);
    if (!isArrayEmpty(contraventions)) {
        idPoursuite = document.getElementById('modif-id-business');
    }
    console.log("good");
}

function isObjectEmpty(jsonObj) {
    return Object.keys(jsonObj).length === 0;
}

function isArrayEmpty(jsonArray) {
    return jsonArray.length === 0;
}

function getInfoContrevenant() {
    let formData = {}
    let etablissement = document.getElementById('modal-dates').value;
    let proprietaire = document.getElementById('modif-proprietaire').value;
    let adresse = document.getElementById('modif-adresse').value;
    let ville = document.getElementById('modif-ville').value;
    let statut = document.getElementById('modif-statut').value;
    let dateStatut = document.getElementById('modif-date_statut').value;

    if (proprietaire !== '') {

        formData['proprietaire'] = proprietaire;
    }
    /*
    if (etablissement !== '') {
        console.log("ici");
        formData['etablissement'] = etablissement;
    }
*/
    if (adresse !== '') {
        formData['adresse'] = adresse;
    }

    if (ville !== '') {
        formData['ville'] = adresse;
    }

    if (statut !== '') {
        formData['statut'] = statut;
    }

    if (dateStatut !== '') {
        formData['date_statut'] = statut;
    }

    return formData;
}

function getInfoContravention() {
    let formArray = [];
    let inputs = document.querySelectorAll('#form-modif-contravention input[type="text"]');

    inputs.forEach(input => {
        let id = input.getAttribute('id');
        let value = input.value.trim();

        if (value !== '') {
            let formData = {
                id: id,
                value: value
            };
            formArray.push(formData);
        }
    });

    return formArray;
}



function openModalModifier(id_business, startDate, endDate) {
    let apiURL = `/modal-dates/${id_business}/${startDate}/${endDate}`;
    fetch(apiURL)
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById("modal-content-modif").innerHTML = htmlContent;
            let modal = new bootstrap.Modal(document.getElementById('modal-date'));
            modal.show(modal);
            document.getElementById('btn-save-modifs-contrevenant').addEventListener('click', OnSaveModificationSubmit);
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        })
}


function sendPatch(URL, objectToSend) {
    return fetch(URL, {
        method: 'PATCH',  // Méthode POST pour envoyer des données JSON
        headers: {
            'Content-Type': 'application/json'  // Type de contenu JSON
        },
        body: JSON.stringify(objectToSend)  // Envoyer l'objet JSON dans le corps de la requête
    });
}


function sendPost(URL, objectToSend) {
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


function addEventListenersOnCells() {
    document.querySelectorAll('#table-dates-results td.cursor-pointer').forEach(cell => {
        cell.addEventListener("click", function () {
            let id_business = cell.getAttribute("data-id-business")
            let startDate = document.getElementById('start-date').value;
            let endDate = document.getElementById('end-date').value;
            openModalModifier(id_business, startDate, endDate);
        });
    });
}



