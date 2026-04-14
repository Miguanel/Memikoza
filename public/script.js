// --- KONFIGURACJA GIST --- //
const GIST_ID = '0df708e9d1973f6ea26340beba9a1038';
const GITHUB_USER = 'Miguanel'; // <-- Tego najwyraźniej brakuje u Ciebie w pliku!

// Adres URL do surowego pliku JSON
const API_URL = `https://gist.githubusercontent.com/${GITHUB_USER}/${GIST_ID}/raw/memy.json?nocache=${new Date().getTime()}`;

// --- LOGIKA PERSYSTENCJI (LocalStorage) --- //
let currentRotation = 0;
let currentScale = 1.0;

function loadSettings() {
    const savedRotation = localStorage.getItem('memikoza_rotation');
    const savedScale = localStorage.getItem('memikoza_scale');

    if (savedRotation !== null) {
        currentRotation = parseInt(savedRotation);
        applyRotation();
    }
    if (savedScale !== null) {
        currentScale = parseFloat(savedScale);
        applyScaling(currentScale);
        document.getElementById('page-scale-slider').value = currentScale;
    }
}

function saveSettings() {
    localStorage.setItem('memikoza_rotation', currentRotation);
    localStorage.setItem('memikoza_scale', currentScale);
}

// --- NOWY ALGORYTM ROTACJI STRONY --- //
function rotatePage() {
    currentRotation = (currentRotation + 90) % 720;  // Zwrócone na 90 po usunięciu dublujących się zdarzeń
    applyRotation();
    saveSettings();
}

function applyRotation() {
    const wrapper = document.getElementById('app-wrapper');
    const isSideways = currentRotation % 180 !== 0;

    if (isSideways) {
        wrapper.style.width = '100vh';
        wrapper.style.height = '100vw';
    } else {
        wrapper.style.width = '100vw';
        wrapper.style.height = '100vh';
    }

    wrapper.style.transform = `translate(-50%, -50%) rotate(${currentRotation}deg)`;
}

// --- NOWY ALGORYTM SKALOWANIA PROPORCJONALNEGO --- //
const scalingPanel = document.getElementById('scaling-panel');
const scaleSlider = document.getElementById('page-scale-slider');
const memeContent = document.getElementById('meme-content');

function toggleScalingPanel() {
    if (scalingPanel.style.display === 'block') {
        scalingPanel.style.display = 'none';
    } else {
        scalingPanel.style.display = 'block';
    }
}

memeContent.addEventListener('click', () => {
    scalingPanel.style.display = 'none';
});

scaleSlider.addEventListener('input', (event) => {
    currentScale = parseFloat(event.target.value);
    applyScaling(currentScale);
});

scaleSlider.addEventListener('change', () => {
    saveSettings();
});

// POPRAWIONA FUNKCJA SKALOWANIA (Używa natywnego 'zoom')
function applyScaling(scaleValue) {
    const tabContents = document.querySelectorAll('.tabcontent');

    tabContents.forEach(content => {
        // 1. Resetujemy stare, błędne style z poprzedniej wersji (aby nie psuły widoku)
        content.style.transform = 'none';
        content.style.width = '100%';

        // 2. Aplikujemy 'zoom' - to właściwość, która poprawnie powiększa całą strukturę
        // zachowując naturalne zawijanie tekstu i granice elementów (layout flow).
        content.style.zoom = scaleValue;
    });
}

// --- FAB - LOGIKA MENU (Speed Dial) --- //
const fabMain = document.getElementById('fab-main');
const fabActions = document.getElementById('fab-actions');

let fabOpen = false;

fabMain.addEventListener('click', function() {
    fabOpen = !fabOpen;
    if (fabOpen) {
        fabActions.classList.add('fab-active');
        fabMain.textContent = 'Ukryj';
    } else {
        fabActions.classList.remove('fab-active');
        fabMain.textContent = 'Pokaż';
        scalingPanel.style.display = 'none';
    }
});

// Usunięto tu eventListenery dla rotacji i skali, by zapobiec dublowaniu (teraz tylko onclick w HTML to kontroluje)

const allActions = document.querySelectorAll('.fab-action');
allActions.forEach(btn => {
    if (btn.classList.contains('btn-rotate') || btn.classList.contains('btn-scale')) return;

    btn.addEventListener('click', () => {
        fabActions.classList.remove('fab-active');
        fabMain.textContent = 'Pokaż';
        fabOpen = false;
        scalingPanel.style.display = 'none';
    });
});

// --- LOGIKA ZAKŁADEK, WIZUALIZACJI ZAKŁADEK I RENDEROWANIA --- //
function openPage(pageName, btnElement) {
    document.getElementById('scroll-container').scrollTo(0, 0);

    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    document.getElementById(pageName).style.display = "block";

    // Zmiana koloru aktywnego przycisku na czarny
    if (btnElement) {
        // Zresetuj wszystkie przyciski memowe na biały tekst
        const tabs = document.querySelectorAll('.fab-actions .fab-action:not(.btn-rotate):not(.btn-scale)');
        tabs.forEach(btn => btn.style.color = 'white');

        // Ustaw kliknięty przycisk na czarny tekst
        btnElement.style.color = 'black';
    }
}

async function loadData() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        document.getElementById('loadingMessage').style.display = 'none';

        renderSection('Jbzd', data.jebmem || {}, data.jebvmem || {});
        renderSection('Jm', data.urljm || {}, data.urljvm || {});
        renderSection('Demo', data.demomemp || {}, data.demomemv || {});
        renderSection('Kwjk', data.kwmems || {}, data.kwvmems || {});
        renderSection('Redmik', data.rmmems);
        renderSection('Atom', data.agmems);

        // Otwórz domyślną zakładkę (i przypisz pierwszy przycisk jako czarny)
        openPage('Jbzd', document.querySelector('.btn1'));

    } catch (error) {
        console.error("Błąd podczas pobierania:", error);
        document.getElementById('loadingMessage').innerText = "Błąd pobierania bazy memów :(";
    }
}

function renderSection(containerId, imagesObj = {}, videosObj = {}) {
    const container = document.getElementById(containerId);
    let htmlContent = '<div>&nbsp;</div>';

    if (imagesObj && Object.keys(imagesObj).length > 0) {
        if (containerId === 'Kwjk') htmlContent += '<blockquote class="lista">';

        Object.values(imagesObj).forEach(val => {
            htmlContent += `
            <div class="mems picture">
                <div class="mems-title-area">
                    <div class="tyt"> -- ${val[0]} --</div>
                </div>
                <div class="mems-content-area">
                    <img src="${val[1]}" onclick="window.open('${val[2]}','_blank')" tabindex="1" alt="${val[0]}">
                </div>
            </div>`;
        });

        if (containerId === 'Kwjk') htmlContent += '</blockquote>';
    }

    if (videosObj && Object.keys(videosObj).length > 0) {
        Object.values(videosObj).forEach(val => {
            htmlContent += `
            <div class="mems vidjo mems">
                <div class="mems-title-area">
                    <div class="tyt"> -- ${val[0]} --</div>
                </div>
                <div class="mems-content-area">
                    <video autoplay loop muted playsinline controls onclick="window.open('${val[2]}','_blank')" style="cursor:pointer">
                        <source src="${val[1]}">
                    </video>
                </div>
            </div>`;
        });
    }

    container.innerHTML = htmlContent;
}

window.addEventListener('DOMContentLoaded', function() {
    loadSettings();
    loadData();
});