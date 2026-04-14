from time import sleep
import fgrequests
from bsmethods import get_soup_by_url, get_soup_from_response

# Czas oczekiwania między pobieraniem kolejnych podstron (w sekundach)
time_beetween_get_soup = 0.05

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# dziala - poprawione i zabezpieczone na podstawie html
def get_jbzd(limit):
    """
    Scrapes jbzd.com.pl, segregating data:
    - jebmem: dict with [title, image_src, source_url]
    - jebvmem: dict with [title, video_src, source_url]
    """
    tempmem = {}
    tempvid = {}

    # Adres JBZD do budowania pełnych linków
    base_url = "https://jbzd.com.pl"

    # Tworzymy listę URL podstron do skrapowania
    url_list = [f"{base_url}/str/{str(i + 1)}" for i in range(0, limit)]

    # Pobieramy strony asynchronicznie
    page_res = fgrequests.build(url_list, headers=HEADERS)

    # Przetwarzamy odpowiedzi z każdej strony
    for res in page_res:
        # Zabezpieczenie przed błędem pobierania strony
        if not res or res.status_code != 200:
            print(f"Błąd pobierania strony JBZD: {res.url if res else 'Nieznany URL'}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)

        # Kontenery na memy (nowy selektor na podstawie html)
        articles = soup.select('article.article')

        for article in articles:
            try:
                # 1. Zabezpieczenie dla tytułu i linku źródłowego
                title_tag = article.select_one('.article-title h2 a')
                if not title_tag:
                    continue

                title_text = title_tag.text.strip()
                source_url = title_tag.get('href', '')

                # Jeśli brak linku, nie możemy stworzyć ID
                if not source_url:
                    continue
                mem_id = source_url.split('/')[-1]  # Używamy sluga jako ID

                # 2. Szukamy multimediów w kontenerze
                media_container = article.select_one('.article-container')

                # Jeśli brak kontenera z mediami, pomijamy
                if not media_container:
                    continue

                # --- SEKREGRACJA: NAJPIERW OBRAZKI ---

                # Sprawdzamy, czy to obrazek
                img_tag = media_container.select_one('img.article-image')

                if img_tag:
                    src = img_tag.get('src', '')
                    if src and mem_id:
                        tempmem[mem_id] = [title_text, src, source_url]
                        continue  # Przechodzimy do następnego mema, żeby nie sprawdzać wideo

                # --- SEKREGRACJA: POTEM WIDEO ---

                # Jeśli nie obrazek, sprawdzamy wideo
                # Szukamy bezpośrednio źródła mp4 w tagu source
                # W HTML wideo jest w videoplyr, ale dla soupa mp4 jest w source
                source_tag = media_container.select_one('source[type="video/mp4"]')

                if source_tag:
                    src = source_tag.get('src', '')
                    if src and mem_id:
                        tempvid[mem_id] = [title_text, src, source_url]

            except Exception as e:
                # Jeśli błąd przy jednym memie, wypisujemy go i idziemy dalej
                print(f"Błąd przy przetwarzaniu mema na JBZD: {e}")
                pass

    # Łączymy wyniki. Twoja strona statyczna powinna wyświetlić je po kolei.
    temp = {"jebmem": tempmem, "jebvmem": tempvid}
    return temp


# NOWA, POPRAWIONA WERSJA dla Kwejk.pl (Obsługuje obrazki, wideo i trudną paginację)
def get_kwejks(limit):
    """
    Scrapes kwejk.pl, handling images, dynamic videos, and tricky decreasing pagination.
    Output:
    - kwmems: dict with [title, image_src, source_url]
    - kwvmems: dict with [title, video_src, source_url]
    """
    final_images = {}
    final_videos = {}

    base_url = "https://kwejk.pl"
    # Zaczynamy od strony głównej
    current_page_url = base_url
    pages_scraped = 0

    print(f"Zaczynam zbieranie linków z Kwejk.pl. Limit stron: {limit}...")

    # Pętla while jest konieczna, bo nie znamy URLi kolejnych stron z góry
    while pages_scraped < limit and current_page_url:
        print(f"Pobieram stronę Kwejka ({pages_scraped + 1}/{limit}): {current_page_url}")

        # Pobieramy stronę synchronicznie, bo potrzebujemy URL następnej
        soup = get_soup_by_url(current_page_url)

        if not soup:
            print(f"Błąd pobierania strony Kwejk: {current_page_url}")
            break  # Przerywamy pętlę, jeśli nie udało się pobrać strony

        sleep(time_beetween_get_soup)

        # Selektor dla kontenerów memów na podstawie HTML
        mem_boxes = soup.select('.box.fav')

        for box in mem_boxes:
            try:
                # 1. Zabezpieczenie dla tytułu i linku źródłowego
                title_tag = box.select_one('h2 a[dusk="media-title-selector"]')
                if not title_tag:
                    continue

                title_text = title_tag.text.strip()
                source_url = title_tag.get('href', '')

                # Jeśli brak linku, nie możemy stworzyć ID
                if not source_url:
                    continue
                # Używamy członu URL przed .html jako ID (np. 4190759)
                mem_id = source_url.split('/')[-1].replace('.html', '')

                # 2. Szukamy multimediów w kontenerze .figure
                figure_holder = box.select_one('.figure-holder')
                if not figure_holder:
                    continue

                # --- SEKREGRACJA: NAJPIERW WIDEO ---
                # W HTML wideo jest w niestandardowym tagu <player> z atrybutem source
                video_player_tag = figure_holder.select_one('player')

                if video_player_tag:
                    src = video_player_tag.get('source', '')
                    if src and mem_id:
                        final_videos[mem_id] = [title_text, src, source_url]
                        continue  # Przechodzimy do następnego mema, żeby nie sprawdzać obrazka

                # --- SEKREGRACJA: POTEM OBRAZKI ---
                # Standardowy obrazek ma klasę .full-image
                img_tag = figure_holder.select_one('img.full-image')

                if img_tag:
                    src = img_tag.get('src', '')
                    if src and mem_id:
                        final_images[mem_id] = [title_text, src, source_url]

            except Exception as e:
                # Jeśli błąd przy jednym memie, wypisujemy go i idziemy dalej
                print(f"Błąd przy przetwarzaniu mema na Kwejk: {e}")
                pass

        # --- PAGINACJA: Szukamy linku do "Następna strona" ---
        pages_scraped += 1
        current_page_url = None  # Resetujemy, aby przerwać pętlę, jeśli nie znajdziemy przycisku

        # Szukamy kontenera .pagination na samym dole strony
        pagination_container = soup.select_one('.pagination')
        if pagination_container:
            # Szukamy przycisku z klasą .btn-next
            next_page_tag = pagination_container.select_one('a.btn-next')
            if next_page_tag:
                current_page_url = next_page_tag.get('href', '')
                # Kwejk często podaje pełne linki, ale dla pewności sprawdzamy
                if current_page_url and not current_page_url.startswith('http'):
                    current_page_url = f"{base_url}{current_page_url}"

    temp = {'kwmems': final_images, 'kwvmems': final_videos}
    print(
        f"Skrapowanie Kwejk.pl zakończone. Pobrano {len(final_images)} memów obrazkowych i {len(final_videos)} memów wideo ze {pages_scraped} stron.")
    return temp


# NOWA, DZIAŁAJĄCA WERSJA dla Joemonster (Dwuetapowe asynchroniczne pobieranie)
def get_jmonster(limit):
    """
    Scrapes joemonster.org, segregating data:
    - urljm: dict with [title, image_src, source_url]
    - urljvm: dict with [title, video_src, source_url]
    """
    tempmem = {}
    tempvid = {}

    uri = 'https://joemonster.org'
    # Adres JBZD do budowania pełnych linków
    edition = "?edition=104"

    # --- ETAP 1: Zbieranie linków do pojedynczych stron memów ze stron galerii ---

    gallery_url_list = [f"{uri}/mg/lastup/{str(i)}{edition}" for i in range(1, limit + 1)]

    # Lista do przechowywania danych pośrednich: {'title':..., 'url':..., 'mem_id':...}
    individual_pages_data = []

    # Pobieramy strony galerii asynchronicznie
    gallery_res = fgrequests.build(gallery_url_list, headers=HEADERS)

    print(f"Zaczynam zbieranie linków ze stron galerii Joe Monster (limit: {limit})...")

    for res in gallery_res:
        if not res or res.status_code != 200:
            print(f"Błąd pobierania strony galerii Joemonster: {res.url if res else 'Nieznany URL'}: {res}: {res.url}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)

        # Selektor dla kontenerów memów na podstawie HTML
        meme_thumbnails = soup.select('li.mg_thumbnail')

        for thumb in meme_thumbnails:
            try:
                # Szukamy linku do pojedynczej strony
                link_tag = thumb.select_one('a')
                if not link_tag:
                    continue

                partial_url = link_tag.get('href', '')
                if not partial_url:
                    continue

                # Budujemy pełny URL
                individual_url = f"{uri}{partial_url}"

                # Szukamy obrazka, aby wyciągnąć tytuł z alt lub title
                img_tag = link_tag.select_one('img')
                if not img_tag:
                    continue

                # Tytuł może być w alt lub w title
                title = img_tag.get('alt') or img_tag.get('title', 'joemonster_mem')
                title = title.strip()

                # Używamy ostatniego członu URL jako mem_id
                mem_id = partial_url.split('/')[-1]

                if not mem_id:
                    continue

                individual_pages_data.append({
                    'title': title,
                    'url': individual_url,
                    'mem_id': mem_id
                })

            except Exception as e:
                print(f"Błąd przy zbieraniu linku z galerii Joemonster: {e}")
                pass

    # --- ETAP 2: Asynchroniczne pobieranie finalnego SRC z pojedynczych stron memów ---

    print(f"Zebrano {len(individual_pages_data)} linków. Zaczynam asynchroniczne pobieranie finalnych SRC...")

    # Lista URLi do pobrania finalnego SRC
    final_src_url_list = [page_data['url'] for page_data in individual_pages_data]

    # Pobieramy pojedyncze strony memów asynchronicznie (to klucz do wydajności)
    final_res = fgrequests.build(final_src_url_list, headers=HEADERS)

    # Iterujemy po danych pośrednich i odpowiedziach jednocześnie przy użyciu zip
    for page_data, res in zip(individual_pages_data, final_res):
        if not res or res.status_code != 200:
            print(f"Błąd pobierania pojedynczej strony Joemonster: {res.url if res else 'Nieznany URL'}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)

        try:
            # 1. Zabezpieczenie dla finalnego kontenera multimedia
            final_media_container = soup.select_one('.gallery-picture-link')
            if not final_media_container:
                continue

            # 2. Zabezpieczenie dla finalnego obrazka
            final_img = final_media_container.select_one('img')
            if not final_img:
                continue

            final_src = final_img.get('src', '')
            if final_src:
                tempmem[page_data['mem_id']] = [page_data['title'], final_src, page_data['url']]

        except Exception as e:
            print(f"Błąd przy wyciąganiu SRC z pojedynczej strony Joemonster: {e}")
            pass

    # Użytkownik prosił tylko o obrazki, więc zwracamy tempmem
    temp = {'urljm': tempmem, 'urljvm': tempvid}
    print(f"Skrapowanie Joemonster zakończone. Pobrano {len(tempmem)} memów.")
    return temp


# NOWA, POPRAWIONA WERSJA dla Demotywatory.pl (Obsługuje obrazki, wideo i asynchroniczne galerie)
def get_demot(limit):
    """
    Scrapes demotywatory.pl, handling images, videos, and asynchronous multi-meme galleries.
    Output:
    - demomemp: dict with [title, image_src, source_url]
    - demomemv: dict with [title, video_src, source_url]
    """
    final_images = {}
    final_videos = {}

    uri = 'https://demotywatory.pl'
    page_prefix = f"{uri}/page/"

    # --- ETAP 1: Zbieranie linków ze stron głównej i segregacja (obrazek, wideo, galeria) ---

    gallery_page_urls_to_scrape = []  # Lista linków do asynchronicznego pobrania galerii
    gallery_metadata_from_main_page = []  # Metadane (tytuł, mem_id) z głównej strony

    main_page_url_list = [f"{page_prefix}{str(i + 1)}" for i in range(0, limit)]

    print(f"Zaczynam zbieranie linków ze stron głównej Demotywatory.pl (limit: {limit})...")
    req_main_pages = fgrequests.build(main_page_url_list, headers=HEADERS)

    for rp in req_main_pages:
        if not rp or rp.status_code != 200:
            print(f"Błąd pobierania strony głównej Demotywatory: {rp.url if rp else 'Nieznany URL'}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(rp)

        # Selektor dla kontenerów memów na podstawie HTML
        mem_articles = soup.select('article')

        for article in mem_articles:
            try:
                # 1. Sprawdzamy, czy to galeria ("wielomem")
                gallery_tag = article.select_one('span.gallery_pics_count')
                if gallery_tag:
                    # To jest galeria. Musimy wyciągnąć jej link, aby pobrać memy asynchronicznie w Etapie 2.
                    title_tag = article.select_one('h1.demot-header a')
                    if not title_tag:
                        continue

                    gallery_partial_url = title_tag.get('href', '')
                    if not gallery_partial_url:
                        continue

                    gallery_full_url = f"{uri}{gallery_partial_url}"

                    # Używamy ostatniego członu URL jako mem_id
                    mem_id = gallery_partial_url.split('/')[-1]
                    title = title_tag.text.strip()

                    gallery_page_urls_to_scrape.append(gallery_full_url)
                    gallery_metadata_from_main_page.append({'title': title, 'mem_id': mem_id})
                    continue  # To jest galeria, więc nie sprawdzamy dalej dla tego artykułu

                # 2. Sprawdzamy, czy to standardowy obrazek lub wideo w HTML5
                demot_inner_video_wrapper = article.select_one('.demotivator_inner_video_wrapper')
                demot_pic = article.select_one('.demot_pic')

                if demot_inner_video_wrapper:
                    # To jest wideo.
                    source_tag = demot_inner_video_wrapper.select_one('video source[type="video/mp4"]')
                    if not source_tag:
                        continue

                    src = source_tag.get('src', '')
                    title_tag = article.select_one('h2.demot-header a')
                    if not title_tag:
                        continue

                    title = title_tag.text.strip()
                    source_url = f"{uri}{title_tag.get('href', '')}"
                    mem_id = title_tag.get('href', '').split('/')[-1]

                    if src and mem_id:
                        final_videos[mem_id] = [title, src, source_url]
                        continue

                elif demot_pic:
                    # To jest standardowy obrazek.
                    img_tag = demot_pic.select_one('img.demot')
                    if not img_tag:
                        continue

                    src = img_tag.get('src', '')
                    title_tag = article.select_one('h2.demot-header a')
                    if not title_tag:
                        continue

                    title = title_tag.text.strip()
                    source_url = f"{uri}{title_tag.get('href', '')}"
                    mem_id = title_tag.get('href', '').split('/')[-1]

                    if src and mem_id:
                        final_images[mem_id] = [title, src, source_url]
                        continue

            except Exception as e:
                print(f"Błąd przy zbieraniu linku ze strony głównej Demotywatory: {e}")
                pass

    # --- ETAP 2: Asynchroniczne pobieranie finalnych SRC z pojedynczych stron galerii ---

    if gallery_page_urls_to_scrape:
        print(
            f"Zebrano {len(gallery_page_urls_to_scrape)} linków do galerii. Zaczynam asynchroniczne pobieranie finalnych SRC wewnątrz galerii...")

        final_gallery_res = fgrequests.build(gallery_page_urls_to_scrape, headers=HEADERS)

        # Iterujemy po danych pośrednich i odpowiedziach jednocześnie przy użyciu zip
        for gallery_metadata, res in zip(gallery_metadata_from_main_page, final_gallery_res):
            if not res or res.status_code != 200:
                print(f"Błąd pobierania pojedynczej strony galerii Demotywatory: {res.url if res else 'Nieznany URL'}")
                continue

            sleep(time_beetween_get_soup)
            soup = get_soup_from_response(res)

            try:
                # 1. Zabezpieczenie dla finalnego kontenera multimedia
                final_media_container = soup.select_one('.rsSlideContent')
                if not final_media_container:
                    continue

                # 2. Sprawdzamy, czy to wideo w galerii
                final_video_tag = final_media_container.select_one('video')
                final_img_tag = final_media_container.select_one('img')

                if final_video_tag:
                    source_tag = final_video_tag.select_one('source[type="video/mp4"]')
                    if not source_tag:
                        continue
                    final_src = source_tag.get('src', '')
                    if final_src:
                        # Wideo w galerii ląduje w final_videos
                        final_videos[gallery_metadata['mem_id']] = [gallery_metadata['title'], final_src, res.url]

                elif final_img_tag:
                    final_src = final_img_tag.get('src', '')
                    if final_src:
                        # Obrazek w galerii ląduje w final_images
                        final_images[gallery_metadata['mem_id']] = [gallery_metadata['title'], final_src, res.url]

            except Exception as e:
                print(f"Błąd przy wyciąganiu SRC z pojedynczej strony galerii Demotywatory: {e}")
                pass

    temp = {'demomemp': final_images, 'demomemv': final_videos}
    print(
        f"Skrapowanie Demotywatory.pl zakończone. Pobrano {len(final_images)} memów obrazkowych i {len(final_videos)} memów wideo.")
    return temp


def get_redmik(limit):
    """Scrapes redmik.pl for images"""
    tempmem = {}
    url_list = [f"https://redmik.pl/page/{str(i + 1)}" for i in range(0, limit)]
    page_res = fgrequests.build(url_list, headers=HEADERS)

    for res in page_res:
        if not res or res.status_code != 200:
            print(f"Błąd pobierania strony Redmik: {res.url if res else 'Nieznany URL'}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('a', {'class', 'g1-frame'})

        # Pierwsze 4 elementy to często nagłówki/reklamy
        if len(mems) < 4:
            continue

        for i in range(4, len(mems)):
            try:
                mem = mems[i]
                href = mem.get('href', '')
                title = mem.get('title', '').strip()

                # Zabezpieczenie dla obrazka
                img_tag = mem.find('img')
                if not img_tag:
                    continue

                # Obrazek może być w 'data-src' (lazy loading) lub w 'src'
                source = img_tag.get('data-src') or img_tag.get('src', '')

                if not source or not title or not href:
                    continue

                tempmem[title] = [title, source, href]
            except Exception as e:
                print(f"Błąd przy przetwarzaniu mema na Redmik: {e}")
                pass

    temp = {'rmmems': tempmem}
    return temp


# dziala - dodane zabezpieczenia
def get_atomgrab(limit):
    """Scrapes atomowegrabie.pl for images"""
    tempmem = {}
    url_list = [f"https://atomowegrabie.pl/?page={str(i + 1)}" for i in range(0, limit)]
    page_res = fgrequests.build(url_list, headers=HEADERS)

    for res in page_res:
        if not res or res.status_code != 200:
            print(f"Błąd pobierania strony Atomowegrabie: {res.url if res else 'Nieznany URL'}")
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        # Kontener na memy
        mems = soup.find_all('div', {'class', 'article'})

        for mem in mems:
            try:
                # 1. Zabezpieczenie dla tytułu
                header = mem.find('h1')
                if not header or not header.find('a'):
                    continue
                title = header.find('a').text.strip()

                # 2. Zabezpieczenie dla kontenera obrazka
                obj = mem.find('div', {'class', 'object'})
                if not obj or not obj.find('img'):
                    continue

                # 3. Zabezpieczenie dla samego obrazka
                source = obj.find('img').get('src', '')

                if not source:
                    continue

                tempmem[title] = [title, source, res.url]
            except Exception as e:
                print(f"Błąd przy przetwarzaniu mema na Atomowegrabie: {e}")
                pass

    temp = {'agmems': tempmem}
    return temp