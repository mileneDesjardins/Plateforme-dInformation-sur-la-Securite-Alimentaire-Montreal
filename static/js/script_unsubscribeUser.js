
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
            return response.text(); // Renvoie la r�ponse du serveur
        }
        throw new Error("Erreur lors de la demande : " + response.status);
    })
    .then(message => {
        // Afficher la r�ponse de la requ�te AJAX
        alert(message);
        // Rediriger vers une autre page ou effectuer d'autres actions si n�cessaire
    })
    .catch(error => {
        console.error("Erreur lors de la demande :", error);
    });
}

// Ajouter un gestionnaire d'�v�nements au bouton de confirmation
document.getElementById("confirm-unsubscribe-btn").addEventListener("click", function () {
    unsubscribeUser();
});
