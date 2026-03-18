// Results Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    if (typeof resultsData === 'undefined') {
        console.error('No results data found');
        return;
    }

    // Parse results if it's a string
    const results = typeof resultsData === 'string' ? JSON.parse(resultsData) : resultsData;
    
    // Populate career matches
    populateCareerMatches(results.career_matches);
    
    // Populate strengths
    populateStrengths(results.top_strengths);
    
    // Populate skill gaps
    populateSkillGaps(results.skill_gaps);
    
    // Populate roadmap
    populateRoadmap(results.learning_roadmap);
    
    // Populate next steps
    populateNextSteps(results.next_steps);
    
    // Populate advice
    populateAdvice(results.personalized_advice);
});

function populateCareerMatches(careers) {
    const container = document.getElementById('careerMatches');
    if (!container) return;
    
    container.innerHTML = careers.map((career, index) => `
        <div class="career-card" style="animation-delay: ${index * 0.1}s">
            <div class="career-header">
                <div class="career-rank">#${index + 1}</div>
                <div class="career-match">${career.match_percentage}% Match</div>
            </div>
            <h3>${career.title}</h3>
            <p class="career-description">${career.description}</p>
            
            <div class="career-details">
                <div class="detail-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="1" x2="12" y2="23"></line>
                        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                    </svg>
                    <div>
                        <strong>Salary Range</strong>
                        <span>${career.salary_range}</span>
                    </div>
                </div>
                
                <div class="detail-item">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                    <div>
                        <strong>Growth Outlook</strong>
                        <span>${career.growth_outlook}</span>
                    </div>
                </div>
            </div>
            
            <div class="why-fit">
                <strong>Why This Fits You:</strong>
                <p>${career.why_good_fit}</p>
            </div>
            
            <div class="skills-needed">
                <strong>Key Skills:</strong>
                <div class="skill-tags">
                    ${career.skills_needed.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function populateStrengths(strengths) {
    const container = document.getElementById('strengths');
    if (!container) return;
    
    container.innerHTML = strengths.map((strength, index) => `
        <div class="strength-item" style="animation-delay: ${index * 0.1}s">
            <div class="strength-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
            <p>${strength}</p>
        </div>
    `).join('');
}

function populateSkillGaps(gaps) {
    const container = document.getElementById('skillGaps');
    if (!container) return;
    
    const priorityColors = {
        'High': '#EF4444',
        'Medium': '#F59E0B',
        'Low': '#10B981'
    };
    
    container.innerHTML = gaps.map((gap, index) => `
        <div class="skill-gap-item" style="animation-delay: ${index * 0.1}s">
            <div class="gap-header">
                <h4>${gap.skill}</h4>
                <span class="priority-badge" style="background: ${priorityColors[gap.priority] || '#6366F1'};">
                    ${gap.priority} Priority
                </span>
            </div>
            <p>${gap.how_to_develop}</p>
        </div>
    `).join('');
}

function populateRoadmap(roadmap) {
    const container = document.getElementById('roadmap');
    if (!container) return;
    
    container.innerHTML = roadmap.map((phase, index) => `
        <div class="roadmap-phase" style="animation-delay: ${index * 0.15}s">
            <div class="phase-number">${index + 1}</div>
            <div class="phase-content">
                <h3>${phase.phase}</h3>
                <p class="phase-focus"><strong>Focus:</strong> ${phase.focus}</p>
                
                <div class="phase-actions">
                    <strong>Actions:</strong>
                    <ul>
                        ${phase.actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="phase-resources">
                    <strong>Resources:</strong>
                    <div class="resource-tags">
                        ${phase.resources.map(resource => `<span class="resource-tag">${resource}</span>`).join('')}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function populateNextSteps(steps) {
    const container = document.getElementById('nextSteps');
    if (!container) return;
    
    container.innerHTML = steps.map((step, index) => `
        <div class="next-step-item" style="animation-delay: ${index * 0.1}s">
            <div class="step-number">${index + 1}</div>
            <p>${step}</p>
        </div>
    `).join('');
}

function populateAdvice(advice) {
    const container = document.getElementById('advice');
    if (!container) return;
    
    container.innerHTML = `<p>${advice}</p>`;
}
