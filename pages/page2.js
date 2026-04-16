const API_BASE = "http://127.0.0.1:8000";
const USER_ID = localStorage.getItem('user_id') || 1; 
let recipe = null;
let stepIdx = 0;
let timerInterval = null;
let currentStepSeconds = 0; // Holds the time for the active step

document.addEventListener('DOMContentLoaded', () => {
    const savedRecipe = localStorage.getItem('active_recipe');
    if (savedRecipe) {
        recipe = JSON.parse(savedRecipe);
        initRecipe();
    }
});

function initRecipe() {
    document.getElementById('recipe-name').innerText = recipe.dish_name;
    // Set protein if available
    if(recipe.protein_content) {
        const proteinEl = document.getElementById('recipe-protein');
        if(proteinEl) proteinEl.innerText = recipe.protein_content;
    }
    updateStepUI();
}

// --- NEW: Time Parsing Helper ---
function parseTimeFromText(text) {
    // Looks for "10-12 min" or "5 minutes"
    const timeMatch = text.match(/(\d+)\s*-\s*(\d+)\s*min/i) || text.match(/(\d+)\s*min/i);
    
    if (timeMatch) {
        // Use the higher number in a range (e.g., 12 from 10-12)
        const mins = timeMatch[2] ? parseInt(timeMatch[2]) : parseInt(timeMatch[1]);
        return mins * 60;
    }
    return 0; // Default fallback: 2 minutes if no time is mentioned
}

function updateStepUI() {
    if (!recipe || !recipe.steps) return;
    
    const instruction = recipe.steps[stepIdx];
    document.getElementById('step-indicator').innerText = `STEP ${stepIdx + 1} OF ${recipe.steps.length}`;
    document.getElementById('instruction-text').innerText = instruction;

    // Reset Timer for the new step
    clearInterval(timerInterval);
    currentStepSeconds = parseTimeFromText(instruction); 
    
    const mins = Math.floor(currentStepSeconds / 60);
    const secs = currentStepSeconds % 60;
    
    const display = document.getElementById('timer-display');
    display.innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
    display.style.color = "#f5f0e1";

    // Button States
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    if (prevBtn) prevBtn.style.opacity = (stepIdx === 0) ? "0.3" : "1";
    if (nextBtn) nextBtn.innerText = (stepIdx === recipe.steps.length - 1) ? "FINISH MEAL" : "NEXT STEP";
}

document.getElementById('start-timer-btn').onclick = () => {
    let time = currentStepSeconds; // Start from the parsed time
    const display = document.getElementById('timer-display');
    
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        time--;
        let mins = Math.floor(time / 60);
        let secs = time % 60;
        display.innerText = `${mins}:${secs < 10 ? '0' : ''}${secs}`;
        
        if (time <= 10) display.style.color = "#ff4444"; 
        if (time <= 0) {
            clearInterval(timerInterval);
            display.innerText = "DONE";
        }
    }, 1000);
};

// Navigation and Finish Logic
document.getElementById('next-btn').onclick = async () => {
    if (stepIdx < recipe.steps.length - 1) {
        stepIdx++;
        updateStepUI();
    } else {
        await finishCookingAndCleanup();
    }
};

document.getElementById('prev-btn').onclick = () => {
    if (stepIdx > 0) {
        stepIdx--;
        updateStepUI();
    }
};

async function finishCookingAndCleanup() {
    try {
        const res = await fetch(`${API_BASE}/inventory/${USER_ID}/clear`, {
            method: 'DELETE'
        });
        if (res.ok) alert("Inventory cleared!");
    } catch (e) {
        console.error("Cleanup failed", e);
    } finally {
        localStorage.removeItem('active_recipe');
        window.location.href = "page1.html"; 
    }
}