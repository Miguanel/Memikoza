// Ukryj sidebar po kliknięciu "Ukryj"
document.getElementById('toggle-button').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var showSidebarButton = document.getElementById('show-sidebar');
    sidebar.classList.add('hidden');
    showSidebarButton.style.display = 'flex';
});

// Pokaż sidebar po kliknięciu pływającego przycisku "Pokaż"
document.getElementById('show-sidebar').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var showSidebarButton = document.getElementById('show-sidebar');
    sidebar.classList.remove('hidden');
    showSidebarButton.style.display = 'none';
});

// Sidebar ukryty domyślnie na mobile przy starcie (na desktopie widoczny)
window.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 900) {
        document.querySelector('.sidebar').classList.add('hidden');
        document.getElementById('show-sidebar').style.display = 'flex';
    } else {
        document.querySelector('.sidebar').classList.remove('hidden');
        document.getElementById('show-sidebar').style.display = 'none';
    }
});

// Przełączanie zakładek (tabcontent)
function openPage(pageName) {
    window.scrollTo(0, 0);
    var i, tabcontent;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    document.getElementById(pageName).style.display = "contents";
}

// (opcjonalnie) Automatycznie pokaż pierwszą zakładkę po załadowaniu
window.addEventListener('DOMContentLoaded', function() {
    // Jeśli chcesz, żeby od razu był wybrany np. Jbzd:
    if (document.getElementById('Jbzd')) {
        openPage('Jbzd');
    }
});
