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
    let nom_client = document.getElementById('plainte-nom').value;
    let prenom_client = document.getElementById('plainte-prenom').value;
    let description = document.getElementById('plainte-description').value;

        console.log(date_visite);
    let plainteJson = {
        etablissement: etablissement,
        adresse: adresse,
        ville: ville,
        date_visite: date_visite,
        nom_client: nom_client,
        prenom_client: prenom_client,
        description: description
    };
    console.log(JSON.stringify(plainteJson));
    return JSON.stringify(plainteJson);
}


function sendQueryPlainte(json) {
    console.log(json)
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/demande-inspection', false)
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(json);

    if (xhr.status === 201) {
        window.location.href = '/plainte-envoyee';

    } else {
        // afficher erreur survenue avec serveur
        console.log("ererur");
    }

}

document.getElementById('btn-submit-plainte').addEventListener("click", onPlainteSubmit);