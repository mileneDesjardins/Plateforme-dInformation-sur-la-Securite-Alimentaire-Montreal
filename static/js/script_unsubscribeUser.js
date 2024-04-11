function unsubscribeUser() {
    var btn = document.getElementById("confirm-unsubscribe-btn");
    var token = btn.getAttribute('data-token');
    var idBusiness = btn.getAttribute('data-id-business');
    var email = btn.getAttribute('data-email');

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
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Affiche le message reçu de l'API
        if (data.success) {
            window.location.href = '/confirmation-unsubscribed-user';
        }
    })
    .catch(error => {
        console.error("Erreur lors de la demande :", error);
    });
}

document.getElementById("confirm-unsubscribe-btn").addEventListener("click", function () {
    unsubscribeUser();
});
