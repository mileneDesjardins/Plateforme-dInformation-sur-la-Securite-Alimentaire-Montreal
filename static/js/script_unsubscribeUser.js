function unsubscribeUser() {
    var token = "{{ token }}"; // Ajoutez ici la manière de récupérer le token si nécessaire
    var idBusiness = "{{ id_business }}";
    var email = "{{ email }}";

    var requestData = {
        token: token,
        id_business: idBusiness,
        email: email
    };

    fetch("/api/unsubscribe", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (response.ok) {
            return response.text(); // Renvoie la réponse du serveur
        }
        throw new Error("Erreur lors de la demande : " + response.status);
    })
    .then(message => {
        // Afficher la réponse de la requête AJAX
        alert(message);
        // Rediriger vers une autre page ou effectuer d'autres actions si nécessaire
    })
    .catch(error => {
        console.error("Erreur lors de la demande :", error);
    });
}

// Ajouter un gestionnaire d'événements au bouton de confirmation
document.getElementById("confirm-unsubscribe-btn").addEventListener("click", function () {
    unsubscribeUser();
});
