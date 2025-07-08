from time import sleep
import fgrequests
from bsmethods import get_soup_by_url, get_soup_from_response

time_beetween_get_soup = 0.05


# dziala
def get_jbzd(limit):
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
    temp = {"jebmem": tempmem, "jebvmem": tempvid}
    return temp


# dziala
def get_kwejks(limit):
    """16 memes per page"""
    mems = {}
    u = "https://kwejk.pl"
    s = get_soup_by_url(f"{u}")
    fp = s.find_all(name='a', attrs={"href": u})[-1].text
    f = int(fp)
    url_list = [f"{u}/strona/{f - p}" for p in range(0, limit)]
    page_res = fgrequests.build(url_list)
    for pr in page_res:
        sleep(time_beetween_get_soup)
        sp = get_soup_from_response(pr)
        mm = sp.select('.box.fav')
        if mm:
            for m in mm:
                t = m.select_one('a[dusk="media-title-selector"]')
                if t:

                    src = ""
                    try:
                        title = t.text.replace('\n', '').replace('  ', '')
                        url = t["href"]
                        mem_id = url.split('/')[-2]
                        s = m.select_one('img[src][alt].full-image')
                        if not s:
                            s = m.select_one('.vjs-tech')
                        if s:
                            src = s["src"]
                        if src is None or '':
                            continue
                        mems[mem_id] = [title, src, url]
                    except Exception as e:
                        print('get_kwejks', e)

    temp = {"kwmems": mems}
    return temp


# juz nie dziala
def get_jmonster(limit):
    """18 memes per page"""
    lis = {}
    uri = 'https://joemonster.org'
    url_list = [uri + '/mg/lastup/list/' + str(i) for i in range(1, limit)]
    page_res = fgrequests.build(url_list)
    for pr in page_res:
        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(pr)
        mems = soup.find_all('a', attrs={"class": "gallery-picture-link"})
        for mem in mems:
            href = mem['href']
            mem_id = href.split('/')[-3]
            tyt = href.split('/')[-1]
            tyt = tyt.replace('_', ' ')
            url = uri + href
            src = mem.img['src']
            lis[mem_id] = [tyt, src, url]

    temp = {'urljm': lis}
    return temp


# dziala
def get_demot(limit):
    """18 memes per page"""
    lisp, lisv = {}, {}
    page = "https://demotywatory.pl"
    page_prefix = page + '/page/'

    url_list = [page_prefix + str(i + 1) for i in range(0, limit)]
    req_pages = fgrequests.build(url_list)

    for rp in req_pages:
        sleep(time_beetween_get_soup)
        page_soup = get_soup_from_response(rp)
        if '200' not in str(rp):
            print('200 not in request')

        # mems = page_soup.find_all("a", attrs={"class": "picwrapper"})
        # print('dmt picture in the page', len(mems))
        mems_vid = page_soup.find_all("div", attrs={"class": "demotivator_inner_video_wrapper"})
        mems_pic = page_soup.find_all("div", attrs={"class": "demot_pic"})

        for mem in mems_vid:
            source = mem.find('source').get('src')
            title = source.split('/')[-1].split('.')[0]
            lisv[title] = [title, source, rp.url]

        for mem in mems_pic:
            source = mem.find('img').get('src')
            title = source.split('/')[-1].split('.')[0]
            lisp[title] = [title, source, rp.url]

    temp = {'demomemp': lisp, 'demomemv': lisv}

    return temp


def get_redmik(limit):
    tempmem = {}
    url_list = ['https://redmik.pl/page/' + str(i + 1) for i in range(0, limit)]
    page_res = fgrequests.build(url_list)
    for res in page_res:  # by page
        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('a', {'class', 'g1-frame'})
        for i in range(4, len(mems)):
            mem = mems[i]
            href = mem.get('href')
            title = mem.get('title')
            source = mem.find('img').get('data-src')
            tempmem[title] = [title, source, href]
    # print(len(tempmem))
    temp = {'rmmems': tempmem}
    return temp


# dziala
def get_atomgrab(limit):
    tempmem = {}
    url_list = ['https://atomowegrabie.pl/?page=' + str(i + 1) for i in range(0, limit)]
    page_res = fgrequests.build(url_list)
    for res in page_res:  # by page
        sleep(time_beetween_get_soup)
        soup = get_soup_from_response(res)
        mems = soup.find_all('div', {'class', 'article'})
        for mem in mems:
            title = mem.find('h1').find('a').text
            source = mem.find('div', {'class', 'object'}).find('img').get('src')
            tempmem[title] = [title, source, res.url]
    # print(len(tempmem))
    temp = {'agmems': tempmem}
    return temp
