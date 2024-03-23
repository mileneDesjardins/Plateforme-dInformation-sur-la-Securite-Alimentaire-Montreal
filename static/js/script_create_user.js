function create_user() {
    document.querySelector('form').addEventListener('submit', function (e) {
        e.preventDefault(); // Empêche l'envoi standard du formulaire

        // Récupérer les données du formulaire
        var formData = new FormData(this);

        // Convertir les données en JSON
        var jsonData = {};
        formData.forEach(function (value, key) {
            jsonData[key] = value;
        });

        // Créer une requête XMLHttpRequest
        var xhr = new XMLHttpRequest();

        // Ouvrir une requête asynchrone POST vers /api/new-user
        xhr.open('POST', '/api/new-user', true); // Le troisième paramètre à true indique une requête asynchrone

        // Définir le type de contenu de la requête
        xhr.setRequestHeader('Content-Type', 'application/json');

        // Gérer la réponse de la requête
        xhr.onreadystatechange = function () {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 201) {
                    // Conversion de la réponse JSON en objet JavaScript
                    var responseData = JSON.parse(xhr.responseText);
                    // Utiliser les données comme nécessaire
                    console.log('Données créées avec succès:', responseData);
                    // Appeler la fonction onCreateUserSubmit
                    onCreateUserSubmit(); // Appeler la fonction après la création de l'utilisateur
                    // Rediriger l'utilisateur vers la page de confirmation
                    window.location.href = '/confirmation-user';
                } else {
                    console.error('Erreur lors de la création du compte');
                }
            }
        };

        // Envoyer les données JSON
        xhr.send(JSON.stringify(jsonData));

        // Ajouter un écouteur d'événements au clic sur le bouton de soumission du formulaire
        document.getElementById('btn-submit-plainte').addEventListener("click", onCreateUserSubmit);

    });
}
