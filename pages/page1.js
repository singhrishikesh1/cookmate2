const API_BASE = "http://127.0.0.1:8000";
// Fallback to 1 if user_id isn't set, change this as per your login logic
const USER_ID = localStorage.getItem('user_id') || 1; 

document.addEventListener('DOMContentLoaded', () => {
    const itemInput = document.getElementById('item-input');
    const addBtn = document.querySelector('.add-btn');
    const inventoryList = document.querySelector('.inventory-list');
    const generateBtn = document.querySelector('.generate-btn');
    const displayName = document.getElementById('display-name');

    // 1. Load User Profile (Name and Streak)
    async function loadProfile() {
        try {
            const res = await fetch(`${API_BASE}/users/${USER_ID}`);
            if (res.ok) {
                const user = await res.json();
                displayName.textContent = user.username;
                // If you have a streak element, update it here:
                // document.querySelector('.streak-count').textContent = `${user.streak_count} DAYS`;
            }
        } catch (e) { 
            console.log("Backend offline, using placeholder name."); 
        }
    }

    // 2. Fetch Existing Inventory from DB
    async function fetchInventory() {
        try {
            const res = await fetch(`${API_BASE}/inventory/${USER_ID}`);
            if (res.ok) {
                const items = await res.json();
                inventoryList.innerHTML = ''; 
                items.forEach(item => renderTag(item.name));
            }
        } catch (e) { 
            console.error("Could not fetch inventory"); 
        }
    }

    // 3. UI Helper to create tags
    function renderTag(name) {
        const tag = document.createElement('div');
        tag.className = 'ingredient-tag';
        tag.innerHTML = `${name} <span class="remove-tag" style="margin-left:8px; opacity:0.5">×</span>`;
        
        // Removal logic (optional: add backend DELETE call here)
        tag.onclick = () => tag.remove();
        inventoryList.appendChild(tag);
    }

    // 4. Add Item to Inventory
    addBtn.addEventListener('click', async () => {
        const val = itemInput.value.trim();
        if (!val) return;

        const payload = [{
            name: val,
            quantity: 1.0,
            unit: "unit"
        }];

        try {
            const res = await fetch(`${API_BASE}/inventory/${USER_ID}/bulk-add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                renderTag(val);
                itemInput.value = '';
            }
        } catch (e) {
            alert("Connection to backend failed.");
        }
    });

    // 5. Generate Recipes Logic (Updated for Persona)
    generateBtn.addEventListener('click', (e) => {
        e.preventDefault();

        // Capture Selected Meal Type
        const selectedMeal = document.querySelector('input[name="meal"]:checked').value;
        
        // Capture Selected Persona (The new part!)
        const selectedPersona = document.querySelector('input[name="persona"]:checked').value;

        // Capture current tags from UI to pass to the next page
        const tags = Array.from(document.querySelectorAll('.ingredient-tag'))
                          .map(tag => tag.innerText.replace('×', '').trim());

        // Save everything to localStorage for selection.html to use
        localStorage.setItem('selected_meal', selectedMeal);
        localStorage.setItem('selected_persona', selectedPersona);
        localStorage.setItem('current_ingredients', JSON.stringify(tags));
        localStorage.setItem('user_id', USER_ID);

        // Redirect to the recipe selection screen
        window.location.href = "selection.html";
    });

    // Initial Loads
    loadProfile();
    fetchInventory();
});