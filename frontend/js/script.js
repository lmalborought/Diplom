console.log("SCRIPT START");
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM LOADED");
    const tabs = document.querySelectorAll('.tab');
    const textPanel = document.getElementById('text-panel');
    const urlPanel = document.getElementById('url-panel');
    const textInput = document.getElementById('text-input');
    const urlInput = document.getElementById('url-input');
    const submitBtn = document.getElementById('submit-btn');
    const clearBtn = document.getElementById('clear-btn');
    const resultEl = document.getElementById('result');
    const resultClassEl = document.getElementById('result-class');
    const resultBadge = document.getElementById('result-badge');
    const resultLabel = document.getElementById('result-label');
    const resultExtra = document.getElementById('result-extra');
    const taskTrack = document.getElementById('task-track');
    const taskHint = document.getElementById('task-hint');
    const charCount = document.getElementById('char-count');
    const wordCountEl = document.getElementById('word-count');
    const charHint = document.getElementById('char-hint');
    const wordBarFill = document.getElementById('word-bar-fill');

    const stepEls = Array.from(document.querySelectorAll('.step'));
    const stepById = Object.fromEntries(stepEls.map((el) => [el.dataset.step, el]));

    const API_BASE = '/api/predict';
    const MIN_WORDS = 100;

    const submitDefaultLabel = submitBtn.querySelector('.btn-label').textContent;

    let mode = 'text';
    let pollingInterval = null;

    function setTabs(nextMode) {
        mode = nextMode;
        tabs.forEach((t) => {
            const active = t.dataset.tab === mode;
            t.classList.toggle('active', active);
            t.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        textPanel.classList.toggle('active', mode === 'text');
        urlPanel.classList.toggle('active', mode === 'url');
    }

    function formatChars(n) {
        const abs = Math.abs(n) % 100;
        const last = abs % 10;
        if (abs >= 11 && abs <= 14) return `${n} символов`;
        if (last === 1) return `${n} символ`;
        if (last >= 2 && last <= 4) return `${n} символа`;
        return `${n} символов`;
    }

    function formatWords(n) {
        const abs = Math.abs(n) % 100;
        const last = abs % 10;
        if (abs >= 11 && abs <= 14) return `${n} слов`;
        if (last === 1) return `${n} слово`;
        if (last >= 2 && last <= 4) return `${n} слова`;
        return `${n} слов`;
    }

    function countWords(text) {
        const t = text.trim();
        if (!t) return 0;
        return t.split(/\s+/).filter(Boolean).length;
    }

    function updateTextStats() {
        const raw = textInput.value;
        const n = raw.length;
        const words = countWords(raw);
        charCount.textContent = formatChars(n);
        wordCountEl.textContent = `${formatWords(words)} · мин. ${MIN_WORDS}`;
        const ok = words >= MIN_WORDS;
        charHint.textContent = ok
            ? `Минимум ${MIN_WORDS} слов выполнен.`
            : `Нужно не менее ${MIN_WORDS} слов (сейчас ${words}).`;
        charHint.classList.toggle('hint-warn', !ok);
        charHint.classList.toggle('hint-ok', ok);
        if (wordBarFill) {
            const pct = Math.min(100, Math.round((words / MIN_WORDS) * 100));
            wordBarFill.style.width = `${pct}%`;
            wordBarFill.classList.toggle('is-complete', ok);
        }
        syncSubmitDisabled();
    }

    function syncSubmitDisabled() {
        if (submitBtn.classList.contains('is-loading')) {
            submitBtn.disabled = true;
            return;
        }
        const blocked = mode === 'text' && countWords(textInput.value) < MIN_WORDS;
        submitBtn.disabled = blocked;
    }

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            setTabs(tab.dataset.tab);
            hideResult();
            stopPolling();
            syncSubmitDisabled();
        });
    });

    textInput.addEventListener('input', updateTextStats);

    textInput.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        if (e.shiftKey || e.ctrlKey || e.metaKey || e.altKey) return;
        if (e.isComposing) return;
        e.preventDefault();
        submit();
    });

    urlInput.addEventListener('keydown', (e) => {
        if (e.key !== 'Enter') return;
        if (e.isComposing) return;
        e.preventDefault();
        submit();
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            textInput.value = '';
            urlInput.value = '';
            updateTextStats();
            hideResult();
            stopPolling();
            setLoading(false);
        });
    }

    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
    }

    function hideResult() {
        resultEl.style.display = 'none';
        resultEl.classList.remove('error');
    }

    function setBadge(kind, text) {
        resultBadge.textContent = text;
        resultBadge.className = 'pill';
        if (kind === 'muted') resultBadge.classList.add('pill-muted');
        if (kind === 'warn') resultBadge.classList.add('pill-warn');
        if (kind === 'ok') resultBadge.classList.add('pill-ok');
        if (kind === 'bad') resultBadge.classList.add('pill-bad');
    }

    function setStepState(status) {
        const pendingEl = stepById.pending;
        const processingEl = stepById.processing;
        const doneEl = stepById.done;

        [pendingEl, processingEl, doneEl].forEach((el) => {
            if (!el) return;
            el.classList.remove('is-active', 'is-done');
        });

        if (status === 'pending') {
            pendingEl.classList.add('is-active');
        } else if (status === 'processing') {
            pendingEl.classList.add('is-done');
            processingEl.classList.add('is-active');
        } else if (status === 'completed') {
            pendingEl.classList.add('is-done');
            processingEl.classList.add('is-done');
            doneEl.classList.add('is-done');
        }
    }

    function showError(message) {
        resultEl.style.display = 'block';
        resultEl.classList.add('error');
        taskTrack.style.display = 'none';
        setBadge('bad', 'ошибка');
        resultLabel.textContent = 'Сообщение';
        resultClassEl.textContent = message;
        resultExtra.style.display = 'none';
    }

    function showImmediateClass(predicted, metaText) {
        resultEl.style.display = 'block';
        resultEl.classList.remove('error');
        taskTrack.style.display = 'none';
        setBadge('ok', 'готово');
        resultLabel.textContent = 'Предсказанный класс';
        resultClassEl.textContent = predicted;
        if (metaText) {
            resultExtra.textContent = metaText;
            resultExtra.style.display = 'block';
        } else {
            resultExtra.style.display = 'none';
        }
        taskHint.textContent = '';
    }

    function beginAsyncTask() {
        resultEl.style.display = 'block';
        resultEl.classList.remove('error');
        taskTrack.style.display = 'block';
        setBadge('warn', 'в работе');
        resultLabel.textContent = 'Классификация';
        resultClassEl.textContent = '—';
        resultExtra.style.display = 'none';
        taskHint.textContent = 'Запрос принят. Статус обновляется автоматически.';
        setStepState('pending');
    }

    function updateAsyncHint(status) {
        if (status === 'pending') taskHint.textContent = 'В очереди на обработку…';
        else if (status === 'processing') taskHint.textContent = 'Идёт обработка текста и инференс модели…';
        else taskHint.textContent = '';
    }

    async function readErrorMessage(response) {
        try {
            const j = await response.json();
            if (typeof j.detail === 'string') return j.detail;
            if (Array.isArray(j.detail)) {
                return j.detail
                    .map((x) => (x && typeof x === 'object' ? x.msg || JSON.stringify(x) : String(x)))
                    .join('; ');
            }
            if (j.message) return String(j.message);
            return JSON.stringify(j);
        } catch {
            return response.statusText || 'Ошибка сервера';
        }
    }

    function setLoading(show) {
        submitBtn.classList.toggle('is-loading', show);
        submitBtn.setAttribute('aria-busy', show ? 'true' : 'false');
        submitBtn.querySelector('.btn-label').textContent = show ? 'Обработка…' : submitDefaultLabel;
        if (show) {
            submitBtn.disabled = true;
        } else {
            syncSubmitDisabled();
        }
    }

    submitBtn.addEventListener('click', submit);

    document.addEventListener('keydown', (e) => {
        if (!(e.ctrlKey || e.metaKey) || e.key !== 'Enter') return;
        const active = document.activeElement;
        if (active === textInput || active === urlInput) {
            e.preventDefault();
            submit();
        }
    });

    async function submit() {
        if (mode === 'text') {
            const t = textInput.value.trim();
            if (!t) {
                showError('Введите текст.');
                return;
            }
            const words = countWords(t);
            if (words < MIN_WORDS) {
                showError(`Нужно не менее ${MIN_WORDS} слов (сейчас: ${words}).`);
                return;
            }
        } else if (!urlInput.value.trim()) {
            showError('Введите ссылку.');
            return;
        }

        stopPolling();
        hideResult();

        setLoading(true);

        try {
            let response;
            if (mode === 'text') {
                response = await fetch(`${API_BASE}/text`, {
                    method: 'POST',
                    body: textInput.value.trim(),
                    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
                });
            } else {
                response = await fetch(`${API_BASE}/url`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlInput.value.trim() }),
                });
            }

            if (!response.ok) {
                const msg = await readErrorMessage(response);
                throw new Error(msg);
            }

            const data = await response.json();

            if (data.predicted_class) {
                showImmediateClass(data.predicted_class);
                setLoading(false);
                return;
            }

            if (data.task_id) {
                beginAsyncTask();
                if (data.status === 'processing') setStepState('processing');
                startPolling(String(data.task_id));
            } else {
                throw new Error('Неожиданный ответ от сервера');
            }
        } catch (err) {
            showError(err.message || 'Ошибка соединения с сервером');
            setLoading(false);
        }
    }

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
                    stopPolling();
                    setStepState('completed');
                    setBadge('ok', 'готово');
                    resultLabel.textContent = 'Предсказанный класс';
                    const predicted =
                        data.result != null && data.result !== '' ? data.result : 'Результат получен';
                    resultClassEl.textContent = predicted;
                    taskHint.textContent = '';
                    if (data.cached) {
                        resultExtra.textContent = 'Ответ из кэша';
                        resultExtra.style.display = 'block';
                    } else {
                        resultExtra.style.display = 'none';
                    }
                    setLoading(false);
                    return;
                }

                if (data.status === 'failed') {
                    stopPolling();
                    showError(data.error || 'Ошибка обработки');
                    setLoading(false);
                    return;
                }

                if (data.status === 'not_found') {
                    stopPolling();
                    showError(data.message || 'Задача не найдена');
                    setLoading(false);
                    return;
                }

                if (data.status === 'processing') {
                    setStepState('processing');
                    updateAsyncHint('processing');
                } else if (data.status === 'pending') {
                    setStepState('pending');
                    updateAsyncHint('pending');
                }

                if (attempts >= maxAttempts) {
                    stopPolling();
                    showError('Превышено время ожидания');
                    setLoading(false);
                }
            } catch {
                if (attempts >= maxAttempts) {
                    stopPolling();
                    showError('Превышено время ожидания');
                    setLoading(false);
                }
            }
        };

        pollOnce();
        pollingInterval = setInterval(pollOnce, intervalMs);
    }

    updateTextStats();

    window.addEventListener('beforeunload', () => {
        stopPolling();
    });
});