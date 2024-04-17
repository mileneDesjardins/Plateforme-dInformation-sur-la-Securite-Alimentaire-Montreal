const DATE_ISO_REGEX = /^\d{4}-\d{2}-\d{2}$/;
const MSG_ERROR_EMPTY = "Veuillez choisir une date.";
const MSG_ERROR_FORMAT_ISO = "Entrez un format valide (JJ-MM-AAAA)";
const MSG_ERROR_DATE_ORDER = "La date de début doit être inférieure à la date de fin."

function areValidDates(startDateID, endDateID) {
    clearMessagesError();
    let startDate = document.getElementById('start-date').value;
    let endDate = document.getElementById('end-date').value;
    let isValid = true;
    if (isEmpty(startDate)) {
        isValid = false;
        handleError(startDateID, MSG_ERROR_EMPTY);
    }
    if (isEmpty(endDate)) {
        isValid = false;
        handleError(endDateID, MSG_ERROR_EMPTY);
    }
    if (!isISO(startDate)) {
        isValid = false;
        handleError(startDateID, MSG_ERROR_FORMAT_ISO)
    }
    if (!isISO(endDate)) {
        isValid = false;
        handleError(endDateID, MSG_ERROR_FORMAT_ISO)
    }

    if (isValid && !isInGoodOrder(startDate, endDate)) {
        isValid = false;
        handleError(startDateID, MSG_ERROR_DATE_ORDER)
    }

    return isValid;
}


function isValidDate(dateID) {
    clearMessagesError();
    let plainteDate = document.getElementById(dateID).value;
    let isValid = true;
    if (isEmpty(plainteDate)) {
        isValid = false;
        handleError(dateID, MSG_ERROR_EMPTY);
    }
    if (isEmpty(plainteDate)) {
        isValid = false;
        handleError(dateID, MSG_ERROR_EMPTY);
    }
    return isValid;
}

function isEmpty(date) {
    return date == null || date === "";
}

function isISO(date) {
    return DATE_ISO_REGEX.test(date);
}


function isInGoodOrder(startDate, endDate) {
    let startDateObj = new Date(startDate);
    let endDateObj = new Date(endDate);
    return startDateObj <= endDateObj;
}

function handleError(errorName, message) {
    let errorText = document.getElementById(`error-${errorName}`);
    errorText.innerHTML = message;
}

function clearMessagesError() {
    let allErrors = document.getElementsByClassName("invalid-feedback");
    for (let error of allErrors) {
        error.innerHTML = '';
    }
}

function isValidSelectDropDown(value) {
    clearMessagesError();

    if (value == 0) {
        handleError("dropdown", "Veuillez sélectionner un établissement.");
        return false;
    }
    return true;
}


