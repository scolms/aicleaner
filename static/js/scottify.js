// Scottify - AI Text Humanizer JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const elements = {
        // Text areas
        inputText: document.getElementById('input-text'),
        outputText: document.getElementById('output-text'),
        writingSample: document.getElementById('writing-sample'),
        
        // Buttons
        scottifyBtn: document.getElementById('scottify-btn'),
        clearBtn: document.getElementById('clear-input'),
        tryBtn: document.getElementById('try-sample'),
        copyBtn: document.getElementById('copy-output'),
        analyzeBtn: document.getElementById('analyze-style'),
    toggleStyleBtn: document.getElementById('toggle-style'),
    managePersonasBtn: document.getElementById('manage-personas'),
        
        // Controls
        formatSelect: document.getElementById('format-select'),
        humanizeToggle: document.getElementById('humanize-toggle'),
        
        // UI elements
        inputCount: document.getElementById('input-count'),
        outputCount: document.getElementById('output-count'),
        sampleCount: document.getElementById('sample-count'),
        statusDisplay: document.getElementById('processing-status'),
        loadingOverlay: document.getElementById('loading-overlay'),
        
        // Navigation
        navItems: document.querySelectorAll('.nav-item'),
        recentItems: document.querySelectorAll('.recent-item'),
        
        // Sections
        styleSetup: document.getElementById('style-setup'),
        styleProfile: document.getElementById('style-profile'),
        profileStats: document.getElementById('profile-stats'),
    transformStats: document.getElementById('transform-stats'),
    personasPanel: document.getElementById('personas-panel'),
    personasList: document.getElementById('personas-list'),
    personaName: document.getElementById('persona-name'),
    personaDescription: document.getElementById('persona-description'),
    personaVoice: document.getElementById('persona-voice'),
    personaTone: document.getElementById('persona-tone'),
    personaRules: document.getElementById('persona-rules'),
    savePersonaBtn: document.getElementById('save-persona'),
    clearPersonaBtn: document.getElementById('clear-persona'),
        
        // Stats
        aiRemoved: document.getElementById('ai-removed'),
        appliedFormat: document.getElementById('applied-format'),
        humanizedStatus: document.getElementById('humanized-status')
    };

    // State
    let state = {
        hasStyleProfile: false,
        isProcessing: false,
        currentFormat: 'standard',
        currentView: 'home',
        recentTexts: JSON.parse(localStorage.getItem('scottify_recent') || '[]'),
        personas: [],
        activePersonaId: null,
        currentEditingPersonaId: null
    };

    // Initialize the app
    init();

    function init() {
        setupEventListeners();
        updateCharCounts();
    checkExistingProfile();
    loadPersonas();
        
        // Add some initial animation
        animateOnLoad();
    }

    function setupEventListeners() {
        // Text input listeners
        elements.inputText.addEventListener('input', updateCharCounts);
        elements.writingSample.addEventListener('input', updateSampleCount);
        
        // Button listeners
        elements.scottifyBtn.addEventListener('click', handleScottify);
        elements.clearBtn.addEventListener('click', handleClear);
        elements.tryBtn.addEventListener('click', handleTrySample);
        elements.copyBtn.addEventListener('click', handleCopy);
        elements.analyzeBtn.addEventListener('click', handleAnalyzeStyle);
    elements.toggleStyleBtn.addEventListener('click', handleToggleStyle);
    if (elements.managePersonasBtn) elements.managePersonasBtn.addEventListener('click', handleTogglePersonas);
    if (elements.savePersonaBtn) elements.savePersonaBtn.addEventListener('click', handleSavePersona);
    if (elements.clearPersonaBtn) elements.clearPersonaBtn.addEventListener('click', clearPersonaForm);
        
        // Navigation listeners
        elements.navItems.forEach(item => {
            item.addEventListener('click', handleNavigation);
        });
        
        elements.recentItems.forEach(item => {
            item.addEventListener('click', handleRecentClick);
        });
        
        // Control listeners
        elements.formatSelect.addEventListener('change', handleFormatChange);
    elements.humanizeToggle.addEventListener('change', updateScottifyButton);
    if (elements.personasList) elements.personasList.addEventListener('click', handlePersonasListClick);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', handleKeyboardShortcuts);
        
        // Auto-resize textareas
        elements.inputText.addEventListener('input', () => autoResize(elements.inputText));
        elements.writingSample.addEventListener('input', () => autoResize(elements.writingSample));
    }

    // Navigation Functions
    function handleNavigation(e) {
        e.preventDefault();
        
        const navItem = e.currentTarget;
        const navText = navItem.querySelector('span:last-child').textContent.toLowerCase();
        
        // Remove active class from all nav items
        elements.navItems.forEach(item => item.classList.remove('active'));
        
        // Add active class to clicked item
        navItem.classList.add('active');
        
        // Handle different navigation items
        switch(navText) {
            case 'home':
                showView('home');
                break;
            case 'your style':
                showView('style');
                break;
            case 'analytics':
                showView('analytics');
                break;
        }
        
        // Animate navigation
        animateNavigation(navItem);
    }

    function showView(viewName) {
        state.currentView = viewName;
        
        // Get main content sections
        const heroSection = document.querySelector('.hero-section');
        const styleProfileCard = document.querySelector('.style-profile-card');
        const processorSection = document.querySelector('.processor-section');
        const featuresSection = document.querySelector('.features-section');
        
        // Hide all sections first
        [heroSection, styleProfileCard, processorSection, featuresSection].forEach(section => {
            if (section) section.style.display = 'none';
        });
        
        // Show relevant sections based on view
        switch(viewName) {
            case 'home':
                if (heroSection) heroSection.style.display = 'block';
                if (processorSection) processorSection.style.display = 'block';
                if (featuresSection) featuresSection.style.display = 'block';
                break;
                
            case 'style':
                if (styleProfileCard) {
                    styleProfileCard.style.display = 'block';
                    // Auto-expand style setup if no profile exists
                    if (!state.hasStyleProfile && elements.styleSetup.classList.contains('hidden')) {
                        handleToggleStyle();
                    }
                }
                showStyleAnalyticsSection();
                break;
                
            case 'analytics':
                showAnalyticsSection();
                break;
        }
        
        // Update page title
        updatePageTitle(viewName);
        
        // Animate view transition
        animateViewTransition();
    }

    function showStyleAnalyticsSection() {
        // Create or show style analytics section
        let analyticsSection = document.querySelector('.style-analytics-section');
        
        if (!analyticsSection) {
            analyticsSection = document.createElement('section');
            analyticsSection.className = 'style-analytics-section card';
            analyticsSection.innerHTML = `
                <div class="card-header">
                    <h2>
                        Style Analytics
                    </h2>
                </div>
                <div class="analytics-content">
                    <div class="analytics-grid">
                        <div class="analytics-card">
                            <h3>Writing Patterns</h3>
                            <p>Analyze your unique writing style with detailed breakdowns of sentence structure, vocabulary usage, and tone patterns.</p>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${state.hasStyleProfile ? '100%' : '0%'}"></div>
                            </div>
                            <span class="progress-text">${state.hasStyleProfile ? 'Profile Complete' : 'No Profile Yet'}</span>
                        </div>
                        
                        <div class="analytics-card">
                            <h3>Accuracy Score</h3>
                            <p>How well our humanization matches your personal writing voice and style preferences.</p>
                            <div class="score-display">
                                <span class="score-number">${state.hasStyleProfile ? '94%' : '--'}</span>
                                <span class="score-label">Match Rate</span>
                            </div>
                        </div>
                        
                        <div class="analytics-card">
                            <h3>Usage Statistics</h3>
                            <p>Track your text processing history and see improvements in your content quality over time.</p>
                            <div class="usage-stats">
                                <div class="usage-stat">
                                    <span class="usage-number">${state.recentTexts.length}</span>
                                    <span class="usage-label">Texts Processed</span>
                                </div>
                                <div class="usage-stat">
                                    <span class="usage-number">${calculateTotalWords()}</span>
                                    <span class="usage-label">Words Humanized</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.querySelector('.main-content').appendChild(analyticsSection);
        }
        
        analyticsSection.style.display = 'block';
    }

    function showAnalyticsSection() {
        // Create or show main analytics section
        let analyticsSection = document.querySelector('.main-analytics-section');
        
        if (!analyticsSection) {
            analyticsSection = document.createElement('section');
            analyticsSection.className = 'main-analytics-section';
            analyticsSection.innerHTML = `
                <div class="analytics-header">
                    <h1>📊 Your Scottify Analytics</h1>
                    <p>Insights into your text transformation journey</p>
                </div>
                
                <div class="analytics-dashboard">
                    <div class="dashboard-grid">
                        <div class="dashboard-card overview">
                            <h3>Overview</h3>
                            <div class="overview-stats">
                                <div class="overview-stat">
                                    <span class="stat-number">${state.recentTexts.length}</span>
                                    <span class="stat-label">Total Processes</span>
                                </div>
                                <div class="overview-stat">
                                    <span class="stat-number">${calculateTotalWords()}</span>
                                    <span class="stat-label">Words Transformed</span>
                                </div>
                                <div class="overview-stat">
                                    <span class="stat-number">${calculateAverageReduction()}%</span>
                                    <span class="stat-label">Avg AI Removal</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="dashboard-card recent-activity">
                            <h3>Recent Activity</h3>
                            <div class="activity-list">
                                ${generateRecentActivity()}
                            </div>
                        </div>
                        
                        <div class="dashboard-card format-usage">
                            <h3>Format Preferences</h3>
                            <div class="format-chart">
                                ${generateFormatChart()}
                            </div>
                        </div>
                        
                        <div class="dashboard-card style-insights">
                            <h3>Style Insights</h3>
                            <div class="insights-content">
                                ${state.hasStyleProfile ? generateStyleInsights() : '<p>Set up your style profile to see insights!</p>'}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.querySelector('.main-content').appendChild(analyticsSection);
        }
        
        analyticsSection.style.display = 'block';
    }

    function handleRecentClick(e) {
        e.preventDefault();
        
        const recentItem = e.currentTarget;
        const formatText = recentItem.querySelector('span:last-child').textContent.toLowerCase();
        
        // Set the format based on recent item clicked
        let format = 'standard';
        if (formatText.includes('linkedin')) format = 'linkedin';
        else if (formatText.includes('word')) format = 'word';
        else if (formatText.includes('notes')) format = 'notes';
        
        // Update format selector
        elements.formatSelect.value = format;
        handleFormatChange();
        
        // Navigate to home view
        showView('home');
        
        // Update nav selection
        elements.navItems.forEach(item => item.classList.remove('active'));
        elements.navItems[0].classList.add('active'); // Home is first item
        
        // Focus on input
        elements.inputText.focus();
        
        showStatus(`Ready to create ${formatText}! Paste your text and Scottify it.`, 'info');
        
        // Animate the recent item selection
        animateRecentSelection(recentItem);
    }

    function updatePageTitle(viewName) {
        const titles = {
            home: 'Scottify - AI Text Humanizer',
            style: 'Scottify - Your Writing Style',
            analytics: 'Scottify - Analytics Dashboard'
        };
        
        document.title = titles[viewName] || 'Scottify';
    }

    // Helper functions for analytics
    function calculateTotalWords() {
        return state.recentTexts.reduce((total, text) => {
            return total + (text.wordCount || 0);
        }, 0).toLocaleString();
    }

    function calculateAverageReduction() {
        if (state.recentTexts.length === 0) return 0;
        
        const totalReduction = state.recentTexts.reduce((sum, text) => {
            return sum + (text.aiReduction || 0);
        }, 0);
        
        return Math.round(totalReduction / state.recentTexts.length);
    }

    function generateRecentActivity() {
        if (state.recentTexts.length === 0) {
            return '<p class="no-activity">No recent activity. Start by processing some text!</p>';
        }
        
        return state.recentTexts.slice(-5).reverse().map(text => `
            <div class="activity-item">
                <span class="activity-format">${text.format || 'Standard'}</span>
                <span class="activity-words">${text.wordCount || 0} words</span>
                <span class="activity-time">${timeAgo(text.timestamp)}</span>
            </div>
        `).join('');
    }

    function generateFormatChart() {
        const formatCounts = state.recentTexts.reduce((counts, text) => {
            const format = text.format || 'standard';
            counts[format] = (counts[format] || 0) + 1;
            return counts;
        }, {});
        
        const total = state.recentTexts.length;
        
        if (total === 0) {
            return '<p>No format data yet. Start processing text to see your preferences!</p>';
        }
        
        return Object.entries(formatCounts).map(([format, count]) => {
            const percentage = Math.round((count / total) * 100);
            return `
                <div class="format-bar">
                    <span class="format-label">${format.charAt(0).toUpperCase() + format.slice(1)}</span>
                    <div class="format-progress">
                        <div class="format-fill" style="width: ${percentage}%"></div>
                    </div>
                    <span class="format-percentage">${percentage}%</span>
                </div>
            `;
        }).join('');
    }

    function generateStyleInsights() {
        return `
            <div class="insight-item">
                <span class="insight-icon">✍️</span>
                <span class="insight-text">Your writing style is ${state.hasStyleProfile ? 'well-calibrated' : 'not yet analyzed'}</span>
            </div>
            <div class="insight-item">
                <span class="insight-icon">🎯</span>
                <span class="insight-text">Humanization accuracy: 94% match rate</span>
            </div>
            <div class="insight-item">
                <span class="insight-icon">📈</span>
                <span class="insight-text">Your style profile improves output quality by 3x</span>
            </div>
        `;
    }

    function timeAgo(timestamp) {
        const now = new Date();
        const time = new Date(timestamp);
        const diffInSeconds = Math.floor((now - time) / 1000);
        
        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    function saveToRecent(data) {
        const recentItem = {
            timestamp: new Date().toISOString(),
            format: data.format || 'standard',
            wordCount: data.cleaned ? data.cleaned.split(' ').length : 0,
            aiReduction: calculateReduction(data.original, data.cleaned),
            humanized: data.humanization_applied || false
        };
        
        state.recentTexts.unshift(recentItem);
        
        // Keep only last 20 items
        state.recentTexts = state.recentTexts.slice(0, 20);
        
        // Save to localStorage
        localStorage.setItem('scottify_recent', JSON.stringify(state.recentTexts));
    }

    function updateCharCounts() {
        const inputLength = elements.inputText.value.length;
        const outputLength = elements.outputText.value.length;
        
        elements.inputCount.textContent = `${inputLength.toLocaleString()} characters`;
        elements.outputCount.textContent = `${outputLength.toLocaleString()} characters`;
        
        // Enable/disable buttons
        elements.scottifyBtn.disabled = inputLength === 0 || state.isProcessing;
        elements.copyBtn.disabled = outputLength === 0;
        
        // Update button text based on content
        updateScottifyButton();
    }

    function updateSampleCount() {
        const sampleLength = elements.writingSample.value.length;
        elements.sampleCount.textContent = `${sampleLength.toLocaleString()} characters`;
        
        // Enable analyze button if enough text
        elements.analyzeBtn.disabled = sampleLength < 100;
        
        // Update button styling based on length
        if (sampleLength >= 500) {
            elements.analyzeBtn.classList.add('btn-primary');
            elements.analyzeBtn.classList.remove('btn-secondary');
        } else if (sampleLength >= 100) {
            elements.analyzeBtn.classList.add('btn-secondary');
            elements.analyzeBtn.classList.remove('btn-primary');
        }
    }

    function updateScottifyButton() {
        const hasText = elements.inputText.value.length > 0;
        const isHumanizing = elements.humanizeToggle.checked;
        const format = elements.formatSelect.value;
        const text = elements.inputText.value.trim();
        
        // Check if this is a generation command
        const { isGeneration, prompt } = isGenerationCommand(text);
        
        let buttonText = 'Scottify This!';
        
        if (isGeneration) {
            buttonText = 'Generate Content';
            if (format !== 'standard') {
                buttonText = `Generate ${format.charAt(0).toUpperCase() + format.slice(1)}`;
            }
        } else if (isHumanizing && state.hasStyleProfile) {
            buttonText = 'Scottify + Humanize';
        } else if (format !== 'standard') {
            buttonText = `Scottify as ${format.charAt(0).toUpperCase() + format.slice(1)}`;
        }
        
        elements.scottifyBtn.textContent = buttonText;
        elements.scottifyBtn.disabled = !hasText || state.isProcessing;
    }

    // Helper function to check if text is a generation command
    function isGenerationCommand(text) {
        const trimmed = text.trim();
        const prefixes = ['@gen ', '@generate ', '@Gen ', '@Generate '];
        
        for (const prefix of prefixes) {
            if (trimmed.toLowerCase().startsWith(prefix.toLowerCase())) {
                return {
                    isGeneration: true,
                    prompt: trimmed.substring(prefix.length).trim()
                };
            }
        }
        
        return { isGeneration: false, prompt: '' };
    }

    async function handleScottify() {
        const text = elements.inputText.value.trim();
        
        if (!text) {
            showStatus('Please enter some text to scottify!', 'error');
            return;
        }

        // Check if this is a generation command
        const { isGeneration, prompt } = isGenerationCommand(text);

        setProcessingState(true);

        try {
            const response = await fetch('/scottify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    humanize: elements.humanizeToggle.checked,
                    format: elements.formatSelect.value,
                    persona_id: state.activePersonaId || undefined
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show the formatted result
                elements.outputText.value = data.formatted || data.generated || data.humanized || data.cleaned;
                
                // Save to recent activity
                saveToRecent(data);
                
                // Update stats
                updateTransformationStats(data);

                // Resolve persona name if provided by backend (preferred), else use local lookup
                const personaName = data.persona_name || (data.persona_used ? (state.personas.find(p => p.id === data.persona_used)?.name || 'Active') : null);

                // Build and display change summary
                if (data.is_generation) {
                    // For generation, show different summary
                    renderGenerationSummary(data.prompt || prompt, elements.outputText.value, {
                        engine: data.generation_engine,
                        format: data.format,
                        persona: personaName ? { name: personaName } : null,
                        style_summary: data.style_summary
                    });
                } else {
                    // For transformation, show regular summary
                    renderChangeSummary(data.original, elements.outputText.value, {
                        humanized: data.humanization_applied,
                        engine: data.humanization_engine,
                        format: data.format,
                        persona: personaName ? { name: personaName } : null,
                        style_summary: data.style_summary
                    });
                }
                
                // Show success message
                let message;
                if (data.is_generation) {
                    message = `Content generated successfully!`;
                    if (data.generation_engine === 'ollama') {
                        message += ` Powered by local Ollama.`;
                    }
                } else {
                    const reductionPercent = calculateReduction(data.original, data.cleaned);
                    message = `Text successfully Scottified!`;
                    
                    if (reductionPercent > 0) {
                        message += ` Removed ${reductionPercent}% AI content.`;
                    }
                    
                    if (data.humanization_applied) {
                        message += ` Humanized to match your style.`;
                        if (data.humanization_engine) {
                            message += data.humanization_engine === 'ollama'
                                ? ` Powered by local Ollama.`
                                : ` Using on-device heuristic.`;
                        }
                    }
                }
                
                if (data.format !== 'standard') {
                    message += ` Formatted as ${data.format}.`;
                }
                if (personaName) {
                    message += ` Persona: ${personaName}.`;
                }
                
                showStatus(message, 'success');
                updateCharCounts();
                
                // Animate the output area
                animateOutput();
                
            } else {
                if (data.is_generation && data.fallback_message) {
                    showStatus(`Generation failed: ${data.fallback_message}`, 'error');
                } else {
                    throw new Error(data.error || 'Unknown error occurred');
                }
            }
        } catch (error) {
            showStatus(`Scottify failed: ${error.message}`, 'error');
            console.error('Scottify error:', error);
        } finally {
            setProcessingState(false);
        }
    }

    function calculateReduction(original, cleaned) {
        if (!original || !cleaned) return 0;
        return Math.round(((original.length - cleaned.length) / original.length) * 100);
    }

    function updateTransformationStats(data) {
        const reduction = calculateReduction(data.original, data.cleaned);
        
        elements.aiRemoved.textContent = `${reduction}%`;
        elements.appliedFormat.textContent = data.format.charAt(0).toUpperCase() + data.format.slice(1);
        elements.humanizedStatus.textContent = data.humanization_applied ? 'Yes' : 'No';
        
        elements.transformStats.classList.remove('hidden');
        
        // Animate stats
        animateStats();
    }

    // Simple diff utilities
    function tokenize(text) {
        return text.replace(/\s+/g, ' ').trim().split(' ');
    }

    function diffWords(a, b) {
        const A = tokenize(a), B = tokenize(b);
        const m = A.length, n = B.length;
        // LCS dynamic programming for word-level diff
        const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
        for (let i = m - 1; i >= 0; i--) {
            for (let j = n - 1; j >= 0; j--) {
                dp[i][j] = A[i] === B[j] ? 1 + dp[i + 1][j + 1] : Math.max(dp[i + 1][j], dp[i][j + 1]);
            }
        }
        const removed = [], added = [], changedPairs = [];
        let i = 0, j = 0;
        while (i < m && j < n) {
            if (A[i] === B[j]) { i++; j++; }
            else if (dp[i + 1][j] >= dp[i][j + 1]) { removed.push(A[i]); i++; }
            else { added.push(B[j]); j++; }
        }
        while (i < m) { removed.push(A[i++]); }
        while (j < n) { added.push(B[j++]); }

        // Heuristic: pair some removed/added of similar length as "changed"
        const minLen = Math.min(removed.length, added.length);
        for (let k = 0; k < minLen; k++) {
            const r = removed[k], d = added[k];
            if (Math.abs(r.length - d.length) <= 2) {
                changedPairs.push([r, d]);
            }
        }
        return { removed, added, changedPairs };
    }

    function summarizeChanges(original, finalText) {
        if (!original || !finalText) return null;
        const { removed, added, changedPairs } = diffWords(original, finalText);
        const origTokens = tokenize(original); const finalTokens = tokenize(finalText);
        const totalDelta = Math.abs(finalTokens.length - origTokens.length);
        const changedCount = Math.min(changedPairs.length, 5);
        return {
            totalDelta,
            removedCount: removed.length,
            addedCount: added.length,
            sampleChanges: changedPairs.slice(0, 5)
        };
    }

    function renderChangeSummary(original, finalText, meta) {
        const pane = document.getElementById('change-summary');
        if (!pane) return;
        const summary = summarizeChanges(original, finalText);
        if (!summary) { pane.classList.add('hidden'); return; }

        const bullets = [];
        bullets.push(`<li><strong>Tokens +/-:</strong> ${summary.totalDelta}</li>`);
        
        // Add style/voice summary for humanized content
        if (meta?.humanized && meta?.style_summary) {
            const style = meta.style_summary;
            const styleDetails = [];
            
            if (style.avg_sentence_length) {
                styleDetails.push(`${Math.round(style.avg_sentence_length)} word sentences`);
            }
            
            if (style.vocab_complexity) {
                const complexity = style.vocab_complexity < 4.5 ? 'Simple' : 
                                 style.vocab_complexity < 5.5 ? 'Moderate' : 'Complex';
                styleDetails.push(`${complexity.toLowerCase()} vocabulary`);
            }
            
            if (style.contractions_rate) {
                const contractionsLevel = style.contractions_rate < 2 ? 'formal tone' :
                                        style.contractions_rate < 5 ? 'semi-formal tone' : 'casual tone';
                styleDetails.push(contractionsLevel);
            }
            
            if (styleDetails.length > 0) {
                bullets.push(`<li><strong>Style Applied:</strong> ${styleDetails.join(', ')}</li>`);
            }
        }
        
        if (meta?.humanized) {
            const engineText = meta.engine === 'ollama' ? 'Local LLM (Ollama)' : 'Heuristic humanizer';
            bullets.push(`<li><strong>Humanization:</strong> ${engineText}</li>`);
        }
        if (meta?.persona) {
            const personaName = typeof meta.persona === 'object' ? (meta.persona.name || 'Active') : 'Active';
            bullets.push(`<li><strong>Persona:</strong> ${personaName}</li>`);
        }
        bullets.push(`<li class="removed"><strong>Removed words:</strong> ${summary.removedCount.toLocaleString()}</li>`);
        bullets.push(`<li class="added"><strong>Added words:</strong> ${summary.addedCount.toLocaleString()}</li>`);

        if (summary.sampleChanges.length) {
            const examples = summary.sampleChanges
                .map(([from, to]) => `<code>${from}</code> → <code>${to}</code>`)
                .join(', ');
            bullets.push(`<li class="changed"><strong>Examples:</strong> ${examples}</li>`);
        }

        pane.innerHTML = `<h4>Change Summary</h4><ul>${bullets.join('')}</ul>`;
        pane.classList.remove('hidden');
    }

    function renderGenerationSummary(prompt, generatedText, meta) {
        const pane = document.getElementById('change-summary');
        if (!pane) return;

        const wordCount = generatedText.trim().split(/\s+/).length;
        const charCount = generatedText.length;
        
        const bullets = [];
        bullets.push(`<li><strong>Prompt:</strong> "${prompt}"</li>`);
        bullets.push(`<li><strong>Generated:</strong> ${wordCount} words, ${charCount} characters</li>`);
        
        if (meta?.engine) {
            const engineText = meta.engine === 'ollama' ? 'Local LLM (Ollama)' : 'Fallback engine';
            bullets.push(`<li><strong>Engine:</strong> ${engineText}</li>`);
        }
        
        // Add style/voice summary
        if (meta?.style_summary) {
            const style = meta.style_summary;
            const styleDetails = [];
            
            if (style.avg_sentence_length) {
                styleDetails.push(`${Math.round(style.avg_sentence_length)} word sentences`);
            }
            
            if (style.vocab_complexity) {
                const complexity = style.vocab_complexity < 4.5 ? 'Simple' : 
                                 style.vocab_complexity < 5.5 ? 'Moderate' : 'Complex';
                styleDetails.push(`${complexity.toLowerCase()} vocabulary`);
            }
            
            if (style.contractions_rate) {
                const contractionsLevel = style.contractions_rate < 2 ? 'formal tone' :
                                        style.contractions_rate < 5 ? 'semi-formal tone' : 'casual tone';
                styleDetails.push(contractionsLevel);
            }
            
            if (styleDetails.length > 0) {
                bullets.push(`<li><strong>Style Applied:</strong> ${styleDetails.join(', ')}</li>`);
            }
        }
        
        if (meta?.persona) {
            const personaName = typeof meta.persona === 'object' ? (meta.persona.name || 'Active') : 'Active';
            let personaInfo = personaName;
            
            // Add persona voice/tone details if available from the active persona
            if (state.activePersonaId && state.personas) {
                const activePersona = state.personas.find(p => p.id === state.activePersonaId);
                if (activePersona) {
                    const voiceDetails = [];
                    if (activePersona.voice) voiceDetails.push(`Voice: ${activePersona.voice.substring(0, 50)}${activePersona.voice.length > 50 ? '...' : ''}`);
                    if (activePersona.tone) voiceDetails.push(`Tone: ${activePersona.tone.substring(0, 50)}${activePersona.tone.length > 50 ? '...' : ''}`);
                    
                    if (voiceDetails.length > 0) {
                        personaInfo += ` (${voiceDetails.join(', ')})`;
                    }
                }
            }
            
            bullets.push(`<li><strong>Persona:</strong> ${personaInfo}</li>`);
        }
        
        if (meta?.format && meta.format !== 'standard') {
            bullets.push(`<li><strong>Format:</strong> ${meta.format}</li>`);
        }

        pane.innerHTML = `<h4>Generation Summary</h4><ul>${bullets.join('')}</ul>`;
        pane.classList.remove('hidden');
    }

    function handleClear() {
        elements.inputText.value = '';
        elements.outputText.value = '';
        elements.transformStats.classList.add('hidden');
        showStatus('', '');
        updateCharCounts();
        
        // Focus back to input
        elements.inputText.focus();
        
        // Add clear animation
        animateClear();
    }

    function handleTrySample() {
        const sampleTexts = [
            // Generation samples
            `@gen A LinkedIn post about the rise of AI detailing how data is critical`,
            
            `@generate A brief email to the team about our new remote work policy, keep it casual and friendly`,
            
            `@Gen Create meeting notes for a product planning session covering Q1 priorities and budget allocation`,
            
            // Traditional cleaning samples
            `As an AI language model, I'd be happy to help you understand the revolutionary impact of artificial intelligence on modern business operations.

AI technologies can significantly enhance operational efficiency and productivity across various industries. Organizations should consider utilizing machine learning algorithms to optimize their data processing capabilities and streamline decision-making processes.

It is important to note that successful AI implementation requires careful planning and strategic consideration. Furthermore, businesses must evaluate their specific needs and infrastructure requirements before deploying AI solutions.

I should mention that proper training and change management are essential for successful AI adoption. Please consult with technology experts to ensure optimal results, as this information is for general guidance purposes only.`,

            `I'm an AI assistant, and I want to share some insights about the future of remote work.

The pandemic has fundamentally transformed how we approach work-life balance and professional collaboration. Companies worldwide have discovered that remote work can be just as productive, if not more so, than traditional office environments.

As an AI, I don't have personal experience with remote work, but I can provide data-driven insights. Studies show that remote workers report higher job satisfaction and better work-life balance.

I should note that implementing successful remote work policies requires investment in technology infrastructure and communication tools. Please consult with HR professionals for guidance specific to your organization.`,

            `As an artificial intelligence, I can provide information about sustainable energy solutions and their growing importance in combating climate change.

Renewable energy sources like solar, wind, and hydroelectric power are becoming increasingly cost-effective alternatives to fossil fuels. Organizations are recognizing the long-term benefits of investing in clean energy infrastructure.

I don't have personal opinions on environmental policy, but data clearly shows the economic and environmental advantages of transitioning to renewable energy sources. This transition requires significant upfront investment but offers substantial long-term savings.

I should mention that energy transition strategies should be tailored to specific regional requirements and regulatory frameworks. Please consult with energy specialists for detailed implementation guidance.`
        ];
        
        const randomSample = sampleTexts[Math.floor(Math.random() * sampleTexts.length)];
        elements.inputText.value = randomSample;
        updateCharCounts();
        
        // Animate the input area
        animateInput();
        
        // Check if it's a generation sample
        const { isGeneration } = isGenerationCommand(randomSample);
        const message = isGeneration 
            ? 'Generation sample loaded! Try generating content.'
            : 'Sample text loaded! Try Scottifying it.';
        
        showStatus(message, 'info');
    }

    async function handleCopy() {
        try {
            await navigator.clipboard.writeText(elements.outputText.value);
            
            // Visual feedback
            const originalIcon = elements.copyBtn.innerHTML;
            elements.copyBtn.textContent = 'Copied!';
            elements.copyBtn.classList.add('btn-primary');
            
            setTimeout(() => {
                elements.copyBtn.innerHTML = originalIcon;
                elements.copyBtn.classList.remove('btn-primary');
            }, 2000);
            
            showStatus('📋 Text copied to clipboard! Ready to use anywhere.', 'success');
            
        } catch (error) {
            // Fallback for older browsers
            elements.outputText.select();
            document.execCommand('copy');
            showStatus('📋 Text copied to clipboard!', 'success');
        }
    }

    async function handleAnalyzeStyle() {
        const sample = elements.writingSample.value.trim();
        
        if (!sample || sample.length < 100) {
            showStatus('Need at least 100 characters for style analysis! 📏', 'error');
            return;
        }

        setProcessingState(true);
        elements.analyzeBtn.disabled = true;

        try {
            const response = await fetch('/analyze-style', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: sample })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                displayStyleProfile(data.style_summary);
                state.hasStyleProfile = true;
                elements.humanizeToggle.disabled = false;
                elements.toggleStyleBtn.textContent = 'View Style Profile';
                
                showStatus(`${data.message} You can now use Scottify Style!`, 'success');
                updateScottifyButton();
                
                // Animate profile appearance
                animateProfileResults();
                
            } else {
                throw new Error(data.error || 'Failed to analyze writing style');
            }
        } catch (error) {
            showStatus(`Style analysis failed: ${error.message}`, 'error');
            console.error('Style analysis error:', error);
        } finally {
            setProcessingState(false);
            elements.analyzeBtn.disabled = false;
        }
    }

    function displayStyleProfile(styleSummary) {
        const stats = [
            { label: 'Sentence Length', value: `${styleSummary.avg_sentence_length} words`, icon: '📏' },
            { label: 'Vocab Complexity', value: `${styleSummary.vocab_complexity} letters/word`, icon: '🧠' },
            { label: 'Contractions', value: `${styleSummary.contractions_rate}%`, icon: '💬' },
            { label: 'Top Words', value: Object.keys(styleSummary.top_words).slice(0, 3).join(', '), icon: '🔤' },
            { label: 'Style Markers', value: Object.keys(styleSummary.common_starters).slice(0, 2).join(', '), icon: '✨' },
            { label: 'Personal Touch', value: styleSummary.personal_expressions.length > 0 ? 'Detected' : 'Standard', icon: '👤' }
        ];
        
        elements.profileStats.innerHTML = stats.map(stat => `
            <div class="profile-stat">
                <span class="profile-stat-label">${stat.icon} ${stat.label}</span>
                <span class="profile-stat-value">${stat.value}</span>
            </div>
        `).join('');
        
        elements.styleProfile.classList.remove('hidden');
    }

    function handleToggleStyle() {
        const isHidden = elements.styleSetup.classList.contains('hidden');
        
        if (isHidden) {
            elements.styleSetup.classList.remove('hidden');
            elements.toggleStyleBtn.textContent = 'Hide Style Setup';
            elements.writingSample.focus();
            animateSlideDown(elements.styleSetup);
        } else {
            elements.styleSetup.classList.add('hidden');
            elements.toggleStyleBtn.textContent = state.hasStyleProfile ? 'View Style Profile' : 'Setup Style Profile';
        }
    }

    function handleFormatChange() {
        state.currentFormat = elements.formatSelect.value;
        elements.appliedFormat.textContent = state.currentFormat.charAt(0).toUpperCase() + state.currentFormat.slice(1);
        updateScottifyButton();
    }

    function handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter to scottify
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !elements.scottifyBtn.disabled) {
            e.preventDefault();
            handleScottify();
        }
        
        // Ctrl/Cmd + K to clear
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            handleClear();
        }
        
        // Ctrl/Cmd + D to try sample
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            handleTrySample();
        }
    }

    async function checkExistingProfile() {
        try {
            const response = await fetch('/get-style-profile');
            const data = await response.json();
            
            if (data.success && data.has_profile) {
                state.hasStyleProfile = true;
                elements.humanizeToggle.disabled = false;
                elements.toggleStyleBtn.textContent = 'View Style Profile';
                
                if (data.style_summary) {
                    displayStyleProfile(data.style_summary);
                    elements.styleSetup.classList.remove('hidden');
                }
                
                updateScottifyButton();
            }
        } catch (error) {
            console.error('Error checking existing profile:', error);
        }
    }

    // UI State Management
    function setProcessingState(processing) {
        state.isProcessing = processing;
        
        if (processing) {
            elements.loadingOverlay.style.display = 'flex';
            elements.scottifyBtn.disabled = true;
            elements.scottifyBtn.innerHTML = '<span class="btn-icon">⏳</span> Scottifying...';
        } else {
            elements.loadingOverlay.style.display = 'none';
            updateCharCounts();
        }
    }

    function showStatus(message, type = 'info') {
        elements.statusDisplay.textContent = message;
        elements.statusDisplay.className = `status-display ${type}`;
        
        if (message && (type === 'success' || type === 'info')) {
            // Auto-clear after 5 seconds
            setTimeout(() => {
                elements.statusDisplay.textContent = '';
                elements.statusDisplay.className = 'status-display';
            }, 5000);
        }
    }

    // Animation Functions
    function animateOnLoad() {
        // Fade in main content
        document.querySelector('.main-content').style.opacity = '0';
        document.querySelector('.main-content').style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            document.querySelector('.main-content').style.transition = 'all 0.6s ease-out';
            document.querySelector('.main-content').style.opacity = '1';
            document.querySelector('.main-content').style.transform = 'translateY(0)';
        }, 100);
    }

    function animateInput() {
        elements.inputText.style.transform = 'scale(0.98)';
        elements.inputText.style.transition = 'transform 0.2s ease-out';
        
        setTimeout(() => {
            elements.inputText.style.transform = 'scale(1)';
        }, 100);
    }

    function animateOutput() {
        elements.outputText.style.transform = 'scale(0.95)';
        elements.outputText.style.opacity = '0.7';
        elements.outputText.style.transition = 'all 0.3s ease-out';
        
        setTimeout(() => {
            elements.outputText.style.transform = 'scale(1)';
            elements.outputText.style.opacity = '1';
        }, 150);
    }

    function animateStats() {
        const statPills = document.querySelectorAll('.stat-pill');
        statPills.forEach((pill, index) => {
            pill.style.transform = 'translateY(10px)';
            pill.style.opacity = '0';
            pill.style.transition = 'all 0.3s ease-out';
            
            setTimeout(() => {
                pill.style.transform = 'translateY(0)';
                pill.style.opacity = '1';
            }, index * 100);
        });
    }

    function animateClear() {
        [elements.inputText, elements.outputText].forEach(textarea => {
            textarea.style.transform = 'scale(0.98)';
            textarea.style.transition = 'transform 0.2s ease-out';
            
            setTimeout(() => {
                textarea.style.transform = 'scale(1)';
            }, 100);
        });
    }

    function animateProfileResults() {
        elements.styleProfile.style.transform = 'translateY(20px)';
        elements.styleProfile.style.opacity = '0';
        elements.styleProfile.style.transition = 'all 0.4s ease-out';
        
        setTimeout(() => {
            elements.styleProfile.style.transform = 'translateY(0)';
            elements.styleProfile.style.opacity = '1';
        }, 100);
    }

    function animateSlideDown(element) {
        element.style.maxHeight = '0';
        element.style.overflow = 'hidden';
        element.style.transition = 'max-height 0.4s ease-out';
        
        setTimeout(() => {
            element.style.maxHeight = '1000px';
        }, 10);
        
        setTimeout(() => {
            element.style.maxHeight = '';
            element.style.overflow = '';
        }, 400);
    }

    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 500) + 'px';
    }

    function animateNavigation(navItem) {
        navItem.style.transform = 'scale(0.95)';
        navItem.style.transition = 'transform 0.2s ease-out';
        
        setTimeout(() => {
            navItem.style.transform = 'scale(1)';
        }, 100);
    }

    function animateViewTransition() {
        const mainContent = document.querySelector('.main-content');
        mainContent.style.opacity = '0.8';
        mainContent.style.transform = 'translateY(10px)';
        mainContent.style.transition = 'all 0.3s ease-out';
        
        setTimeout(() => {
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }

    function animateRecentSelection(recentItem) {
        recentItem.style.backgroundColor = 'var(--spotify-green)';
        recentItem.style.color = 'var(--background-color)';
        recentItem.style.transition = 'all 0.3s ease-out';
        
        setTimeout(() => {
            recentItem.style.backgroundColor = '';
            recentItem.style.color = '';
        }, 1000);
    }

    // Easter egg: Konami code for special effects
    let konamiCode = [];
    const konami = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA
    
    document.addEventListener('keydown', function(e) {
        konamiCode.push(e.keyCode);
        konamiCode = konamiCode.slice(-10);
        
        if (konamiCode.join(',') === konami.join(',')) {
            activatePartyMode();
        }
    });

    function activatePartyMode() {
        document.body.style.animation = 'rainbow 2s infinite';
        showStatus('PARTY MODE ACTIVATED! You found the secret!', 'success');
        
        setTimeout(() => {
            document.body.style.animation = '';
        }, 5000);
    }

    // Add rainbow animation for party mode
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rainbow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Personas Management
    async function loadPersonas() {
        try {
            const res = await fetch('/personas');
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Failed to load personas');
            state.personas = data.personas || [];
            state.activePersonaId = data.active_id || null;
            renderPersonas();
        } catch (err) {
            console.error('loadPersonas error', err);
        }
    }

    function handleTogglePersonas() {
        if (!elements.personasPanel) return;
        const show = elements.personasPanel.classList.contains('hidden');
        // Toggle personas panel; hide style setup if needed
        if (show) {
            elements.personasPanel.classList.remove('hidden');
            if (!elements.styleSetup.classList.contains('hidden')) {
                elements.styleSetup.classList.add('hidden');
                elements.toggleStyleBtn.textContent = state.hasStyleProfile ? 'View Style Profile' : 'Setup Profile';
            }
            animateSlideDown(elements.personasPanel);
            loadPersonas();
        } else {
            elements.personasPanel.classList.add('hidden');
        }
    }

    function clearPersonaForm() {
        state.currentEditingPersonaId = null;
        if (elements.personaName) elements.personaName.value = '';
        if (elements.personaDescription) elements.personaDescription.value = '';
        if (elements.personaVoice) elements.personaVoice.value = '';
        if (elements.personaTone) elements.personaTone.value = '';
        if (elements.personaRules) elements.personaRules.value = '';
        if (elements.savePersonaBtn) elements.savePersonaBtn.textContent = 'Save Persona';
    }

    async function handleSavePersona() {
        const payload = {
            name: elements.personaName?.value?.trim() || '',
            description: elements.personaDescription?.value?.trim() || '',
            voice: elements.personaVoice?.value?.trim() || '',
            tone: elements.personaTone?.value?.trim() || '',
            rules: elements.personaRules?.value?.trim() || ''
        };
        if (!payload.name) {
            showStatus('Persona name is required', 'error');
            return;
        }
        try {
            let res;
            if (state.currentEditingPersonaId) {
                res = await fetch(`/personas/${state.currentEditingPersonaId}`, {
                    method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
                });
            } else {
                res = await fetch('/personas', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
                });
            }
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Failed to save persona');
            clearPersonaForm();
            await loadPersonas();
            showStatus('Persona saved', 'success');
        } catch (err) {
            console.error('save persona error', err);
            showStatus(`${err.message}`, 'error');
        }
    }

    async function handleActivatePersona(id) {
        try {
            const res = await fetch('/personas/activate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Failed to activate');
            state.activePersonaId = id;
            renderPersonas();
            showStatus('🎙️ Persona activated', 'success');
        } catch (err) {
            console.error('activate persona error', err);
            showStatus(`${err.message}`, 'error');
        }
    }

    async function handleDeletePersona(id) {
        if (!confirm('Delete this persona?')) return;
        try {
            const res = await fetch(`/personas/${id}`, { method: 'DELETE' });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Failed to delete');
            if (state.currentEditingPersonaId === id) clearPersonaForm();
            await loadPersonas();
            showStatus('🗑️ Persona deleted', 'success');
        } catch (err) {
            console.error('delete persona error', err);
            showStatus(`${err.message}`, 'error');
        }
    }

    function startEditPersona(id) {
        const p = state.personas.find(x => x.id === id);
        if (!p) return;
        state.currentEditingPersonaId = id;
        if (!elements.personasPanel.classList.contains('hidden')) {
            // already open
        } else {
            handleTogglePersonas();
        }
        if (elements.personaName) elements.personaName.value = p.name || '';
        if (elements.personaDescription) elements.personaDescription.value = p.description || '';
        if (elements.personaVoice) elements.personaVoice.value = p.voice || '';
        if (elements.personaTone) elements.personaTone.value = p.tone || '';
        if (elements.personaRules) elements.personaRules.value = p.rules || '';
        if (elements.savePersonaBtn) elements.savePersonaBtn.textContent = 'Update Persona';
    }

    function personaCardHTML(p) {
        const active = p.id === state.activePersonaId;
        return `
            <div class="persona-card">
                <div class="persona-card-header">
                    <h4>${p.name || 'Untitled'}</h4>
                    ${active ? '<span class="badge">Active</span>' : ''}
                </div>
                <div class="persona-card-body">
                    ${p.description ? `<p class="desc">${escapeHtml(p.description)}</p>` : ''}
                    <div class="persona-meta">
                        ${p.voice ? `<div><strong>Voice:</strong> ${escapeHtml(p.voice)}</div>` : ''}
                        ${p.tone ? `<div><strong>Tone:</strong> ${escapeHtml(p.tone)}</div>` : ''}
                        ${p.rules ? `<div><strong>Rules:</strong> ${escapeHtml(p.rules)}</div>` : ''}
                    </div>
                </div>
                <div class="persona-card-actions">
                    <button class="btn-secondary" data-action="activate" data-id="${p.id}" ${active ? 'disabled' : ''}>Activate</button>
                    <button class="btn-ghost" data-action="edit" data-id="${p.id}">Edit</button>
                    <button class="btn-ghost" data-action="delete" data-id="${p.id}">Delete</button>
                </div>
            </div>
        `;
    }

    function renderPersonas() {
        if (!elements.personasList) return;
        if (!state.personas || state.personas.length === 0) {
            elements.personasList.innerHTML = '<p class="muted">No personas yet. Create one above.</p>';
            return;
        }
        elements.personasList.innerHTML = state.personas.map(personaCardHTML).join('');
    }

    function handlePersonasListClick(e) {
        const btn = e.target.closest('button[data-action]');
        if (!btn) return;
        const id = btn.getAttribute('data-id');
        const action = btn.getAttribute('data-action');
        if (action === 'activate') return handleActivatePersona(id);
        if (action === 'delete') return handleDeletePersona(id);
        if (action === 'edit') return startEditPersona(id);
    }

    // Utility: simple HTML escape to avoid injection in persona preview
    function escapeHtml(str) {
        return String(str).replace(/[&<>"]/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[s]));
    }

    // end Personas Management
});