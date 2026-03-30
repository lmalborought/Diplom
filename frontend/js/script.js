const tabs = document.querySelectorAll('.tab');
const textPanel = document.getElementById('text-panel');
const urlPanel = document.getElementById('url-panel');
const textInput = document.getElementById('text-input');
const urlInput = document.getElementById('url-input');
const submitBtn = document.getElementById('submit-btn');
const resultEl = document.getElementById('result');
const resultClassEl = document.getElementById('result-class');

const API_BASE = '/api/predict';

let mode = 'text';
let pollingInterval = null;

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        mode = tab.dataset.tab;

        textPanel.classList.toggle('active', mode === 'text');
        urlPanel.classList.toggle('active', mode === 'url');

        resultEl.style.display = 'none';
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    });
});

submitBtn.addEventListener('click', async () => {
    const isEmpty = mode === 'text' ? !textInput.value.trim() : !urlInput.value.trim();
    if (isEmpty) {
        showResult('Введите текст или ссылку', true);
        return;
    }

    resultEl.style.display = 'none';
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }

    submitBtn.disabled = true;
    showLoading(true);

    try {
        let response;
        if (mode === 'text') {
            response = await fetch(`${API_BASE}/text`, {
                method: 'POST',
                body: textInput.value.trim(),
                headers: { 'Content-Type': 'text/plain; charset=utf-8' }
            });
        } else {
            response = await fetch(`${API_BASE}/url`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: urlInput.value.trim() })
            });
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сервера');
        }

        const data = await response.json();

        if (data.predicted_class) {
            showResult(data.predicted_class, false);
            submitBtn.disabled = false;
            showLoading(false);
            return;
        }

        if (data.task_id) {
            showResult('⏳ В очереди...', false);
            startPolling(data.task_id);
        } else {
            throw new Error('Неожиданный ответ от сервера');
        }

    } catch (err) {
        showResult(err.message || 'Ошибка соединения с сервером', true);
        submitBtn.disabled = false;
        showLoading(false);
    }
});

function startPolling(taskId) {
    let attempts = 0;
    const maxAttempts = 120;
    const intervalMs = 2000;

    const pollOnce = async () => {
        attempts++;

        try {
            const response = await fetch(`${API_BASE}/task/${encodeURIComponent(taskId)}`);
            const data = await response.json();

            if (data.status === 'completed') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                const predicted =
                    data.result != null && data.result !== ''
                        ? data.result
                        : 'Результат получен';
                showResult(predicted, false);
                submitBtn.disabled = false;
                showLoading(false);
                return;
            }
            if (data.status === 'failed') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                showResult(data.error || 'Ошибка обработки', true);
                submitBtn.disabled = false;
                showLoading(false);
                return;
            }
            if (data.status === 'not_found') {
                clearInterval(pollingInterval);
                pollingInterval = null;
                showResult(data.message || 'Задача не найдена', true);
                submitBtn.disabled = false;
                showLoading(false);
                return;
            }
            if (data.status === 'processing') {
                showResult('🔄 Обработка...', false);
            } else if (data.status === 'pending') {
                showResult('⏳ В очереди...', false);
            }

            if (attempts >= maxAttempts) {
                clearInterval(pollingInterval);
                pollingInterval = null;
                showResult('Превышено время ожидания', true);
                submitBtn.disabled = false;
                showLoading(false);
            }
        } catch (err) {
            showResult('⏳ Ожидание ответа...', false);
            if (attempts >= maxAttempts) {
                clearInterval(pollingInterval);
                pollingInterval = null;
                showResult('Превышено время ожидания', true);
                submitBtn.disabled = false;
                showLoading(false);
            }
        }
    };

    pollOnce();
    pollingInterval = setInterval(pollOnce, intervalMs);
}

function showResult(text, isError = false) {
    resultClassEl.textContent = text;
    resultEl.classList.toggle('error', isError);
    resultEl.style.display = 'block';
}

function showLoading(show) {
    if (show) {
        submitBtn.innerHTML = '⏳ Обработка...';
    } else {
        submitBtn.innerHTML = 'Классифицировать';
    }
}

window.addEventListener('beforeunload', () => {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }
});