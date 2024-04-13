const MSG_NOTHING_TO_MODIFY = "Aucune modification à apporter.";
const MSG_SUCESS_MODIF = "Modifications enregistrée ";
const MSG_ERREUR_MODIF = "Modifications annulées";
const MSG_SUCCES_DELETE_CONTREVENANT = "Le contrevenant a bien été supprimé.";
const MSG_ERROR_DELETE_CONTREVENANT = "Une erreur est survenue, le contrevenant n'a pu être supprimé."
const MSG_SUCCES_DELETE_CONTRAVENTION = "La contravention a bien été supprimée.";
const MSG_ERROR_DELETE_CONTRAVENTION = "Une erreur est survenue, la contravention n'a pu être supprimée."


function onFastSearchSubmit() {
    let startDate = document.getElementById('start-date').value;
    let endDate = document.getElementById('end-date').value;

    if (!areValidDates('start-date', 'end-date')) {
        return;
    }
    document.getElementById("result-fast-search").innerHTML = '';
    let apiUrl = `/api/contrevenant?start-date=${startDate}&end-date=${endDate}`;

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
            console.log("Erreur côté serveur", err); //TODO afficher message
        });
}

function OnGetInfoEtablissementSubmit() {
    let id_business = document.getElementById('select-etablissement').value;
    let apiUrl = `/api/contrevenant/${id_business}`;

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
            console.log("Erreur côté serveur", err); //TODO afficher message
        });
}


function OnSaveModificationSubmit() {
    let textResponse = document.getElementById('reponse-requete');
    textResponse.innerHTML = "";
    sendModifContrevenant(textResponse);
}


function sendModifContrevenant(textResponse) {
    contrevenantToSend = getInfoContrevenant();
    if (!isObjectEmpty(contrevenantToSend)) {
        idBusiness = document.getElementById('modif-id-business').value;
        let modifContrevenantURL = `/api/contrevenant/${idBusiness}`;
        sendPatch(modifContrevenantURL, contrevenantToSend)
            .then(response => {
                if (response.ok) {
                    textResponse.innerHTML = `<span style="color: #149804; font-weight: bold;">${MSG_SUCESS_MODIF}</span>`;
                    onFastSearchSubmit();
                } else {
                    textResponse.innerHTML = `<span style="color: #c70101; font-weight: bold;">${MSG_ERREUR_MODIF}</span>`;
                }
            })
    }
}




function isObjectEmpty(jsonObj) {
    return Object.keys(jsonObj).length === 0;
}



function getInfoContrevenant() {
    let formData = {}
    let etablissement = document.getElementById('modif-etablissement').value;
    let proprietaire = document.getElementById('modif-proprietaire').value;
    let adresse = document.getElementById('modif-adresse').value;
    let statut = document.getElementById('modif-statut').value;
    let dateStatut = document.getElementById('modif-date_statut').value;

    if (proprietaire !== '') {

        formData['proprietaire'] = proprietaire;
    }

    if (etablissement !== '') {
        formData['etablissement'] = etablissement;
    }

    if (adresse !== '') {
        formData['adresse'] = adresse;
    }

    if (statut !== '') {
        formData['statut'] = statut;
    }

    if (dateStatut !== '') {
        formData['date_statut'] = statut;
    }
    console.log(formData);
    return formData;
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
            addEventListenerOnSVGDeletes();
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);  //TODO afficher message
        })
}


function OnDeleteContrevenant() {
    let textResponse = document.getElementById('reponse-requete');
    textResponse.innerHTML = "";
    idBusiness = document.getElementById('modif-id-business').value;
    apiURL = `/api/contrevenant/${idBusiness}`
    const request = new Request(apiURL, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    fetch(request).then(response => {
        if (response.ok) {
            textResponse.innerHTML = MSG_SUCCES_DELETE_CONTREVENANT
            onFastSearchSubmit();
        } else {
            textResponse.innerHTML = MSG_ERROR_DELETE_CONTREVENANT
        }
    })
}


function OnDeleteContravention(svgId) {
    let textResponse = document.getElementById('reponse-requete');
    textResponse.innerHTML = "";
    let row = svgId.charAt(svgId.length - 1);
    let idPoursuite = document.getElementById(`modif-id-poursuite-${row}`).value;
    let apiURL = `/api/contravention/${idPoursuite}`
    const request = new Request(apiURL, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    fetch(request).then(response => {
        if (response.ok) {
            textResponse.innerHTML = MSG_SUCCES_DELETE_CONTRAVENTION;
            onFastSearchSubmit();
        } else {
            textResponse.innerHTML = MSG_ERROR_DELETE_CONTRAVENTION;
        }
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

function addEventListenerOnSVGDeletes() {
    document.getElementById(`svg-delete-contrevenant`).addEventListener(`click`, OnDeleteContrevenant);
    document.querySelectorAll('svg.delete').forEach(svg => {
        svg.addEventListener("click", () => OnDeleteContravention(svg.id))
    })
}



