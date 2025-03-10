function validateForm() {
    const continent = document.getElementById("continent").value;
    if (continent === "") {
        alert("Please type a continent name!");
        return false;
    }
    document.getElementById("confirmation-message").style.display = "block";
    return true;
}

setTimeout(function() {
    document.getElementById("confirmation-message").style.display = "none";
}, 5000);

function showPollResult() {
    const continent = document.getElementById("continent").value;
    const resultDiv = document.getElementById("poll-result");
    resultDiv.innerHTML = `<h3>Your selected continent is: ${continent}</h3>`;
    resultDiv.style.display = 'block';  // Show the result div
}