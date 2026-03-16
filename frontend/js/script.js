const tabs = document.querySelectorAll('.tab');
const textPanel = document.getElementById('text-panel');
const urlPanel = document.getElementById('url-panel');
const textInput = document.getElementById('text-input');
const urlInput = document.getElementById('url-input');
const submitBtn = document.getElementById('submit-btn');
const resultEl = document.getElementById('result');
const resultClassEl = document.getElementById('result-class');

const API_URL = 'http://localhost:8000';

let mode = 'text';

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        mode = tab.dataset.tab;

        textPanel.classList.toggle('active', mode === 'text');
        urlPanel.classList.toggle('active', mode === 'url');
    });
});

submitBtn.addEventListener('click', async () => {
    const isEmpty = mode === 'text' ? !textInput.value.trim() : !urlInput.value.trim();
    if (isEmpty) {
        showResult('Введите текст или ссылку', true);
        return;
    }

    submitBtn.disabled = true;
    resultEl.style.display = 'block';

    try {
        let response;
        if (mode === 'text') {
            response = await fetch(`${API_URL}/api/predict/text`, {
                method: 'POST',
                body: textInput.value.trim(),
                headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
        } else {
            response = await fetch(`${API_URL}/api/predict/url`, {
                method: 'POST',
                body: JSON.stringify({ url: urlInput.value.trim() }),
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const data = await response.json();
        const isError = !response.ok || ['Некорректный URL', 'Не удалось получить текст'].includes(data.predicted_class);
        showResult(data.predicted_class, isError);
    } catch (err) {
        showResult('Ошибка соединения с сервером', true);
    } finally {
        submitBtn.disabled = false;
    }
});

function showResult(text, isError = false) {
    resultClassEl.textContent = text;
    resultEl.classList.toggle('error', isError);
}