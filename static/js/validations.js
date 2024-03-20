const DATE_ISO_REGEX = /^\d{4}-\d{2}-\d{2}$/;
const MSG_ERROR_EMPTY = "Veuillez choisir une date.";

function areValidDates(startDateID, endDateID) {
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
    isValid = !isEmpty(startDate) && !isEmpty(endDate);
    isValid = isValid && isISO(startDate) && isISO(endDate);
    isValid = isValid && isGoodOrder(startDate, endDate);
    return isValid;
}


function isEmpty(date) {
    return date == null || date === "";
}

function isISO(date) {
    console.log(DATE_ISO_REGEX.test(date));
    return DATE_ISO_REGEX.test(date);
}


function isGoodOrder(startDate, endDate) {
    let startDateObj = new Date(startDate);
    let endDateObj = new Date(endDate);
    console.log(startDateObj <= endDateObj);
    return startDateObj <= endDateObj;
}

function handleError(errorName, message) {
    let errorText = document.getElementById(`error-${errorName}`);
    errorText.innerHTML = message;
}



