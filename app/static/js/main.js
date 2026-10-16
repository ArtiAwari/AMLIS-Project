/**
 * Legal Document Category Prediction - Interactive Client Application Logic
 */

// Utility: Show Alert / Toast
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    const bgClass = type === 'success' ? 'bg-success text-white' : 
                    type === 'error' ? 'bg-danger text-white' : 
                    type === 'warning' ? 'bg-warning text-dark' : 'bg-primary text-white';

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center ${bgClass} border-0 mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    toastContainer.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
}

// -------------------------------------------------------------
// 1. CLASSIFICATION PAGE LOGIC
// -------------------------------------------------------------
let currentPredictionResult = null;

function initClassifyPage() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const selectedFileBadge = document.getElementById('selected-file-badge');
    const fileNameSpan = document.getElementById('selected-file-name');
    const removeFileBtn = document.getElementById('remove-file-btn');
    const rawTextArea = document.getElementById('raw-text-input');
    const classifyBtn = document.getElementById('classify-btn');
    const loadingSpinner = document.getElementById('classify-spinner');
    const resultsPanel = document.getElementById('results-panel');

    let activeFile = null;

    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileSelection(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files && fileInput.files[0]) {
                handleFileSelection(fileInput.files[0]);
            }
        });
    }

    function handleFileSelection(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'txt') {
            showToast('Unsupported file type. Please choose a .pdf or .txt document.', 'error');
            return;
        }
        activeFile = file;
        if (fileNameSpan) fileNameSpan.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        if (selectedFileBadge) selectedFileBadge.classList.remove('d-none');
        if (rawTextArea) rawTextArea.value = ''; // prioritize file
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', () => {
            activeFile = null;
            if (fileInput) fileInput.value = '';
            if (selectedFileBadge) selectedFileBadge.classList.add('d-none');
        });
    }

    // Quick Sample Loaders
    const sampleButtons = document.querySelectorAll('.btn-load-sample');
    sampleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const sampleType = btn.getAttribute('data-sample');
            loadSampleText(sampleType);
        });
    });

    function loadSampleText(type) {
        const samples = {
            nda: `MUTUAL NON-DISCLOSURE AND PROPRIETARY INFORMATION AGREEMENT\nThis Agreement is entered into by and between Disclosing Party and Receiving Party.\nThe Receiving Party agrees to treat all technical data, proprietary source code, software architecture designs, algorithmic models, and business trade secrets as strictly confidential. The Receiving Party shall hold and maintain the Proprietary Information in strictest confidence and shall not disclose such information to any third party without prior written consent. The obligations of confidentiality shall survive termination for five (5) years.`,
            lease: `STANDARD RESIDENTIAL APARTMENT LEASE AGREEMENT\nThis Lease Agreement is made between Landlord (Apex Properties LLC) and Tenant (Alexander Wright) for residential premises located at Unit 4B, 108 Park Avenue.\nThe monthly rent shall be $2,450 payable on the first day of each calendar month. Tenant agrees to deposit $4,900 as security deposit against property damage, unpaid rent, and tenant breach. Tenant covenants to maintain the demised premises in a clean and tenantable condition. Landlord shall be responsible for structural maintenance and heating systems. In the event of rent delinquency exceeding 14 calendar days, Landlord may issue notice to vacate or initiate eviction proceedings.`,
            employment: `EXECUTIVE EMPLOYMENT AGREEMENT\nThis Employment Agreement is entered into between CloudScale Technologies Inc. ("Employer") and Jordan Miller ("Employee").\nEmployee shall serve in the executive role of Senior Director of Engineering, reporting directly to the Vice President of Product Engineering. Employer agrees to pay an annual base salary of $175,000, payable in bi-weekly disbursements subject to statutory tax withholding. Employee is eligible for the annual performance bonus, comprehensive health insurance, and 401(k) matching. During the term of employment and for twelve (12) months following termination, Employee covenants not to solicit customers or engage in competing software engineering enterprises.`,
            judgment: `IN THE HIGH COURT OF JUSTICE, CHANCERY DIVISION\nCase No: HC-2024-001928. Before the Honorable Justice Kensington.\nBetween: Apex Technologies Limited (Claimant) and Global Synthetics Corporation (Defendant). JUDGMENT.\nThe Claimant seeks damages and a permanent injunction for patent infringement under Section 60 of the Patents Act. Having reviewed the witness statements, technical expert depositions, and prior art evidence, this Court finds that Claim 1 of the patent-in-suit is valid and Defendant's manufacturing process infringes claims 1, 4, and 9. IT IS HEREBY ORDERED that Defendant is restrained from marketing the infringing product, and damages shall be assessed at an inquiry. Judgment for Claimant with costs.`
        };

        if (samples[type] && rawTextArea) {
            rawTextArea.value = samples[type];
            activeFile = null;
            if (fileInput) fileInput.value = '';
            if (selectedFileBadge) selectedFileBadge.classList.add('d-none');
            showToast(`Loaded ${type.toUpperCase()} sample document.`, 'info');
        }
    }

    // Submit Classification
    if (classifyBtn) {
        classifyBtn.addEventListener('click', async () => {
            const textValue = rawTextArea ? rawTextArea.value.trim() : '';

            if (!activeFile && !textValue) {
                showToast('Please upload a PDF/TXT file or paste legal text to classify.', 'warning');
                return;
            }

            const formData = new FormData();
            if (activeFile) {
                formData.append('file', activeFile);
            } else {
                formData.append('text', textValue);
            }

            classifyBtn.disabled = true;
            if (loadingSpinner) loadingSpinner.classList.remove('d-none');

            try {
                const response = await fetch('/api/classify', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || 'Classification failed.');
                }

                currentPredictionResult = data;
                renderClassificationResult(data);
                showToast('Document classified successfully!', 'success');
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                classifyBtn.disabled = false;
                if (loadingSpinner) loadingSpinner.classList.add('d-none');
            }
        });
    }

    function renderClassificationResult(data) {
        if (!resultsPanel) return;
        resultsPanel.classList.remove('d-none');
        resultsPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });

        document.getElementById('res-category').textContent = data.predicted_category;
        document.getElementById('res-model').textContent = data.model_used;
        
        const confText = document.getElementById('res-confidence-text');
        const confBar = document.getElementById('res-confidence-bar');
        if (data.confidence_available) {
            const conf = data.confidence_score_percent;
            confText.textContent = `${conf}%`;
            confBar.style.width = `${conf}%`;
            confBar.className = conf >= 75 ? 'progress-bar bg-success' : conf >= 50 ? 'progress-bar bg-warning' : 'progress-bar bg-danger';
        } else {
            confText.textContent = 'Decision Boundary Score';
            confBar.style.width = '100%';
            confBar.className = 'progress-bar bg-secondary';
        }

        // Indicative Terms Pills
        const termsContainer = document.getElementById('res-indicative-terms');
        termsContainer.innerHTML = '';
        if (data.indicative_terms && data.indicative_terms.length > 0) {
            data.indicative_terms.forEach(t => {
                const span = document.createElement('span');
                span.className = 'term-tag';
                span.innerHTML = `<strong>${t.term}</strong> <span class="term-weight">(+${t.weight})</span>`;
                termsContainer.appendChild(span);
            });
        } else {
            termsContainer.innerHTML = '<span class="text-muted small">No distinct keyword spikes extracted.</span>';
        }

        // Full Probability Distribution Breakdown
        const probContainer = document.getElementById('res-probabilities-list');
        probContainer.innerHTML = '';
        if (data.all_class_scores && data.all_class_scores.length > 0) {
            data.all_class_scores.forEach(item => {
                const isSelected = item.category === data.predicted_category;
                const row = document.createElement('div');
                row.className = `p-2 mb-1 rounded d-flex justify-content-between align-items-center ${isSelected ? 'bg-light border border-primary font-weight-bold' : ''}`;
                row.innerHTML = `
                    <span class="${isSelected ? 'fw-bold text-primary' : 'text-secondary'} small">${item.category}</span>
                    <span class="badge ${isSelected ? 'bg-primary' : 'bg-light text-dark border'}">${item.score}%</span>
                `;
                probContainer.appendChild(row);
            });
        }

        // Document Preview
        const previewEl = document.getElementById('res-text-preview');
        if (previewEl && data.text_preview) {
            previewEl.textContent = data.text_preview;
        }

        // Document Stats
        const statsEl = document.getElementById('res-text-stats');
        if (statsEl && data.text_statistics) {
            statsEl.textContent = `${data.text_statistics.raw_char_count} characters | ${data.text_statistics.token_count} words/tokens | Source: ${data.filename}`;
        }
    }

    // Download Report Handlers
    const dlPdfBtn = document.getElementById('download-pdf-btn');
    const dlTxtBtn = document.getElementById('download-txt-btn');

    if (dlPdfBtn) {
        dlPdfBtn.addEventListener('click', () => downloadReport('pdf'));
    }
    if (dlTxtBtn) {
        dlTxtBtn.addEventListener('click', () => downloadReport('txt'));
    }

    async function downloadReport(format) {
        if (!currentPredictionResult) {
            showToast('No active classification result to download.', 'warning');
            return;
        }

        try {
            const payload = {
                ...currentPredictionResult,
                format: format
            };
            const response = await fetch('/api/download-report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('Failed to generate report.');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Classification_Report_${currentPredictionResult.filename || 'Document'}.${format}`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            showToast(`Downloaded ${format.toUpperCase()} report successfully!`, 'success');
        } catch (err) {
            showToast(err.message, 'error');
        }
    }
}


// -------------------------------------------------------------
// 3. MODEL EVALUATION PAGE LOGIC
// -------------------------------------------------------------
async function initEvaluationPage() {
    const tableBody = document.getElementById('eval-table-body');
    const classReportContainer = document.getElementById('per-class-report-container');
    const tuningContainer = document.getElementById('tuning-details-container');
    const dlReportBtn = document.getElementById('download-eval-pdf-btn');

    if (dlReportBtn) {
        dlReportBtn.addEventListener('click', () => {
            window.location.href = '/api/download-evaluation-report';
        });
    }

    try {
        const response = await fetch('/api/evaluation-data');
        const data = await response.json();

        if (tableBody && data.models) {
            tableBody.innerHTML = '';
            for (const [name, stats] of Object.entries(data.models)) {
                const isBest = (name === data.best_model_name);
                const tr = document.createElement('tr');
                tr.className = isBest ? 'table-warning font-weight-bold' : '';
                tr.innerHTML = `
                    <td>
                        <strong>${name}</strong>
                        ${isBest ? '<span class="badge bg-gold text-dark ms-2">Selected Best</span>' : ''}
                    </td>
                    <td>${(stats.accuracy * 100).toFixed(2)}%</td>
                    <td>${(stats.macro_precision * 100).toFixed(2)}%</td>
                    <td>${(stats.macro_recall * 100).toFixed(2)}%</td>
                    <td><strong>${(stats.macro_f1 * 100).toFixed(2)}%</strong></td>
                    <td>${(stats.weighted_f1 * 100).toFixed(2)}%</td>
                    <td>${(stats.cv_mean_f1 * 100).toFixed(2)}% ± ${(stats.cv_std_f1 * 100).toFixed(2)}%</td>
                `;
                tableBody.appendChild(tr);
            }
        }

        // Per-Class Classification Report for Best Model
        if (classReportContainer && data.models && data.best_model_name) {
            const bestStats = data.models[data.best_model_name];
            const report = bestStats.classification_report;
            if (report) {
                let html = '<div class="table-responsive"><table class="table table-hover table-striped align-middle small mb-0">';
                html += '<thead class="table-dark"><tr><th>Legal Category</th><th>Precision</th><th>Recall</th><th>F1-Score</th><th>Test Support</th></tr></thead><tbody>';
                
                for (const [cls, m] of Object.entries(report)) {
                    if (['accuracy', 'macro avg', 'weighted avg'].includes(cls)) continue;
                    html += `
                        <tr>
                            <td><strong>${cls}</strong></td>
                            <td>${(m.precision * 100).toFixed(1)}%</td>
                            <td>${(m.recall * 100).toFixed(1)}%</td>
                            <td><span class="badge bg-primary">${(m['f1-score'] * 100).toFixed(1)}%</span></td>
                            <td>${m.support}</td>
                        </tr>
                    `;
                }
                html += '</tbody></table></div>';
                classReportContainer.innerHTML = html;
            }
        }

        // Hyperparameter Tuning Details
        if (tuningContainer && data.hyperparameter_tuning) {
            const t = data.hyperparameter_tuning;
            tuningContainer.innerHTML = `
                <div class="p-3 bg-light rounded border">
                    <h6 class="text-navy fw-bold mb-2"><i class="bi bi-gear-wide-connected me-2"></i>GridSearchCV Optimization Protocol</h6>
                    <p class="mb-1 small"><strong>Candidate Algorithm:</strong> ${t.algorithm || 'Multinomial Naive Bayes'}</p>
                    <p class="mb-1 small"><strong>Optimal Parameters:</strong> <code>${JSON.stringify(t.best_params)}</code></p>
                    <p class="mb-1 small"><strong>Best Cross-Validation Macro F1:</strong> <span class="badge bg-success">${(t.best_cv_score * 100).toFixed(2)}%</span></p>
                    <p class="mb-0 small text-muted">Tuning evaluates n-gram vocabulary ranges (unigrams vs bigrams) and Laplace smoothing values across stratified folds.</p>
                </div>
            `;
        }

    } catch (err) {
        showToast('Failed to load evaluation benchmarks: ' + err.message, 'error');
    }
}

// -------------------------------------------------------------
// 4. DATASET EXPLORER PAGE LOGIC
// -------------------------------------------------------------
async function initDatasetPage() {
    const totalDocsEl = document.getElementById('ds-total-rows');
    const validDocsEl = document.getElementById('ds-valid-rows');
    const duplicatesEl = document.getElementById('ds-duplicates');
    const categoriesCountEl = document.getElementById('ds-categories-count');
    const previewTbody = document.getElementById('dataset-preview-tbody');
    const searchInput = document.getElementById('ds-search-input');
    const uploadForm = document.getElementById('dataset-upload-form');
    const retrainBtn = document.getElementById('retrain-model-btn');
    const retrainSpinner = document.getElementById('retrain-spinner');

    let allPreviewRows = [];

    async function loadDatasetStats() {
        try {
            const response = await fetch('/api/dataset-stats');
            const data = await response.json();
            const rep = data.validation_report;

            if (totalDocsEl) totalDocsEl.textContent = rep.total_rows;
            if (validDocsEl) validDocsEl.textContent = rep.valid_rows;
            if (duplicatesEl) duplicatesEl.textContent = rep.duplicate_count;
            if (categoriesCountEl) categoriesCountEl.textContent = rep.unique_categories;

            allPreviewRows = data.preview_rows || [];
            renderPreviewTable(allPreviewRows);
            renderDatasetDistributionChart(rep.category_distribution);
        } catch (err) {
            showToast('Failed to load dataset details: ' + err.message, 'error');
        }
    }

    function renderPreviewTable(rows) {
        if (!previewTbody) return;
        previewTbody.innerHTML = '';
        if (rows.length === 0) {
            previewTbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No records match filter.</td></tr>';
            return;
        }

        rows.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><code>${r.document_id}</code></td>
                <td><span class="badge bg-light text-dark border">${r.category}</span></td>
                <td><span class="text-muted small">${r.snippet}</span></td>
                <td>${r.word_count} words</td>
            `;
            previewTbody.appendChild(tr);
        });
    }

    function renderDatasetDistributionChart(dist) {
        const ctx = document.getElementById('datasetDistChart');
        if (!ctx || !dist) return;
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(dist),
                datasets: [{
                    label: 'Document Count',
                    data: Object.values(dist),
                    backgroundColor: '#1e3a5f'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                scales: { x: { beginAtZero: true } },
                plugins: { legend: { display: false } }
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allPreviewRows.filter(r => 
                r.document_id.toLowerCase().includes(query) ||
                r.category.toLowerCase().includes(query) ||
                r.snippet.toLowerCase().includes(query)
            );
            renderPreviewTable(filtered);
        });
    }

    // CSV Upload Handler
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('csv-file-input');
            if (!fileInput || !fileInput.files[0]) {
                showToast('Please select a CSV dataset to upload.', 'warning');
                return;
            }

            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const res = await fetch('/api/dataset/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (!res.ok || !data.success) {
                    throw new Error(data.error || 'Dataset upload failed.');
                }

                showToast(data.message, 'success');
                fileInput.value = '';
                loadDatasetStats();
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    // Retraining Handler
    if (retrainBtn) {
        retrainBtn.addEventListener('click', async () => {
            if (!confirm('Start full model training across Naive Bayes, Logistic Regression, and Linear SVM? This will benchmark all candidate models.')) {
                return;
            }

            retrainBtn.disabled = true;
            if (retrainSpinner) retrainSpinner.classList.remove('d-none');

            try {
                const res = await fetch('/api/retrain', { method: 'POST' });
                const data = await res.json();

                if (!res.ok || !data.success) {
                    throw new Error(data.error || 'Retraining failed.');
                }

                showToast(`Retraining Complete! Selected Model: ${data.best_model} (Macro F1: ${(data.macro_f1 * 100).toFixed(1)}%)`, 'success');
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                retrainBtn.disabled = false;
                if (retrainSpinner) retrainSpinner.classList.add('d-none');
            }
        });
    }

    loadDatasetStats();
}

// -------------------------------------------------------------
// 5. PREDICTION HISTORY PAGE LOGIC
// -------------------------------------------------------------
async function initHistoryPage() {
    const historyTbody = document.getElementById('history-tbody');
    const searchInput = document.getElementById('history-search');
    const categoryFilter = document.getElementById('history-category-filter');
    const clearAllBtn = document.getElementById('clear-all-history-btn');

    async function loadHistory() {
        const search = searchInput ? searchInput.value.trim() : '';
        const cat = categoryFilter ? categoryFilter.value : '';

        try {
            const url = `/api/history?limit=100&search=${encodeURIComponent(search)}&category=${encodeURIComponent(cat)}`;
            const res = await fetch(url);
            const data = await res.json();
            renderHistoryRows(data.records || []);
        } catch (err) {
            showToast('Failed to load history: ' + err.message, 'error');
        }
    }

    function renderHistoryRows(records) {
        if (!historyTbody) return;
        historyTbody.innerHTML = '';
        if (records.length === 0) {
            historyTbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No prediction records found.</td></tr>';
            return;
        }

        records.forEach(r => {
            const dateStr = new Date(r.created_at).toLocaleString();
            const conf = r.confidence_score ? `${r.confidence_score}%` : 'N/A';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><small class="text-muted">${dateStr}</small></td>
                <td><strong>${r.filename}</strong></td>
                <td><span class="badge bg-primary">${r.predicted_category}</span></td>
                <td><span class="badge bg-light text-dark border">${conf}</span></td>
                <td><small>${r.model_used}</small></td>
                <td><span class="text-muted small" title="${r.snippet}">${r.snippet.length > 50 ? r.snippet.substring(0, 48) + '...' : r.snippet}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-danger btn-delete-row" data-id="${r.id}" title="Delete Record">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
            historyTbody.appendChild(tr);
        });

        // Bind delete buttons
        document.querySelectorAll('.btn-delete-row').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                if (confirm('Delete this prediction record?')) {
                    try {
                        const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
                        if (res.ok) {
                            showToast('Record deleted.', 'info');
                            loadHistory();
                        }
                    } catch (e) {
                        showToast(e.message, 'error');
                    }
                }
            });
        });
    }

    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to permanently clear all prediction history?')) {
                try {
                    const res = await fetch('/api/history/clear', { method: 'DELETE' });
                    if (res.ok) {
                        showToast('All history records cleared.', 'success');
                        loadHistory();
                    }
                } catch (e) {
                    showToast(e.message, 'error');
                }
            }
        });
    }

    if (searchInput) searchInput.addEventListener('input', () => loadHistory());
    if (categoryFilter) categoryFilter.addEventListener('change', () => loadHistory());

    loadHistory();
}

// -------------------------------------------------------------
// 6. AMLIS CONCEPTS & CLUSTERING EXPLORER LOGIC
// -------------------------------------------------------------
async function initConceptsPage() {
    const kSelector = document.getElementById('cluster-k-select');
    const clusterCardsContainer = document.getElementById('cluster-cards-container');
    const svdScatterCanvas = document.getElementById('svdScatterChart');
    let svdChart = null;

    async function loadClustering(k = 5) {
        try {
            const res = await fetch(`/api/clustering-data?k=${k}`);
            const data = await res.json();

            if (data.error) {
                showToast(data.error, 'warning');
                return;
            }

            renderClusterCards(data.clusters);
            renderScatterPlot(data);
        } catch (err) {
            showToast('Failed to load clustering: ' + err.message, 'error');
        }
    }

    function renderClusterCards(clusters) {
        if (!clusterCardsContainer || !clusters) return;
        clusterCardsContainer.innerHTML = '';
        const clusterColors = ['#0f223d', '#d4af37', '#0284c7', '#059669', '#dc2626', '#7c3aed', '#d97706', '#475569'];

        clusters.forEach((c, idx) => {
            const col = document.createElement('div');
            col.className = 'col-md-4 col-sm-6 mb-3';
            const color = clusterColors[idx % clusterColors.length];
            col.innerHTML = `
                <div class="card h-100 shadow-sm border" style="border-top: 4px solid ${color} !important;">
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="fw-bold mb-0" style="color: ${color};">${c.label}</h6>
                            <span class="badge bg-light text-dark border">${c.document_count} docs</span>
                        </div>
                        <div class="small text-muted mb-2">Top Centroid Terms:</div>
                        <div>
                            ${c.top_terms.map(t => `<span class="badge bg-light text-secondary border me-1 mb-1">${t}</span>`).join('')}
                        </div>
                    </div>
                </div>
            `;
            clusterCardsContainer.appendChild(col);
        });
    }

    function renderScatterPlot(data) {
        if (!svdScatterCanvas) return;
        const clusterColors = ['#0f223d', '#d4af37', '#0284c7', '#059669', '#dc2626', '#7c3aed', '#d97706', '#475569'];

        // Group points by cluster for Chart.js scatter dataset
        const datasets = [];
        for (let i = 0; i < data.n_clusters; i++) {
            const pointsInCluster = data.points.filter(p => p.cluster_id === i);
            datasets.push({
                label: `Cluster ${i + 1}`,
                data: pointsInCluster.map(p => ({ x: p.x, y: p.y, meta: p })),
                backgroundColor: clusterColors[i % clusterColors.length],
                pointRadius: 6,
                pointHoverRadius: 9
            });
        }

        if (svdChart) svdChart.destroy();

        svdChart = new Chart(svdScatterCanvas, {
            type: 'scatter',
            data: { datasets: datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: { display: true, text: `TruncatedSVD Component 1 (${data.explained_variance_ratio_percent[0]}% Variance)` },
                        grid: { color: '#f1f5f9' }
                    },
                    y: {
                        title: { display: true, text: `TruncatedSVD Component 2 (${data.explained_variance_ratio_percent[1]}% Variance)` },
                        grid: { color: '#f1f5f9' }
                    }
                },
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                const p = ctx.raw.meta;
                                return [
                                    `ID: ${p.document_id}`,
                                    `True Label: ${p.category}`,
                                    `Text: ${p.snippet}`
                                ];
                            }
                        }
                    }
                }
            }
        });
    }

    if (kSelector) {
        kSelector.addEventListener('change', (e) => {
            loadClustering(parseInt(e.target.value));
        });
    }

    loadClustering(5);
}

// -------------------------------------------------------------
// Global Page Dispatcher
// -------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const pageId = document.body.getAttribute('data-page');
    if (pageId === 'classify') initClassifyPage();
    else if (pageId === 'evaluation') initEvaluationPage();
    else if (pageId === 'dataset') initDatasetPage();
    else if (pageId === 'history') initHistoryPage();
    else if (pageId === 'concepts') initConceptsPage();
});
