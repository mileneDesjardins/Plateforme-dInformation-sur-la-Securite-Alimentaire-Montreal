const MSG_NOTHING_TO_MODIFY = "Aucune modification à apporter."
const MSG_SUCESS_MODIF = "Les modifications ont été apportées avec succès."
const MSG_ERREUR_MODIF = "Les modifications n'ont pu être apportées."

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
    let textResponse = document.getElementById('reponse-requete');
    textResponse.innerHTML = "";
    sendModifContrevenant(textResponse);
    sendModifContravention(textResponse);
}


function sendModifContrevenant(textResponse) {
    contrevenantToSend = getInfoContrevenant();
    if (!isObjectEmpty(contrevenantToSend)) {
        idBusiness = document.getElementById('modif-id-business').value;
        let modifContrevenantURL = `/api/contrevenants/${idBusiness}`;
        sendPost(modifContrevenantURL, contrevenantToSend)
            .then(response => {
                if (response.ok) {
                    textResponse.innerHTML = MSG_SUCESS_MODIF;

                } else {
                    textResponse.innerHTML = MSG_ERREUR_MODIF;
                }
            })
    }
}

function sendModifContravention(textResponse) {
    contraventionsToSend = getInfoContraventions();
    console.log("contra " + contraventionsToSend);
    if (!isArrayEmpty(contraventionsToSend)) {
        idBusiness = document.getElementById('modif-id-business').value;
        let modifContrevenantURL = `/api/contraventions/${idBusiness}`;
        console.log(JSON.stringify(contraventionsToSend));
        sendPatch(modifContrevenantURL, contraventionsToSend)
            .then(response => {
                if (response.ok) {
                    textResponse.innerHTML = MSG_SUCESS_MODIF;
                } else {
                    textResponse.innerHTML = MSG_ERREUR_MODIF;
                }
            })
    } else {
        textResponse.innerHTML = MSG_NOTHING_TO_MODIFY;
    }
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

function getInfoContraventions() {
    tableRows = document.getElementById('modif-contravention-table').rows.length;
    let formArray = [];
    for (let i = 1; i < tableRows; i++) {
        formData = {}
        let montant = document.getElementById(`modif-montant-${i}`).value;
        let dateVisite = document.getElementById(`modif-date-visite-${i}`).value;
        let dateJugement = document.getElementById(`modif-date-jugement-${i}`).value;

        let categorie = document.getElementById(`modif-categorie-${i}`).value;
        let description = document.getElementById(`modif-description-${i}`).value;
        let idBusiness = document.getElementById(`modif-id-business`).value;
        let idPoursuite = document.getElementById(`modif-id-poursuite-${i}`).value;

        if (dateVisite !== '') {
            formData['date'] = dateVisite;
        }
        if (dateJugement !== '') {
            formData['date_jugement'] = dateJugement;
        }
        if (montant !== '') {
            formData['montant'] = montant;
        }
        if (categorie !== '') {
            formData['categorie'] = categorie;
        }
        if (description !== '') {
            formData['description'] = description;
        }

        if (!isObjectEmpty(formData)) {
            formData['id_poursuite'] = idPoursuite;
            formData['id_business'] = idBusiness;
            formArray.push(formData);
        }

    }
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
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(objectToSend)
    });
}


function sendPost(URL, objectToSend) {
    return fetch(URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(objectToSend)
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



