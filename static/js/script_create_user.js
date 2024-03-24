function onSubmitNewUser() {
    // Créer le JSON à envoyer
    console.log("fffff");
    var jsonToSend = createJson();

    // Envoyer la requête à la route /api/new-user
    fetch('/api/new-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonToSend
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                console.error('Erreur lors de la création du compte');
                throw new Error('Erreur lors de la création du compte');
            }
        })
        .then(data => {
            console.log('Données créées avec succès:', data);
            onCreateUserSubmit();
            window.location.href = '/confirmation-new-user';
        })
        .catch(error => {
            console.error('Erreur:', error.message);
        });
}

// Fonction pour créer le JSON à partir des données du formulaire
function createJson() {
    var formData = new FormData(document.querySelector('form'));
    var jsonData = {};
    formData.forEach(function (value, key) {
        jsonData[key] = value;
    });
    console.log(jsonData);
    console.log("allo");
    return JSON.stringify(jsonData);
}

// Ajouter un écouteur d'événements au clic sur le bouton de soumission du formulaire
document.getElementById('btn-submit-user').addEventListener("click", onSubmitNewUser);
