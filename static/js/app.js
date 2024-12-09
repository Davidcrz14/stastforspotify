let currentSlide = 0;
const CLIENT_ID = "09ad32ff6cd44f92af6deb600e170ac9";
const REDIRECT_URI = "http://localhost:5000/callback";
const SCOPE = "user-top-read user-read-recently-played";

// Función para generar el estado aleatorio
function generateRandomString(length) {
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return Array.from(crypto.getRandomValues(new Uint8Array(length)))
        .map(x => possible[x % possible.length])
        .join('');
}

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', () => {
    const loginButton = document.getElementById('login-button');
    loginButton.addEventListener('click', initiateLogin);

    // Verificar si estamos en el callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    if (code) {
        handleCallback();
    }
});

// Iniciar el proceso de login
function initiateLogin() {
    const state = generateRandomString(16);
    localStorage.setItem('spotify_auth_state', state);

    const params = new URLSearchParams({
        client_id: CLIENT_ID,
        response_type: 'code',
        redirect_uri: REDIRECT_URI,
        state: state,
        scope: SCOPE
    });

    window.location = `https://accounts.spotify.com/authorize?${params.toString()}`;
}

// Manejar el callback de Spotify
async function handleCallback() {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const storedState = localStorage.getItem('spotify_auth_state');

    if (state === null || state !== storedState) {
        showError('Error de estado en la autenticación');
        return;
    }

    localStorage.removeItem('spotify_auth_state');
    showLoading();

    try {
        const response = await fetch('/api/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code })
        });

        if (!response.ok) throw new Error('Error al obtener el token');

        const data = await response.json();
        await fetchAndDisplayStats(data.access_token);
    } catch (error) {
        showError(error.message);
    }
}

// Mostrar las estadísticas
async function fetchAndDisplayStats(token) {
    try {
        const response = await fetch('/api/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error al obtener estadísticas');

        const stats = await response.json();
        displayStats(stats);
    } catch (error) {
        showError(error.message);
    }
}

// Funciones de UI
function showLoading() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('loading-section').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');
    updateLoadingText();
}

function updateLoadingText() {
    const loadingTexts = [
        "Redirigiendo a Spotify...",
        "Obteniendo tus datos...",
        "Analizando tu música...",
        "Creando tu Wrapped personalizado..."
    ];
    let currentText = 0;
    const loadingElement = document.getElementById('loading-text');

    const interval = setInterval(() => {
        loadingElement.textContent = loadingTexts[currentText];
        currentText = (currentText + 1) % loadingTexts.length;
    }, 2000);

    // Limpiar el intervalo cuando se muestren los resultados
    document.addEventListener('showResults', () => clearInterval(interval));
}

function showResults() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('loading-section').classList.add('hidden');
    const resultsSection = document.getElementById('results-section');
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');
    // Disparar evento para limpiar el intervalo de textos de carga
    document.dispatchEvent(new Event('showResults'));
}

function displayStats(stats) {
    const carousel = document.querySelector('.carousel-inner');
    carousel.innerHTML = '';

    // Agregar imágenes al carrusel
    stats.images.forEach(imageData => {
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${imageData}`;
        img.classList.add('fade-in');
        carousel.appendChild(img);
    });

    showResults();
    setupCarousel();
}

// Configuración del carrusel
function setupCarousel() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const carousel = document.querySelector('.carousel-inner');
    const slides = carousel.children;

    prevBtn.addEventListener('click', () => {
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        updateCarousel();
    });

    nextBtn.addEventListener('click', () => {
        currentSlide = (currentSlide + 1) % slides.length;
        updateCarousel();
    });

    updateCarousel();
}

function updateCarousel() {
    const carousel = document.querySelector('.carousel-inner');
    carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
}

function showError(message) {
    // Implementar manejo de errores
    console.error(message);
}
