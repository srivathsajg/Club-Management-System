// Motivational statements that will be displayed daily in h1 elements
const motivationalStatements = [
    "Achieve greatness today!",
    "Your potential is limitless!",
    "Make today amazing!",
    "Embrace the challenge!",
    "Success begins with you!",
    "Dream big, achieve bigger!",
    "Turn obstacles into opportunities!",
    "Progress over perfection!",
    "Today is your day to shine!",
    "Small steps lead to big results!",
    "Believe in yourself!",
    "Create your own success story!",
    "Your attitude determines your direction!",
    "Focus on what matters!",
    "Every day is a new beginning!",
    "Consistency is the key to success!",
    "Challenge yourself every day!",
    "Your only limit is you!",
    "Stay positive, work hard!",
    "Make it happen!",
    "Excellence is not an act but a habit!",
    "The best is yet to come!",
    "Strive for progress, not perfection!",
    "You are stronger than you think!",
    "Today's efforts are tomorrow's results!",
    "Keep moving forward!",
    "Success is a journey, not a destination!",
    "Be the best version of yourself!",
    "Your passion fuels your success!",
    "Determination gets you further than talent!"
];

// Function to get a motivational statement based on the day of the year or randomly for refreshes
function getDailyMotivationalStatement(useRandom = false) {
    if (useRandom) {
        // Generate a random index for page refreshes
        const randomIndex = Math.floor(Math.random() * motivationalStatements.length);
        return motivationalStatements[randomIndex];
    } else {
        // Use day of year for initial page load
        const today = new Date();
        const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
        const statementIndex = dayOfYear % motivationalStatements.length;
        return motivationalStatements[statementIndex];
    }
}

// Function to update h1 elements with motivational statements
function updateH1WithMotivationalStatement() {
    const h1Elements = document.querySelectorAll('h1');
    const statement = getDailyMotivationalStatement();
    
    h1Elements.forEach(h1 => {
        // Check if the h1 contains a welcome message
        if (h1.textContent.includes('Welcome')) {
            // Keep the welcome part and add the motivational statement
            const welcomePart = h1.textContent.split('!');
            if (welcomePart.length > 0) {
                h1.innerHTML = `${welcomePart[0]}! <span class="motivational-text">${statement}</span>`;
            }
        }
    });
}

// Add CSS for the motivational text
function addMotivationalStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .motivational-text {
            display: block;
            font-size: 1.2rem;
            font-weight: 500;
            margin-top: 0.5rem;
            color: #FF69B4;
            font-style: italic;
            animation: fadeIn 1s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
}

// Execute when DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        addMotivationalStyles();
        updateH1WithMotivationalStatement();
    });
} else {
    // DOM already loaded
    addMotivationalStyles();
    updateH1WithMotivationalStatement();
}

// Force a new motivational statement on page refresh
window.addEventListener('load', function() {
    // Get a random motivational statement for page refreshes
    const statement = getDailyMotivationalStatement(true);
    
    // Update h1 elements with the random motivational statement
    const h1Elements = document.querySelectorAll('h1');
    h1Elements.forEach(h1 => {
        if (h1.textContent.includes('Welcome')) {
            const welcomePart = h1.textContent.split('!');
            if (welcomePart.length > 0) {
                h1.innerHTML = `${welcomePart[0]}! <span class="motivational-text">${statement}</span>`;
            }
        }
    });
});