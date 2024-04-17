// Fonction pour créer le JSON à partir des données du formulaire
function createJson() {
    var formData = new FormData(document.getElementById('user-form'));
    var selectedIds = Array.from(formData.getAll('choix_etablissements')).map(Number); // Convertir les chaînes en entiers

    var jsonData = {
        nom_complet: formData.get('nom_complet') || '', // Assurer que les valeurs sont des chaînes
        courriel: formData.get('courriel') || '',
        mdp: formData.get('mdp') || '',
        choix_etablissements: selectedIds
    };

    return jsonData;
}

// Fonction pour valider le JSON par rapport au schéma
function validateJson(jsonData) {
    // Comparer avec le schéma de validation
    const errors = [];
    // Validation pour le nom complet
    if (typeof jsonData.nom_complet !== 'string' || jsonData.nom_complet.trim().length < 3 || jsonData.nom_complet.trim().length > 50) {
        errors.push('Le nom complet doit contenir entre 3 et 50 caractères');
    }
    // Validation pour l'adresse courriel
    const emailRegex = /^[\w.+-]+@([\w-]+\.)+[\w-]{2,4}$/;
    if (typeof jsonData.courriel !== 'string' || !emailRegex.test(jsonData.courriel)) {
        errors.push('L\'adresse courriel est invalide ou ne respecte pas le format attendu');
    }
    // Validation pour les choix d'établissements
    if (!Array.isArray(jsonData.choix_etablissements) || jsonData.choix_etablissements.length === 0) {
        errors.push('Veuillez sélectionner au moins un établissement');
    } else {
        jsonData.choix_etablissements.forEach(id => {
            if (typeof id !== 'number' || isNaN(id)) {
                errors.push('ID d\'établissement invalide');
            }
        });
    }
    // Validation pour le mot de passe
    if (typeof jsonData.mdp !== 'string' || jsonData.mdp.length < 5 || jsonData.mdp.length > 20) {
        errors.push('Le mot de passe doit contenir entre 5 et 20 caractères');
    }

    return errors;
}

function onSubmitNewUser(event) {
    event.preventDefault();

    // Créer le JSON à envoyer
    var jsonData = createJson();
    console.log('Données du formulaire:', jsonData);

    // Valider le JSON par rapport au schéma
    var validationErrors = validateJson(jsonData);
    if (validationErrors.length > 0) {
        console.error('Erreurs de validation:', validationErrors);
        displayErrors(validationErrors); // Afficher les erreurs sur la page
        return;
    }

    // Envoyer la requête à la route /api/new-user
    console.log('Envoi des données au serveur...');
    fetch('/api/new-user', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(jsonData)
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
            window.location.href = '/confirmation-new-user';
        })
        .catch(error => {
            console.error('Erreur:', error.message);
            displayErrors([error.message]); // Affiche les erreurs renvoyées par le serveur
        });
}

document.addEventListener("DOMContentLoaded", function (event) {
    // Ajouter un écouteur d'événements au clic sur le bouton de soumission du formulaire
    document.getElementById('btn-submit-user').addEventListener("click", onSubmitNewUser);
});

function displayErrors(errors) {
    const errorContainer = document.getElementById('error-container');
    errorContainer.innerHTML = ''; // Clear previous errors
    if (errors.length > 0) {
        errorContainer.style.display = 'inline-block'; // Make sure the
        // container is visible
    } else {
        errorContainer.style.display = 'none'; // Hide if no errors
        return;
    }

    errors.forEach(error => {
        const errorElement = document.createElement('p');
        errorElement.textContent = error;
        errorElement.style.margin = '0';  // Enlever la marge
        errorContainer.appendChild(errorElement);
    });
}

