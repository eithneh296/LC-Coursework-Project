document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("poll-form");

    form.addEventListener("submit", function(event) {
        // Get user inputs
        const country = document.querySelector("input[name='Country']").value.trim();
        const happinessResponse = document.querySelector("input[name='happy']:checked");  // Fixed
        const score = document.querySelector("input[name='Score']").value.trim();

        // Validate inputs
        if (!country || !happinessResponse || !score) {
            alert("Please answer all questions before submitting.");
            event.preventDefault();
            return;
        }

        // Ensure score is between 1-10
        const scoreValue = parseInt(score, 10);
        if (isNaN(scoreValue) || scoreValue < 1 || scoreValue > 10) {
            alert("Please enter a valid happiness score between 1-10.");
            event.preventDefault();
            return;
        }

        alert("Thank you! Redirecting to summary...");
    });
});




