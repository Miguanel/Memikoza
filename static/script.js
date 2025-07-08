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
