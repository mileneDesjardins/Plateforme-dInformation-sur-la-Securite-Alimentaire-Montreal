
function unsubscribeUser() {
    var idBusiness = "{{ id_business }}";
    var email = "{{ email }}";
    fetch("/unsubscribe-user/" + idBusiness + "/" + email, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
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
