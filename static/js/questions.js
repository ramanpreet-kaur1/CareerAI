// Questions Navigation and Auto-save
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('assessmentForm');
    const questionCards = document.querySelectorAll('.question-card');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const progressBar = document.getElementById('progressBar');
    const currentQuestionSpan = document.getElementById('currentQuestion');
    const progressPercentSpan = document.getElementById('progressPercent');
    const autosaveIndicator = document.getElementById('autosaveIndicator');
    
    let currentQuestion = 1;
    const totalQuestions = 15;
    
    // Initialize
    updateUI();
    
    // Slider real-time updates
    const sliders = document.querySelectorAll('.skill-slider, .big-slider');
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            const targetId = this.getAttribute('data-target');
            const target = document.getElementById(targetId);
            if (target) {
                target.textContent = this.value;
            }
        });
    });
    
    // Textarea character count
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const charCount = textarea.parentElement.querySelector('.char-count');
        textarea.addEventListener('input', function() {
            if (charCount) {
                charCount.textContent = `${this.value.length}/500`;
            }
        });
    });
    
    // Max checkbox limit (3 for academic subjects)
    const maxCheckboxes = document.querySelectorAll('.max-check-3');
    maxCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkboxGroup = document.querySelectorAll('.max-check-3:checked');
            if (checkboxGroup.length > 3) {
                this.checked = false;
                alert('You can select a maximum of 3 subjects.');
            }
        });
    });
    
    // Previous button
    prevBtn.addEventListener('click', function() {
        if (currentQuestion > 1) {
            currentQuestion--;
            showQuestion(currentQuestion);
            autoSave();
        }
    });
    
    // Next button
    nextBtn.addEventListener('click', function() {
        if (validateCurrentQuestion()) {
            if (currentQuestion < totalQuestions) {
                currentQuestion++;
                showQuestion(currentQuestion);
                autoSave();
            }
        }
    });
    
    // Show specific question
    function showQuestion(questionNum) {
        questionCards.forEach(card => {
            card.classList.remove('active');
            if (parseInt(card.getAttribute('data-question')) === questionNum) {
                card.classList.add('active');
            }
        });
        
        updateUI();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // Update UI elements
    function updateUI() {
        // Update progress
        const progress = Math.round((currentQuestion / totalQuestions) * 100);
        progressBar.style.width = progress + '%';
        currentQuestionSpan.textContent = currentQuestion;
        progressPercentSpan.textContent = progress;
        
        // Update buttons
        prevBtn.disabled = currentQuestion === 1;
        
        if (currentQuestion === totalQuestions) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'inline-flex';
        } else {
            nextBtn.style.display = 'inline-flex';
            submitBtn.style.display = 'none';
        }
    }
    
    // Validate current question
    function validateCurrentQuestion() {
        const currentCard = document.querySelector(`.question-card[data-question="${currentQuestion}"]`);
        
        // Check for required radio buttons
        const radioGroups = currentCard.querySelectorAll('input[type="radio"]');
        if (radioGroups.length > 0) {
            const radioName = radioGroups[0].getAttribute('name');
            const checked = currentCard.querySelector(`input[name="${radioName}"]:checked`);
            if (!checked) {
                alert('Please select an option before continuing.');
                return false;
            }
        }
        
        // Check for checkboxes (at least one for Q1)
        if (currentQuestion === 1) {
            const checkboxes = currentCard.querySelectorAll('input[type="checkbox"]:checked');
            if (checkboxes.length === 0) {
                alert('Please select at least one activity that excites you.');
                return false;
            }
        }
        
        // Check for required textareas
        const textareas = currentCard.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            if (textarea.value.trim().length < 10 && (currentQuestion === 5 || currentQuestion === 14)) {
                alert('Please provide a more detailed answer (at least 10 characters).');
                return false;
            }
        });
        
        // Check ranking (Q9)
        if (currentQuestion === 9) {
            const selects = currentCard.querySelectorAll('select');
            let allSelected = true;
            selects.forEach(select => {
                if (!select.value) {
                    allSelected = false;
                }
            });
            if (!allSelected) {
                alert('Please rank all priorities before continuing.');
                return false;
            }
        }
        
        return true;
    }
    
    // Auto-save functionality
    function autoSave() {
        showAutosaveIndicator();
        
        // Save to localStorage as backup
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        localStorage.setItem('assessment_backup', JSON.stringify(data));
    }
    
    // Show autosave indicator
    function showAutosaveIndicator() {
        autosaveIndicator.classList.add('show');
        setTimeout(() => {
            autosaveIndicator.classList.remove('show');
        }, 2000);
    }
    
    // Restore from localStorage on page load
    function restoreFromBackup() {
        const backup = localStorage.getItem('assessment_backup');
        if (backup) {
            const data = JSON.parse(backup);
            for (let key in data) {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    if (input.type === 'checkbox' || input.type === 'radio') {
                        if (Array.isArray(data[key])) {
                            data[key].forEach(value => {
                                const element = form.querySelector(`[name="${key}"][value="${value}"]`);
                                if (element) element.checked = true;
                            });
                        } else {
                            const element = form.querySelector(`[name="${key}"][value="${data[key]}"]`);
                            if (element) element.checked = true;
                        }
                    } else {
                        input.value = data[key];
                        // Update slider displays
                        const targetId = input.getAttribute('data-target');
                        if (targetId) {
                            document.getElementById(targetId).textContent = data[key];
                        }
                    }
                }
            }
        }
    }
    
    restoreFromBackup();
    
    // Submit form
    submitBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (validateCurrentQuestion()) {
            // Clear localStorage backup
            localStorage.removeItem('assessment_backup');
            form.submit();
        }
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' && currentQuestion < totalQuestions) {
            nextBtn.click();
        } else if (e.key === 'ArrowLeft' && currentQuestion > 1) {
            prevBtn.click();
        }
    });
});
