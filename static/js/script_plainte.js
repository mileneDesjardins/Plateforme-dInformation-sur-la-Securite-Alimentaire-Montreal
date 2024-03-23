function onPlainteSubmit() {
    /*
    * if (!isValidDate('plainte-date')) {
        return;
    }
    * */
    jsonToSend = createJson();
    sendQueryPlainte(jsonToSend);
}


function createJson() {
    let etablissement = document.getElementById('plainte-etablissement').value;
    let adresse = document.getElementById('plainte-adresse').value;
    let ville = document.getElementById('plainte-ville').value;
    let date_visite = document.getElementById('plainte-date').value;
    let nom_complet_client = document.getElementById('plainte-nom-complet').value;
    let description = document.getElementById('plainte-description').value;
    let plainteJson = {
        etablissement: etablissement,
        adresse: adresse,
        ville: ville,
        date_visite: date_visite,
        nom_complet_client: nom_complet_client,
        description: description
    };
    return JSON.stringify(plainteJson);
}


function sendQueryPlainte(json) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/demande-inspection', false)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(json);

    if (xhr.status === 201) {
        window.location.href = '/plainte-envoyee';

    } else if (xhr.status === 400) {
        // afficher autres erreurs
        console.log("erreur format et/ou structure JSON");
    } else {
        console.log("erreur serveur")
    }

}

document.getElementById('btn-submit-plainte').addEventListener("click", onPlainteSubmit);