async function getBooks() {
    const input = document.getElementById('userPrompt');
    const grid = document.getElementById('resultsGrid');
    const loading = document.getElementById('loading');
    const prompt = input.value;

    if (!prompt) return;

    // UI Reset
    grid.innerHTML = '';
    loading.classList.remove('hidden');

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt }),
        });

        const books = await response.json();

        loading.classList.add('hidden');

        if (books.error) {
            grid.innerHTML = `<p>Error: ${books.error}</p>`;
            return;
        }

        // Render Books
        books.forEach(book => {
            const card = document.createElement('div');
            card.className = 'card';
            
            // Generate a random gradient for the mock cover
            const gradient = getRandomGradient();
            
            card.innerHTML = `
                <div class="cover-placeholder" style="background: ${gradient}">
                    ${getInitials(book.title)}
                </div>
                <h3>${book.title}</h3>
                <p class="author">${book.author}</p>
                <div class="rating">
                    <span class="stars">★★★★★</span>
                    <span>$${(Math.random() * 20 + 10).toFixed(2)} (random price placeholder)</span>
                </div>
            `;
            grid.appendChild(card);
        });

    } catch (error) {
        console.error('Error:', error);
        loading.classList.add('hidden');
        grid.innerHTML = '<p>Something went wrong. Please check your API keys.</p>';
    }
}

// Helper to make the covers look distinct
function getRandomGradient() {
    const colors = [
        ['#ff9a9e', '#fecfef'],
        ['#a18cd1', '#fbc2eb'],
        ['#84fab0', '#8fd3f4'],
        ['#fccb90', '#d57eeb'],
        ['#e0c3fc', '#8ec5fc']
    ];
    const choice = colors[Math.floor(Math.random() * colors.length)];
    return `linear-gradient(120deg, ${choice[0]} 0%, ${choice[1]} 100%)`;
}

// Helper to put text on the cover
function getInitials(title) {
    return title.split(' ').slice(0, 3).map(n => n[0]).join('').toUpperCase();
}