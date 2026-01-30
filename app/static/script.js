const tweetInput = document.getElementById('tweetInput');
const predictButton = document.getElementById('predictButton');
const resultDiv = document.getElementById('result');
const loadingMessage = document.getElementById('loadingMessage');
const resultMessage = document.getElementById('resultMessage');
const sentimentSpan = document.getElementById('sentiment');
const confidenceSpan = document.getElementById('confidence');
const modelUsedSpan = document.getElementById('modelUsed');
const feedbackButtons = document.getElementById('feedbackButtons');
const thumbsUpButton = document.getElementById('thumbsUp');
const thumbsDownButton = document.getElementById('thumbsDown');
const feedbackMessage = document.getElementById('feedbackMessage');
const modelSelect = document.getElementById('modelSelect');

let currentPrediction = null;

// Fetch available models on page load
fetch('/models')
    .then(response => response.json())
    .then(data => {
        modelSelect.innerHTML = '';
        data.models.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model.toUpperCase();
            if (model === data.default) {
                option.selected = true;
            }
            modelSelect.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error fetching models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
    });

predictButton.addEventListener('click', () => {
    const tweetText = tweetInput.value;
    const selectedModel = modelSelect.value;

    if (tweetText.trim() === "") {
        alert("Please enter a tweet!");
        return;
    }

    predictButton.disabled = true;
    predictButton.textContent = 'Predicting...';

    loadingMessage.textContent = 'Analysing sentiments...';
    loadingMessage.style.display = 'block';
    resultMessage.style.display = 'none';
    feedbackButtons.style.display = 'none';
    feedbackMessage.style.display = 'none';

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: tweetText, model: selectedModel })
    })
    .then(response => response.json())
    .then(data => {
        resultDiv.style.display = 'block';
        resultMessage.style.display = 'block';
        sentimentSpan.textContent = data.label;
        confidenceSpan.textContent = data.confidence.toFixed(2);
        modelUsedSpan.textContent = data.model.toUpperCase();
        feedbackButtons.style.display = 'block';
        loadingMessage.style.display = 'none';

        currentPrediction = {
            text: tweetText,
            label: data.label,
            confidence: data.confidence,
            model: data.model
        };
    })
    .catch(error => {
        console.error('Error:', error);
        alert("An error occurred. Please try again.");
    })
    .finally(() => {
        predictButton.disabled = false;
        predictButton.textContent = 'Predict Sentiment';
    });
});

thumbsUpButton.addEventListener('click', () => {
    sendFeedback(true);
});

thumbsDownButton.addEventListener('click', () => {
    sendFeedback(false);
});

function sendFeedback(isCorrect) {
    if (!currentPrediction) return;

    fetch('/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ...currentPrediction,
            correct: isCorrect
        })
    })
    .then(response => {
        if (response.ok) {
            feedbackButtons.style.display = 'none';
            feedbackMessage.textContent = 'Thank you for your feedback!';
            feedbackMessage.style.display = 'block';
            currentPrediction = null;
        } else {
            throw new Error("Failed to submit feedback.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error submitting feedback.");
    });
}
