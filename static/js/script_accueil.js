function onFastSearchSubmit() {
    let startDate = document.getElementById('start-date').value;
    let endDate = document.getElementById('end-date').value;

    if (!areValidDates('start-date', 'end-date')) {
        return;
    }
    let resultAffiche = document.getElementById("result-fast-search");
    resultAffiche.innerHTML = '';
    let apiUrl = `/api/contrevenants/start/${startDate}/end/${endDate}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let tableURL = `/search-by-dates`;
            return fetch(tableURL, {
                method: 'POST',  // Méthode POST pour envoyer des données JSON
                headers: {
                    'Content-Type': 'application/json'  // Type de contenu JSON
                },
                body: JSON.stringify(data)  // Envoyer l'objet JSON dans le corps de la requête
            });
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('result-fast-search').innerHTML = htmlContent;

        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        });
}


function OnGetInfoEtablissementSubmit() {
    let etablissement = document.getElementById('select-etablissement').value;
    let apiUrl = `/api/info-etablissement/${etablissement}`;

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            let modalURL = `/modal`;
            return fetch(modalURL, {
                method: 'POST',  // Méthode POST pour envoyer des données JSON
                headers: {
                    'Content-Type': 'application/json'  // Type de contenu JSON
                },
                body: JSON.stringify(data)  // Envoyer l'objet JSON dans le corps de la requête
            });
        })
        .then(response => response.text())
        .then(htmlContent => {
            document.getElementById('modal-content').innerHTML = htmlContent;
        })
        .catch(err => {
            console.log("Erreur côté serveur", err);
        });
}


function countContraventions(contraventions) {
    let occurenceEtablissements = {};

    Object.values(contraventions).forEach(contravention => {
        let etablissement = contravention.etablissement;
        if (occurenceEtablissements.hasOwnProperty(etablissement)) {
            occurenceEtablissements[etablissement]++;
        } else {
            occurenceEtablissements[etablissement] = 1;
        }
    });

    return occurenceEtablissements;
}


// Creer la table HTML
function creerTable(data, resultAffiche) {

    const table = document.createElement("table");
    table.classList.add("table", "table-striped", "table-bordered", "table-sm");
    const thead = creerEnteteTable();
    const tbody = creerCorpsTable(data);
    table.appendChild(thead);
    table.appendChild(tbody);
    resultAffiche.appendChild(table);
}

// Creer en-tete de la table
function creerEnteteTable() {
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const th1 = creerCelluleEntete("Établissement");
    const th2 = creerCelluleEntete("Nombre de contraventions");

    headerRow.appendChild(th1);
    headerRow.appendChild(th2);
    thead.appendChild(headerRow);

    return thead;
}

// Creer corps de la table
function creerCorpsTable(data) {
    const tbody = document.createElement("tbody");

    // Appel de la fonction countContraventions avec les données JSON
    const resultTable = countContraventions(data);

    // Remplir les données de la table avec les résultats de countContraventions
    for (const etablissement in resultTable) {
        const row = document.createElement("tr");
        const td1 = creerCelluleDonnee(etablissement);
        const td2 = creerCelluleDonnee(resultTable[etablissement]);

        row.appendChild(td1);
        row.appendChild(td2);
        tbody.appendChild(row);
    }

    return tbody;
}

function creerCelluleEntete(texte) {
    const th = document.createElement("th");
    th.textContent = texte;
    return th;
}

function creerCelluleDonnee(texte) {
    const td = document.createElement("td");
    td.textContent = texte;
    return td;
}


document.getElementById('btn-fast-search').addEventListener("click", onFastSearchSubmit);
document.getElementById('btn-info-etablissement').addEventListener("click", OnGetInfoEtablissementSubmit);
