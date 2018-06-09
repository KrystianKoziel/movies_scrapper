import bs4 as bs

from urllib import request

import mongo_config


COLLECTION = "movies"


def get_source(url: str) -> str:
    source = request.urlopen(url)
    soup = bs.BeautifulSoup(source, 'lxml')
    return soup


def get_movies_sites() -> list:
    # most popular films from
    film_sites = []
    urls = ['https://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm_8',
            'https://www.imdb.com/chart/top?ref_=nv_mv_250_6',
            'https://www.imdb.com/chart/boxoffice?ref_=nv_ch_cht_1']
    for url in urls:
        soup = get_source(url)
        table = soup.find('table', attrs={'class': 'chart full-width'})
        for link in table.findAll('a'):
            pure_link = link.get('href')
            pure_link = 'https://www.imdb.com' + pure_link
            if pure_link not in film_sites:
                film_sites.append(pure_link)
    return film_sites


def get_genres(soup: bs.BeautifulSoup) -> list:
    genres_div = soup.find('div', attrs={'itemprop': 'genre'})
    genres_links = genres_div.findAll('a')
    return [genre.text for genre in genres_links]


def get_name(soup: bs.BeautifulSoup) -> str:
    name_el = soup.find('div', attrs={'class': 'originalTitle'})
    if name_el is None:
        name_el = soup.find('h1', attrs={'itemprop': 'name'})
    return name_el.text


def get_box_office(soup: bs.BeautifulSoup) -> str:
    sibling = soup.find('h4', text='Cumulative Worldwide Gross:')
    if sibling is None:
        return 0
    return ''.join([i for i in sibling.next_sibling if i.isdigit()])


def get_as_dict(name, genres, year, country, box_office):
    informations = dict()
    informations['title'] = name
    informations['genres'] = genres
    informations['year'] = year
    informations['country'] = country
    informations['box_office'] = box_office
    return informations


def get_data():
    urls = get_movies_sites()
    for url in urls:
        soup = get_source(url)
        name = get_name(soup)
        genres = get_genres(soup)
        year = soup.find('span', attrs={'id': 'titleYear'}).find('a').text
        country = soup.find('h4', text='Country:').next_sibling.next_sibling.text
        box_office = get_box_office(soup)
        if box_office != 0:
            informations = get_as_dict(name, genres, year, country, box_office)
            mongo_config.save_in_mongo(informations, COLLECTION)


if __name__ == '__main__':
    get_data()
