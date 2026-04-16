document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault(); 

    const username = document.getElementById('username').value;
    const goal = document.querySelector('input[name="goal"]:checked').value;
    const allergies = document.getElementById('allergies').value || "None";

    const userData = {
        username: username,
        dietary_goal: goal,
        allergies: allergies,
        persona: "hosteler", 
        preferences: "None",
        current_effort_level: "normal"
    };
    

    try {
        const response = await fetch('http://127.0.0.1:8000/users/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
        });

        if (response.ok) {
            const result = await response.json();
            console.log("User Created:", result);
            
            if (result.id) {
                localStorage.setItem('user_id', result.id);
                console.log("Local ID set to:", result.id);
            }

            document.querySelector('.glass-container').classList.add('exit-animation');
            
            setTimeout(() => {
                window.location.href = "page1.html"; 
            }, 600);
        } else {
            alert("Failed to save profile. Check terminal for errors.");
        }
    } catch (error) {
        console.error("Error connecting to backend:", error);
        alert("Backend server not reachable!");
    }
});