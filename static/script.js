document.getElementById('toggle-button').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var buttonGroup = document.getElementById('button-group');
    var showSidebarButton = document.getElementById('show-sidebar');

    if (sidebar.classList.contains('hidden')) {
        sidebar.classList.remove('hidden');
        buttonGroup.style.display = 'flex';
        buttonGroup.style.flexDirection = 'column'; // Ustawienie przycisków w pionie
        showSidebarButton.style.display = 'none';
    } else {
        sidebar.classList.add('hidden');
        buttonGroup.style.display = 'none';
        showSidebarButton.style.display = 'block';
    }
});

document.getElementById('show-sidebar').addEventListener('click', function() {
    var sidebar = document.querySelector('.sidebar');
    var buttonGroup = document.getElementById('button-group');
    var showSidebarButton = document.getElementById('show-sidebar');

    sidebar.classList.remove('hidden');
    buttonGroup.style.display = 'flex';
    buttonGroup.style.flexDirection = 'column'; // Ustawienie przycisków w pionie
    showSidebarButton.style.display = 'none';
});

function flyNavi() {
    var navbar = document.getElementById("navbar");
    var sticky = navbar.offsetTop;
    var tc = document.getElementsByClassName("tabcontent");

    if (window.pageYOffset >= sticky) {
        navbar.classList.add("sticky");
        for (i = 0; i < tc.length; i++) {
            tc[i].style.marginTop = "35px";
        }
    } else {
        navbar.classList.remove("sticky");
        for (i = 0; i < tc.length; i++) {
            tc[i].style.marginTop = "10px";
        }
    }
}

function clickCopy(uriel) {
  var Url = uriel;
  Url.innerHTML = window.location.href;
  console.log(Url.innerHTML)
  Url.select();
  document.execCommand("copy");
}
function openPage(pageName, color) {
    window.scrollTo(0, 0);
    var i, tabcontent, tablinks, tabbd;
    tabcontent = document.getElementsByClassName("tabcontent");

    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = "grey";
    }

    document.getElementById(pageName).style.display = "contents";

//    elmnt.style.backgroundColor = color;

    tabbd = document.getElementsByTagName("html");
    tabbd[0].style.backgroundColor = color;

}

document.getElementById('show-sidebar').click();
document.getElementById('toggle-button').click();

axios.get('/scrape?url=https://jbzd.pl')
  .then(resp => {
    // 1) sparsuj HTML do Document
    const parser = new DOMParser();
    const doc = parser.parseFromString(resp.data, 'text/html');

    // 2) selektorami DOM wyciągnij, co chcesz:
    const titles = Array.from(doc.querySelectorAll('h2'))
                        .map(h2 => h2.textContent);
    console.log(titles);
  })
  .catch(console.error);