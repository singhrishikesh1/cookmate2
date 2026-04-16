

const API_BASE = "http://127.0.0.1:8000";

async function fetchRecipes() {
    const gallery = document.getElementById('recipe-gallery');
    const userId = localStorage.getItem('user_id');
    const selectedMeal = localStorage.getItem('selected_meal') || "breakfast";

    try {
        const response = await fetch(`${API_BASE}/generate-recipe/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                user_id: parseInt(userId), 
                meal_type: selectedMeal 
            }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        if (data && data.recipes) {
            renderRecipeCards(data.recipes);
        } else {
            gallery.innerHTML = "<p>No recipes found.</p>";
        }

    } catch (error) {
        console.error("Fetch Error:", error);
        console.log(error)
        gallery.innerHTML = "<p>Chef is busy. Check if backend is running!</p>";
    }
}

function renderRecipeCards(recipes) {
    const gallery = document.getElementById('recipe-gallery');
    gallery.innerHTML = ''; 

    recipes.forEach(recipe => {
        const card = document.createElement('div');
        card.className = 'menu-card';
        card.innerHTML = `
            <div class="card-content">
                <span class="meal-icon">🥘</span>
                <h3>${recipe.dish_name}</h3>
                <p>Effort: ${recipe.effort_score}/10 | Protein: ${recipe.protein_content}</p>
                <button class="generate-btn">START COOKING</button>
            </div>
        `;
        
        card.onclick = () => {
            localStorage.setItem('active_recipe', JSON.stringify(recipe));
            window.location.href = 'page2.html';
        };
        gallery.appendChild(card);
    });
}
fetchRecipes();