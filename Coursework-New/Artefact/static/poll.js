document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("poll-form");

    form.addEventListener("submit", function(event) {
        const country = document.querySelector("input[name='Country']").value.trim();
        const happinessResponse = document.querySelector("input[name='happy']:checked");
        const score = document.querySelector("input[name='Score']").value.trim();

        if (!country || !happinessResponse || !score) {
            alert("Please answer all questions before submitting.");
            event.preventDefault();
            return;
        }

        const scoreValue = parseInt(score, 7);
        if (isNaN(scoreValue) || scoreValue < 1 || scoreValue > 7) {
            alert("Please enter a valid happiness score between 1-7.");
            event.preventDefault();
            return;
        }

        alert("Thank you! Redirecting to summary...");
    });
});




