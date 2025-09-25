document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const inputText = document.getElementById('input-text');
    const outputText = document.getElementById('output-text');
    const cleanButton = document.getElementById('clean-text');
    const clearButton = document.getElementById('clear-input');
    const copyButton = document.getElementById('copy-output');
    const inputCount = document.getElementById('input-count');
    const outputCount = document.getElementById('output-count');
    const cleaningStatus = document.getElementById('cleaning-status');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    // Style profile elements
    const toggleStyleButton = document.getElementById('toggle-style');
    const styleSetup = document.getElementById('style-setup');
    const writingSample = document.getElementById('writing-sample');
    const analyzeStyleButton = document.getElementById('analyze-style');
    const styleProfile = document.getElementById('style-profile');
    const humanizeCheckbox = document.getElementById('humanize-checkbox');
    const sampleCount = document.querySelector('.sample-count');

    let hasStyleProfile = false;

    // Character count updates
    function updateCharCount() {
        const inputLength = inputText.value.length;
        const outputLength = outputText.value.length;
        
        inputCount.textContent = inputLength.toLocaleString();
        outputCount.textContent = outputLength.toLocaleString();
        
        // Enable/disable buttons based on content
        cleanButton.disabled = inputLength === 0;
        copyButton.disabled = outputLength === 0;
    }

    function updateSampleCount() {
        const sampleLength = writingSample.value.length;
        sampleCount.textContent = `${sampleLength.toLocaleString()} characters`;
        
        // Enable analyze button if enough text
        analyzeStyleButton.disabled = sampleLength < 100;
    }

    function displayStyleProfile(styleSummary) {
        const profileStats = document.querySelector('.profile-stats');
        
        const stats = [
            { label: 'Average Sentence Length', value: `${styleSummary.avg_sentence_length} words` },
            { label: 'Vocabulary Complexity', value: `${styleSummary.vocab_complexity} avg letters/word` },
            { label: 'Contractions Usage', value: `${styleSummary.contractions_rate}%` },
            { label: 'Top Words', value: Object.keys(styleSummary.top_words).slice(0, 3).join(', ') },
            { label: 'Common Starters', value: Object.keys(styleSummary.common_starters).slice(0, 3).join(', ') }
        ];
        
        profileStats.innerHTML = stats.map(stat => `
            <div class="stat-item">
                <span class="stat-label">${stat.label}:</span>
                <span class="stat-value">${stat.value}</span>
            </div>
        `).join('');
        
        styleProfile.classList.remove('hidden');
    }

    // Check for existing style profile on load
    async function checkExistingProfile() {
        try {
            const response = await fetch('/get-style-profile');
            const data = await response.json();
            
            if (data.success && data.has_profile) {
                hasStyleProfile = true;
                humanizeCheckbox.disabled = false;
                toggleStyleButton.textContent = 'View Style Profile';
                
                if (data.style_summary) {
                    displayStyleProfile(data.style_summary);
                    styleSetup.classList.remove('hidden');
                }
            }
        } catch (error) {
            console.error('Error checking existing profile:', error);
        }
    }

    // Event listeners
    inputText.addEventListener('input', updateCharCount);
    writingSample.addEventListener('input', updateSampleCount);
    
    // Toggle style setup
    toggleStyleButton.addEventListener('click', function() {
        const isHidden = styleSetup.classList.contains('hidden');
        if (isHidden) {
            styleSetup.classList.remove('hidden');
            toggleStyleButton.textContent = 'Hide Style Setup';
        } else {
            styleSetup.classList.add('hidden');
            toggleStyleButton.textContent = 'Setup Style Profile';
        }
    });
    
    // Analyze writing style
    analyzeStyleButton.addEventListener('click', async function() {
        const sample = writingSample.value.trim();
        
        if (!sample || sample.length < 100) {
            showStatus('Please provide at least 100 characters of writing sample for analysis.', 'error');
            return;
        }

        showLoading(true);
        analyzeStyleButton.disabled = true;

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
                hasStyleProfile = true;
                humanizeCheckbox.disabled = false;
                showStatus(data.message, 'success');
                
                // Update toggle button
                toggleStyleButton.textContent = 'View Style Profile';
            } else {
                throw new Error(data.error || 'Failed to analyze writing style');
            }
        } catch (error) {
            showStatus(`❌ Error analyzing style: ${error.message}`, 'error');
            console.error('Style analysis error:', error);
        } finally {
            showLoading(false);
            analyzeStyleButton.disabled = false;
        }
    });
    
    // Clear input
    clearButton.addEventListener('click', function() {
        inputText.value = '';
        outputText.value = '';
        cleaningStatus.textContent = '';
        updateCharCount();
        inputText.focus();
    });

    // Clean text
    cleanButton.addEventListener('click', async function() {
        const text = inputText.value.trim();
        
        if (!text) {
            showStatus('Please enter some text to clean.', 'error');
            return;
        }

        showLoading(true);
        cleanButton.disabled = true;

        try {
            const response = await fetch('/clean', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    humanize: humanizeCheckbox.checked
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Show the humanized text if available, otherwise the cleaned text
                const finalText = data.humanized || data.cleaned;
                outputText.value = finalText;
                
                // Calculate reduction percentage
                const originalLength = data.original.length;
                const finalLength = finalText.length;
                const reduction = ((originalLength - finalLength) / originalLength * 100).toFixed(1);
                
                let statusMessage = '';
                if (reduction > 0) {
                    statusMessage = `✅ Text cleaned successfully! Removed ${reduction}% of content.`;
                } else {
                    statusMessage = '✅ Text processed. No AI watermarks detected.';
                }
                
                if (data.humanization_applied) {
                    statusMessage += ' 🎨 Humanized to match your writing style.';
                }
                
                showStatus(statusMessage, 'success');
                updateCharCount();
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        } catch (error) {
            showStatus(`❌ Error: ${error.message}`, 'error');
            console.error('Cleaning error:', error);
        } finally {
            showLoading(false);
            cleanButton.disabled = false;
        }
    });

    // Copy to clipboard
    copyButton.addEventListener('click', async function() {
        try {
            await navigator.clipboard.writeText(outputText.value);
            
            // Visual feedback
            const originalText = copyButton.textContent;
            copyButton.textContent = '✅ Copied!';
            copyButton.classList.add('copied');
            
            setTimeout(() => {
                copyButton.textContent = originalText;
                copyButton.classList.remove('copied');
            }, 2000);
            
            showStatus('📋 Text copied to clipboard!', 'success');
        } catch (error) {
            // Fallback for older browsers
            outputText.select();
            document.execCommand('copy');
            showStatus('📋 Text copied to clipboard!', 'success');
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to clean text
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !cleanButton.disabled) {
            e.preventDefault();
            cleanButton.click();
        }
        
        // Ctrl/Cmd + K to clear
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            clearButton.click();
        }
        
        // Ctrl/Cmd + C on output area
        if ((e.ctrlKey || e.metaKey) && e.key === 'c' && document.activeElement === outputText && !copyButton.disabled) {
            copyButton.click();
        }
    });

    // Show status message
    function showStatus(message, type = 'info') {
        cleaningStatus.textContent = message;
        cleaningStatus.className = `status-message ${type}`;
        
        // Auto-clear after 5 seconds for success/info messages
        if (type === 'success' || type === 'info') {
            setTimeout(() => {
                cleaningStatus.textContent = '';
                cleaningStatus.className = 'status-message';
            }, 5000);
        }
    }

    // Show/hide loading overlay
    function showLoading(show) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    // Auto-resize textareas
    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 400) + 'px';
    }

    inputText.addEventListener('input', () => autoResize(inputText));
    outputText.addEventListener('input', () => autoResize(outputText));

    // Initialize
    updateCharCount();
    updateSampleCount();
    checkExistingProfile();
    inputText.focus();

    // Add sample text button for demo purposes
    const addSampleButton = document.createElement('button');
    addSampleButton.textContent = '📝 Try Sample';
    addSampleButton.className = 'btn btn-secondary';
    addSampleButton.style.marginLeft = '10px';
    
    addSampleButton.addEventListener('click', function() {
        const sampleText = `As an AI language model, I'd be happy to help you understand the benefits of renewable energy.

Renewable energy sources like solar, wind, and hydroelectric power offer numerous advantages:

1. **Environmental Benefits**: They produce clean energy without harmful emissions
2. **Economic Advantages**: Long-term cost savings and job creation
3. **Energy Independence**: Reduced reliance on imported fossil fuels

I should mention that the transition to renewable energy requires significant upfront investment. However, the long-term benefits far outweigh the costs.

Please consult with energy professionals for specific advice tailored to your situation, as this information is for general educational purposes only.`;
        
        inputText.value = sampleText;
        updateCharCount();
    });
    
    document.querySelector('.input-actions').appendChild(addSampleButton);
});