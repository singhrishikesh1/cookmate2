
const API_BASE_URL = "http://127.0.0.1:8000";

export const generateRecipe = async (userId, mealType) => {
    try {
        const response = await fetch(`${API_BASE_URL}/generate-recipe/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_id: userId,
                meal_type: mealType
            }),
        });
        return await response.json();
    } catch (error) {
        console.error("Connection failed:", error);
    }
};