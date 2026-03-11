// FAB - Speed Dial logic
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
    }
});

// Zamknij menu po kliknięciu dowolnego przycisku w dymku (opcjonalnie, ale UX-friendly)
const allActions = document.querySelectorAll('.fab-action');
allActions.forEach(btn => {
    btn.addEventListener('click', () => {
        fabActions.classList.remove('fab-active');
        fabMain.textContent = 'Pokaż';
        fabOpen = false;
    });
});

// Zakładki jak dawniej:
function openPage(pageName) {
    window.scrollTo(0, 0);
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    document.getElementById(pageName).style.display = "contents";
}

// Otwórz domyślną zakładkę po załadowaniu
window.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('Jbzd')) {
        openPage('Jbzd');
    }
});

// --- LOGIKA POBIERANIA I RENDEROWANIA DANYCH --- //

// PODMIEŃ NA SWÓJ BIN ID Z JSONBIN.IO
const BIN_ID = '69b1ee90c3097a1dd519978f';
// meta=false zwraca sam json bez metadanych serwisu
const API_URL = `https://api.jsonbin.io/v3/b/${BIN_ID}?meta=false`;

async function loadData() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();

        document.getElementById('loadingMessage').style.display = 'none';

        // Renderujemy poszczególne sekcje
        renderSection('Jbzd', data.jebmem, data.jebvmem);
        renderSection('Jm', data.urljm);
        renderSection('Demo', data.demomemp, data.demomemv);
        renderSection('Kwjk', data.kwmems);
        renderSection('Redmik', data.rmmems);
        renderSection('Atom', data.agmems);

        // Otwórz domyślną zakładkę po załadowaniu
        openPage('Jbzd');

    } catch (error) {
        console.error("Błąd podczas pobierania:", error);
        document.getElementById('loadingMessage').innerText = "Błąd pobierania bazy memów :(";
    }
}

// Uniwersalna funkcja do budowania HTML
function renderSection(containerId, imagesObj = {}, videosObj = {}) {
    const container = document.getElementById(containerId);
    let htmlContent = '<div>&nbsp;</div>';

    // Obrazki
    if (imagesObj && Object.keys(imagesObj).length > 0) {
        if (containerId === 'Kwjk') htmlContent += '<blockquote class="lista">';

        Object.values(imagesObj).forEach(val => {
            htmlContent += `
            <div class="mems">
                <div class="tyt"> -- ${val[0]} --</div>
                <img src="${val[1]}" onclick="window.open('${val[2]}','_blank')" tabindex="1">
            </div>`;
        });

        if (containerId === 'Kwjk') htmlContent += '</blockquote>';
    }

    // Wideo
    if (videosObj && Object.keys(videosObj).length > 0) {
        Object.values(videosObj).forEach(val => {
            htmlContent += `
            <div class="vidjo mems">
                <div class="tyt"> -- ${val[0]} --</div>
                <video autoplay="autoplay" loop="true" muted playsinline controls>
                    <source src="${val[1]}" onclick="window.open('${val[2]}','_blank')">
                </video>
            </div>`;
        });
    }

    container.innerHTML = htmlContent;
}

// Uruchomienie po załadowaniu DOM
window.addEventListener('DOMContentLoaded', function() {
    loadData();
});