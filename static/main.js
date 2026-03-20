async function fetchWithFallback(urls, request) {
    for (let url of urls) {
        try {
            const response = await fetch(url, request);
            if (!response.ok) {
                continue;
            }
            return response; // Success
        } catch (err) {
            // Continue to the next fallback URL
        }
    }
    throw new Error('All fetch attempts failed');
}

async function performAnalysis(input) {
    const response = await fetchWithFallback(['http://127.0.0.1:5000/', 'http://localhost:5000/'], {
        method: 'POST',
        headers: {
            'Content-Type': 'text/plain'
        },
        body: input
    });
    const output = await response.json();
    return output;
}

function updateAnalysis(output) {
    document.getElementById('input-text-id').innerText = output.text;
    document.getElementById('sentiment-id').innerText = output.sentiment;
    document.getElementById('confidence-id').innerText = Math.round(output.confidence * 10000) / 100 + '%';
    document.getElementById('keywords-id').innerText = output.keywords.join(', ');
}

function processInput() {
    const sentimentContainerElement = document.getElementById('sentiment-container-id'),
          hinglishTextareaElement = document.getElementById('hinglish-textarea-id');
    const inputText = hinglishTextareaElement.value.trim();
    if (inputText.length == 0) {
        sentimentContainerElement.style.display = 'none';
        if (hinglishTextareaElement.classList.contains('focus:border-blue-500')) {
            hinglishTextareaElement.classList.remove('border-gray-300');
            hinglishTextareaElement.classList.remove('focus:border-blue-500');
            hinglishTextareaElement.classList.add('border-red-500');
        }
        hinglishTextareaElement.focus();
        return;
    }
    performAnalysis(inputText)
        .then(output => updateAnalysis(output));
    sentimentContainerElement.style.display = 'block';
    if (hinglishTextareaElement.classList.contains('border-red-500')) {
        hinglishTextareaElement.classList.add('border-gray-300');
        hinglishTextareaElement.classList.add('focus:border-blue-500');
        hinglishTextareaElement.classList.remove('border-red-500');
    }
}