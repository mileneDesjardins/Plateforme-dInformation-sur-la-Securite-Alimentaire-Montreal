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
    if (typeof jsonData.nom_complet !== 'string' || jsonData.nom_complet.trim() === '') {
        errors.push('Le nom complet est invalide');
    }
    if (typeof jsonData.courriel !== 'string' || jsonData.courriel.trim() === '') {
        errors.push('L\'adresse courriel est invalide');
    }
    if (!Array.isArray(jsonData.choix_etablissements) || jsonData.choix_etablissements.length === 0) {
        errors.push('Veuillez sélectionner au moins un établissement');
    } else {
        jsonData.choix_etablissements.forEach(id => {
            if (typeof id !== 'number' || isNaN(id)) {
                errors.push('ID d\'établissement invalide');
            }
        });
    }
    if (typeof jsonData.mdp !== 'string' || jsonData.mdp.trim() === '') {
        errors.push('Le mot de passe est invalide');
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
        return;
    }

    // Envoyer la requête à la route /api/new-user
    console.log('Envoi des données au serveur...');
    fetch('/api/new-user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
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
        });
}

document.addEventListener("DOMContentLoaded", function (event) {
    // Ajouter un écouteur d'événements au clic sur le bouton de soumission du formulaire
    document.getElementById('btn-submit-user').addEventListener("click", onSubmitNewUser);
});
