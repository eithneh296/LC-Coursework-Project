let entryID = 1; // Auto-incrementing ID

document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("poll-form");

    form.addEventListener("submit", async function(event) {
        event.preventDefault(); // Prevent page reload

        // Get user inputs
        const country = document.getElementById("country").value.trim();
        const happinessResponse = document.querySelector('input[name="happy"]:checked');
        const score = document.getElementById("score").value.trim();

        // Validate inputs
        if (!country || !happinessResponse || !score) {
            alert("Please answer all questions before submitting.");
            return;
        }

        // Ensure score is a number between 1-10
        const scoreValue = parseInt(score, 10);
        if (isNaN(scoreValue) || scoreValue < 1 || scoreValue > 10) {
            alert("Please enter a valid happiness score between 1-10.");
            return;
        }

        // Send data to Flask backend
        let response = await fetch("/userpoll", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({
                country: country,
                happy: happinessResponse.value,
                score: score
            })
        });

        let data = await response.text(); // Receive updated HTML

        // Extract just the table content from the response
        const parser = new DOMParser();
        const doc = parser.parseFromString(data, 'text/html');
        const newTable = doc.querySelector('#results-table');  // Extract table from response

        // Replace only the table with the updated results
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = newTable.outerHTML;  // Replace the table content
    });
});



