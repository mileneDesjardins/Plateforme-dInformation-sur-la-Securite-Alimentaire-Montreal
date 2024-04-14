let etablissementInput = document.getElementById('plainte-etablissement');
let adresseInput = document.getElementById('plainte-adresse');
let villeInput = document.getElementById('plainte-ville');
let dateVisiteInput = document.getElementById('plainte-date');
let nomCompletClientInput = document.getElementById('plainte-nom-complet');
let descriptionInput = document.getElementById('plainte-description');


etablissementInput.addEventListener('input', removeInvalidClass);
adresseInput.addEventListener('input', removeInvalidClass);
villeInput.addEventListener('input', removeInvalidClass);
dateVisiteInput.addEventListener('input', removeInvalidClass);
nomCompletClientInput.addEventListener('input', removeInvalidClass);
descriptionInput.addEventListener('input', removeInvalidClass);

function removeInvalidClass(event) {
    let input = event.target;
    input.classList.remove('is-invalid');
    input.nextElementSibling.innerText = '';
}
function onSubmitPlainte() {
    if (checkInputsFilled()) {
        jsonToSend = createJson();
        sendQueryPlainte(jsonToSend);
    }
}

function checkInputsFilled() {
    let etablissementValid = validateInputFilled(etablissementInput);
    let adresseValid = validateInputFilled(adresseInput);
    let villeValid = validateInputFilled(villeInput);
    let dateVisiteValid = validateInputFilled(dateVisiteInput);
    let nomCompletClientValid = validateInputFilled(nomCompletClientInput);
    let descriptionValid = validateInputFilled(descriptionInput);

    return etablissementValid && adresseValid && villeValid && dateVisiteValid && nomCompletClientValid && descriptionValid;
}

function validateInputFilled(input) {
    let isValid = input.checkValidity();
    if (!isValid) {
        input.classList.add('is-invalid');
        input.nextElementSibling.innerText = 'Veuillez remplir ce champ.';
    }
    return isValid;
}


function isFilled() {
    let etablissementInput = document.getElementById('plainte-etablissement');
    let formIsValid = etablissementInput.checkValidity();
    return formIsValid;
}

function createJson() {
    let etablissement = etablissementInput.value;
    let adresse = adresseInput.value;
    let ville = villeInput.value;
    let date_visite = dateVisiteInput.value;
    let nom_complet_client = nomCompletClientInput.value;
    let description = descriptionInput.value;
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

document.getElementById('btn-submit-plainte').addEventListener("click", onSubmitPlainte);