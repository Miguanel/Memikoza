from time import sleep
import fgrequests
from bsmethods import get_soup_by_url, get_soup_from_response

time_beetween_get_soup = 0.05

# 1. POPRAWKA: Bardziej wiarygodne nagłówki omijające blokady (np. JoeMonster)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3'
}


def get_jbzd(limit):
    tempmem = {}
    tempvid = {}
    base_url = "https://jbzd.com.pl"
    url_list = [f"{base_url}/str/{str(i + 1)}" for i in range(0, limit)]
    page_res = fgrequests.build(url_list, headers=HEADERS)

    for res in page_res:
        if not res or res.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        articles = soup.select('article.article')

        for article in articles:
            try:
                title_tag = article.select_one('.article-title h2 a')
                if not title_tag:
                    continue

                title_text = title_tag.text.strip()
                source_url = title_tag.get('href', '')
                if not source_url:
                    continue
                mem_id = source_url.split('/')[-1]

                # --- 1. POPRAWKA: WIDEO NA PODSTAWIE ZRZUTU EKRANU ---
                src = ''
                # Szukamy znacznika 'source' wewnątrz 'video', które jest w '.video-player'
                source_tag = article.select_one('.video-player video source')

                if source_tag:
                    src = source_tag.get('src', '')
                else:
                    # Fallback na wypadek gdyby src był umieszczony bezpośrednio w tagu video
                    video_tag = article.select_one('.video-player video')
                    if video_tag:
                        src = video_tag.get('src', '')

                if not src:
                    src = article.find("videoplyr")
                    if not src:
                        src = article.find(attrs={"class": "vue-plyr"})
                    if not src:
                        src = article.find(attrs={"type": "video/mp4"})
                    if src:
                        src = src.attrs['video_url']
                        tempvid[mem_id] = [title_text, src, source_url]

                if src and mem_id:
                    tempvid[mem_id] = [title_text, src, source_url]
                    continue  # <--- Przechodzimy dalej TYLKO jeśli to wideo

                # --- 2. JEŚLI NIE MA WIDEO, SPRAWDZAMY OBRAZEK ---
                # Twój zrzut pokazuje, że głównym kontenerem jest <div class="article-image">
                # Szukamy obrazka, odrzucając ikonkę ograniczenia wiekowego (+18),
                # która ma klasę "video-player-badge"
                img_tag = article.select_one('.article-image img:not(.video-player-badge)')

                # Dodatkowe zabezpieczenie na wypadek starej struktury JBZD
                if not img_tag:
                    img_tag = article.select_one('img.article-image')

                if img_tag:
                    src = img_tag.get('src', '')
                    if src and mem_id:
                        tempmem[mem_id] = [title_text, src, source_url]

            except Exception as e:
                print(f"Błąd JBZD przy memie {mem_id if 'mem_id' in locals() else 'nieznanym'}: {e}")

    temp = {"jebmem": tempmem, "jebvmem": tempvid}
    print(f"Pobrano JBZD: {len(tempmem)} img, {len(tempvid)} vid")
    return temp

def get_jzd(limit):
    """8 memes per page"""
    tempmem = {}
    tempvid = {}
    url_list = ['https://jbzd.com.pl/str/' + str(i + 1) for i in range(0, limit)]
    page_res = fgrequests.build(url_list)
    for res in page_res:
        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('div', {'class', 'article-content'})
        for mem in mems:
            try:
                tyt = mem.select_one('h3.article-title').a
                url = tyt['href']
                tyt = tyt.text.replace('\n', '').replace('  ', '')
                art_cont = mem.select_one('.article-container')
                mem_id = url.split('/')[-2]
                if art_cont:
                    artimg_src = art_cont.select_one("img[src]")
                    if artimg_src:
                        src = artimg_src["src"]
                        tempmem[mem_id] = [tyt, src, url]
                else:
                    src = mem.find("videoplyr")
                    if not src:
                        src = mem.find(attrs={"class": "vue-plyr"})
                    if not src:
                        src = mem.find(attrs={"type": "video/mp4"})
                    if src:
                        src = src.attrs['video_url']
                        tempvid[mem_id] = [tyt, src, url]
            except Exception as e:
                print(e)

    temp = {"jebmem": tempmem, "jebvmem": tempvid}
    print(f"Pobrano JBZD: {len(tempmem)} img, {len(tempvid)} vid")
    return temp

def get_kwejks(limit):
    # (Kwejk działał poprawnie, pozostawiony bez zmian logicznych, używa nowych nagłówków)
    final_images = {}
    final_videos = {}
    base_url = "https://kwejk.pl"
    current_page_url = base_url
    pages_scraped = 0

    while pages_scraped < limit and current_page_url:
        soup = get_soup_by_url(current_page_url)
        if not soup:
            break

        sleep(time_beetween_get_soup)
        mem_boxes = soup.select('.box.fav')

        for box in mem_boxes:
            try:
                title_tag = box.select_one('h2 a[dusk="media-title-selector"]')
                if not title_tag:
                    continue

                title_text = title_tag.text.strip()
                source_url = title_tag.get('href', '')
                if not source_url:
                    continue
                mem_id = source_url.split('/')[-1].replace('.html', '')

                figure_holder = box.select_one('.figure-holder')
                if not figure_holder:
                    continue

                video_player_tag = figure_holder.select_one('player')
                if video_player_tag:
                    src = video_player_tag.get('source', '')
                    if src and mem_id:
                        final_videos[mem_id] = [title_text, src, source_url]
                        continue

                img_tag = figure_holder.select_one('img.full-image')
                if img_tag:
                    src = img_tag.get('src', '')
                    if src and mem_id:
                        final_images[mem_id] = [title_text, src, source_url]

            except Exception:
                pass

        pages_scraped += 1
        current_page_url = None
        pagination_container = soup.select_one('.pagination')
        if pagination_container:
            next_page_tag = pagination_container.select_one('a.btn-next')
            if next_page_tag:
                current_page_url = next_page_tag.get('href', '')
                if current_page_url and not current_page_url.startswith('http'):
                    current_page_url = f"{base_url}{current_page_url}"

    temp = {'kwmems': final_images, 'kwvmems': final_videos}
    print(f"Pobrano KWEJK: {len(final_images)} img, {len(final_videos)} vid")
    return temp


def get_jmonster(limit):
    tempmem = {}
    tempvid = {}
    uri = 'https://joemonster.org'
    edition = "?edition=104"

    gallery_url_list = [f"{uri}/mg/lastup/{str(i)}{edition}" for i in range(1, limit + 1)]
    individual_pages_data = []
    gallery_res = fgrequests.build(gallery_url_list, headers=HEADERS)

    for res in gallery_res:
        if not res or res.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)

        # JoeMonster bardzo często zmienia nazwy klas w galerii.
        # Rozszerzamy wyszukiwanie o alternatywne kontenery
        meme_thumbnails = soup.select('li.mg_thumbnail, div.photo-box')

        for thumb in meme_thumbnails:
            try:
                link_tag = thumb.select_one('a')
                if not link_tag:
                    continue

                partial_url = link_tag.get('href', '')
                if not partial_url:
                    continue

                individual_url = f"{uri}{partial_url}"
                img_tag = link_tag.select_one('img')
                if not img_tag:
                    continue

                title = img_tag.get('alt') or img_tag.get('title', 'joemonster_mem')
                title = title.strip()
                mem_id = partial_url.split('/')[-1]

                if not mem_id:
                    continue

                individual_pages_data.append({
                    'title': title,
                    'url': individual_url,
                    'mem_id': mem_id
                })

            except Exception:
                pass

    final_src_url_list = [page_data['url'] for page_data in individual_pages_data]
    final_res = fgrequests.build(final_src_url_list, headers=HEADERS)

    for page_data, res in zip(individual_pages_data, final_res):
        if not res or res.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)

        try:
            final_media_container = soup.select_one('.gallery-picture-link, .photo-content')
            if not final_media_container:
                continue

            final_img = final_media_container.select_one('img')
            if not final_img:
                continue

            final_src = final_img.get('src', '')
            if final_src:
                tempmem[page_data['mem_id']] = [page_data['title'], final_src, page_data['url']]

        except Exception:
            pass

    temp = {'urljm': tempmem, 'urljvm': tempvid}
    print(f"Pobrano JM: {len(tempmem)} img, {len(tempvid)} vid")  # Zostawiam print do logów w Renderze!
    return temp


def get_demot(limit):
    final_images = {}
    final_videos = {}
    uri = 'https://demotywatory.pl'
    page_prefix = f"{uri}/page/"

    gallery_page_urls_to_scrape = []
    gallery_metadata_from_main_page = []
    main_page_url_list = [f"{page_prefix}{str(i + 1)}" for i in range(0, limit)]

    req_main_pages = fgrequests.build(main_page_url_list, headers=HEADERS)

    for rp in req_main_pages:
        if not rp or rp.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(rp)

        # 3. POPRAWKA DEMOTYWATORY: Szukamy po uniwersalnej klasie, a nie tagu <article>
        mem_articles = soup.select('.demotivator')

        for article in mem_articles:
            try:
                gallery_tag = article.select_one('span.gallery_pics_count')
                if gallery_tag:
                    title_tag = article.select_one('h1.demot-header a, h2.demot-header a')
                    if not title_tag:
                        continue

                    gallery_partial_url = title_tag.get('href', '')
                    if not gallery_partial_url:
                        continue

                    gallery_full_url = f"{uri}{gallery_partial_url}"
                    mem_id = gallery_partial_url.split('/')[-1]
                    title = title_tag.text.strip()

                    gallery_page_urls_to_scrape.append(gallery_full_url)
                    gallery_metadata_from_main_page.append({'title': title, 'mem_id': mem_id})
                    continue

                demot_inner_video_wrapper = article.select_one('.demotivator_inner_video_wrapper')
                demot_pic = article.select_one('.demot_pic')

                if demot_inner_video_wrapper:
                    source_tag = demot_inner_video_wrapper.select_one('video source')
                    if not source_tag:
                        continue

                    src = source_tag.get('src', '')
                    title_tag = article.select_one('h2.demot-header a, h1.demot-header a')
                    if not title_tag:
                        continue

                    title = title_tag.text.strip()
                    source_url = f"{uri}{title_tag.get('href', '')}"
                    mem_id = title_tag.get('href', '').split('/')[-1]

                    if src and mem_id:
                        final_videos[mem_id] = [title, src, source_url]
                        continue

                elif demot_pic:
                    img_tag = demot_pic.select_one('img.demot')
                    if not img_tag:
                        continue

                    src = img_tag.get('src', '')
                    title_tag = article.select_one('h2.demot-header a, h1.demot-header a')
                    if not title_tag:
                        continue

                    title = title_tag.text.strip()
                    source_url = f"{uri}{title_tag.get('href', '')}"
                    mem_id = title_tag.get('href', '').split('/')[-1]

                    if src and mem_id:
                        final_images[mem_id] = [title, src, source_url]
                        continue

            except Exception:
                pass

    if gallery_page_urls_to_scrape:
        final_gallery_res = fgrequests.build(gallery_page_urls_to_scrape, headers=HEADERS)

        for gallery_metadata, res in zip(gallery_metadata_from_main_page, final_gallery_res):
            if not res or res.status_code != 200:
                continue

            sleep(time_beetween_get_soup)
            soup = get_soup_from_response(res)

            try:
                final_media_container = soup.select_one('.rsSlideContent')
                if not final_media_container:
                    continue

                final_video_tag = final_media_container.select_one('video')
                final_img_tag = final_media_container.select_one('img')

                if final_video_tag:
                    source_tag = final_video_tag.select_one('source')
                    if not source_tag:
                        continue
                    final_src = source_tag.get('src', '')
                    if final_src:
                        final_videos[gallery_metadata['mem_id']] = [gallery_metadata['title'], final_src, res.url]

                elif final_img_tag:
                    final_src = final_img_tag.get('src', '')
                    if final_src:
                        final_images[gallery_metadata['mem_id']] = [gallery_metadata['title'], final_src, res.url]

            except Exception:
                pass

    temp = {'demomemp': final_images, 'demomemv': final_videos}
    print(f"Pobrano DEMOTY: {len(final_images)} img, {len(final_videos)} vid")  # Zostawiam print do logów
    return temp


def get_redmik(limit):
    tempmem = {}
    url_list = [f"https://redmik.pl/page/{str(i + 1)}" for i in range(0, limit)]
    page_res = fgrequests.build(url_list, headers=HEADERS)

    for res in page_res:
        if not res or res.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('a', {'class', 'g1-frame'})

        if len(mems) < 4:
            continue

        for i in range(4, len(mems)):
            try:
                mem = mems[i]
                href = mem.get('href', '')
                title = mem.get('title', '').strip()

                img_tag = mem.find('img')
                if not img_tag:
                    continue

                source = img_tag.get('data-src') or img_tag.get('src', '')
                if not source or not title or not href:
                    continue

                tempmem[title] = [title, source, href]
            except Exception:
                pass

    temp = {'rmmems': tempmem}
    print(f"Pobrano REDMIK: {len(tempmem)}")
    return temp


def get_atomgrab(limit):
    tempmem = {}
    url_list = [f"https://atomowegrabie.pl/?page={str(i + 1)}" for i in range(0, limit)]
    page_res = fgrequests.build(url_list, headers=HEADERS)

    for res in page_res:
        if not res or res.status_code != 200:
            continue

        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('div', {'class', 'article'})

        for mem in mems:
            try:
                header = mem.find('h1')
                if not header or not header.find('a'):
                    continue
                title = header.find('a').text.strip()

                obj = mem.find('div', {'class', 'object'})
                if not obj or not obj.find('img'):
                    continue

                source = obj.find('img').get('src', '')
                if not source:
                    continue

                tempmem[title] = [title, source, res.url]
            except Exception:
                pass

    temp = {'agmems': tempmem}
    return temp