# -*- coding: utf-8 -*-

'''
    Filmsarok.hu Add-on
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import urllib.parse
import resolveurl as urlresolver
from resources.lib.modules.utils import py2_decode, py2_encode
from datetime import datetime
import html

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')
base_log_info = f'filmsarok.hu | v{version} | Kodi: {kodi_version[:5]}'

xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://www.filmsarok.hu'

headers = {
    'Referer': 'https://www.filmsarok.hu/',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))

    def root(self):
        self.addDirectoryItem("Filmek", f"items&url=https://www.filmsarok.hu/filmek/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozatok", f"items&url=https://www.filmsarok.hu/tvsorozatok/", '', 'DefaultFolder.png')
        self.addDirectoryItem("Kategóriák", "categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Megjelenés éve", "num_categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "newsearch", '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategories(self):

        categories = {
            "Action & Adventure": "https://www.filmsarok.hu/filmkategoria/action-adventure/",
            "Akció": "https://www.filmsarok.hu/filmkategoria/akcio/",
            "Animációs": "https://www.filmsarok.hu/filmkategoria/animacios/",
            "Bűnügyi": "https://www.filmsarok.hu/filmkategoria/bunugyi/",
            "Családi": "https://www.filmsarok.hu/filmkategoria/csaladi/",
            "Dokumentum": "https://www.filmsarok.hu/filmkategoria/dokumentum/",
            "Dráma": "https://www.filmsarok.hu/filmkategoria/drama/",
            "Fantasy": "https://www.filmsarok.hu/filmkategoria/fantasy/",
            "Háborús": "https://www.filmsarok.hu/filmkategoria/haborus/",
            "Horror": "https://www.filmsarok.hu/filmkategoria/horror/",
            "Kaland": "https://www.filmsarok.hu/filmkategoria/kaland/",
            "Rejtély": "https://www.filmsarok.hu/filmkategoria/rejtely/",
            "Romantikus": "https://www.filmsarok.hu/filmkategoria/romantikus/",
            "Sci-Fi": "https://www.filmsarok.hu/filmkategoria/sci-fi/",
            "Sci-Fi & Fantasy": "https://www.filmsarok.hu/filmkategoria/sci-fi-fantasy/",
            "Thriller": "https://www.filmsarok.hu/filmkategoria/thriller/",
            "Történelmi": "https://www.filmsarok.hu/filmkategoria/tortenelmi/",
            "TV film": "https://www.filmsarok.hu/filmkategoria/tv-film/",
            "Vígjáték": "https://www.filmsarok.hu/filmkategoria/vigjatek/",
            "War & Politics": "https://www.filmsarok.hu/filmkategoria/war-politics/",
            "Western": "https://www.filmsarok.hu/filmkategoria/western/",
            "Zenei": "https://www.filmsarok.hu/filmkategoria/zenei/"
        }

        for category, cat_link in categories.items():
            self.addDirectoryItem(f"{category}", f'items&url={quote_plus(cat_link)}', '', 'DefaultFolder.png')
        
        self.endDirectory()

    def getNumCategories(self):

        start_year = 2001
        current_year = datetime.now().year

        for year in range(current_year, start_year - 1, -1):
        
            year_link = f'{base_url}/megjelenes/{year}/'
            self.addDirectoryItem(f"{year}", f'items&url={quote_plus(year_link)}', '', 'DefaultFolder.png')
        
        self.endDirectory()

    def getItems(self, url, title, image_link, link_type, rating, date):
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')

        archive_content = soup.find('div', id='archive-content')
        if not archive_content:
            archive_content = soup.find('div', class_='items full')

        all_articles = []

        if re.findall(r'tvsorozatok', str(archive_content)):
            raw_type = 'tvshows'
            articles = archive_content.find_all('article', class_=f'item {raw_type}')
            for article in articles:
                title = article.find('h3').text.strip()
                image_link_part1 = article.find('img')['src']
                image_link = re.findall(r'(http.*)-', str(image_link_part1))[0].strip()
                image_link = f'{image_link}.jpg'
                
                link = article.find('a')['href']
                if re.findall(r'tvsorozatok', str(link)):
                    link_form = re.findall(r'tvsorozatok', str(link))[0].strip()
                    link_type = 'Sorozat'
                elif re.findall(r'filmek', str(link)):
                    link_form = re.findall(r'filmek', str(link))[0].strip()
                    link_type = 'Film'
                
                rating_text = article.find('div', class_='rating').text.strip()
                try:
                    rating = float(rating_text) if rating_text != 'N/A' else None
                except ValueError:
                    rating = None
        
                date = article.find('span').text.strip()
                if date:
                    date = f'- {date}'

                all_articles.append({
                    'title': title,
                    'image_link': image_link,
                    'link': link,
                    'link_type': link_type,
                    'rating': rating,
                    'date': date,
                    'raw_type': raw_type
                })

        if re.findall(r'filmek', str(archive_content)):
            raw_type = 'movies'
            articles = archive_content.find_all('article', class_=f'item {raw_type}')
            for article in articles:
                title = article.find('h3').text.strip()
                image_link_part1 = article.find('img')['src']
                image_link = re.findall(r'(http.*)-', str(image_link_part1))[0].strip()
                image_link = f'{image_link}.jpg'
                
                link = article.find('a')['href']
                if re.findall(r'tvsorozatok', str(link)):
                    link_form = re.findall(r'tvsorozatok', str(link))[0].strip()
                    link_type = 'Sorozat'
                elif re.findall(r'filmek', str(link)):
                    link_form = re.findall(r'filmek', str(link))[0].strip()
                    link_type = 'Film'
                
                rating_text = article.find('div', class_='rating').text.strip()
                try:
                    rating = float(rating_text) if rating_text != 'N/A' else None
                except ValueError:
                    rating = None
        
                date = article.find('span').text.strip()
                if date:
                    date = f'- {date}'

                all_articles.append({
                    'title': title,
                    'image_link': image_link,
                    'link': link,
                    'link_type': link_type,
                    'rating': rating,
                    'date': date,
                    'raw_type': raw_type
                })

        for article in all_articles:
            if article['link_type'] == 'Film':
                self.addDirectoryItem(
                    f'[B]{article["title"]} - ({article["rating"]}) {article["date"]}[/B]',
                    f'get_movie&url={article["link"]}&title={article["title"]}&image_link={article["image_link"]}&link_type={article["link_type"]}&rating={article["rating"]}&date={article["date"]}',
                    article['image_link'],
                    'DefaultMovies.png',
                    isFolder=True,
                    meta={'title': f'{article["title"]}\n{article["rating"]}'}
                )
            else:
                self.addDirectoryItem(
                    f'[B]{article["title"]} - ({article["rating"]}) {article["date"]}[/B]',
                    f'get_series&url={article["link"]}&title={article["title"]}&image_link={article["image_link"]}&link_type={article["link_type"]}&rating={article["rating"]}&date={article["date"]}',
                    article['image_link'],
                    'DefaultMovies.png',
                    isFolder=True,
                    meta={'title': f'{article["title"]}\n{article["rating"]}'}
                )
        
        try:
            pagination = soup.find('div', class_='pagination')
            if pagination:
                next_page_url = None

                arrow_pag_links = pagination.find_all('a', class_='arrow_pag')
                for link_x in arrow_pag_links:
                    if 'nextpagination' in link_x.find('i')['id']:
                        next_page_url = link_x['href']
                        break

                if not next_page_url:
                    current_span = pagination.find('span', class_='current')
                    if current_span:
                        next_page = int(current_span.text) + 1
                        next_page_link = pagination.find('a', text=str(next_page))
                        if next_page_link:
                            next_page_url = next_page_link['href']

                if not next_page_url:
                    current_span = pagination.find('span', class_='current')
                    if current_span:
                        next_page = int(current_span.text) + 1
                        next_page_link = pagination.find('a', text=str(next_page))
                        if next_page_link:
                            next_page_url = next_page_link['href']
        
                if next_page_url:
                    self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
        except (AttributeError, requests.exceptions.ConnectionError):
            xbmc.log(f'{base_log_info}| getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')


    def getMovieInfo(self, url, title, image_link, link_type, rating, date, description):
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')        
        
        info_div = soup.find(id="info")
        description = info_div.find("div", class_="wp-content").text.strip()
        
        first_table = soup.find('div', {'id': 'videos', 'class': 'sbox'}).find('table')
        
        for idx, row in enumerate(first_table.find('tbody').find_all('tr'), start=1):
            link = row.find('a')['href']
            try:
                quality = row.find('strong', class_='quality').text
                language = row.find_all('td')[2].text
                prov_img = row.find('img')['src']
                provider = re.findall(r'domain=(.*)', str(prov_img))[0].strip()
                
                self.addDirectoryItem(f'{idx:02d} - [B]{provider} - {quality} - {language} - {title}[/B]', f'extr_movie&url={link}&title={title}&image_link={image_link}&link_type={link_type}&rating={rating}&date={date}&description={description}', image_link, 'DefaultMovies.png', isFolder=True, meta={'title': f'{title}\n{rating}', 'plot': description})
            except AttributeError:
                continue
        
        self.endDirectory('movies')

    def extrMovie(self, url, title, image_link, link_type, rating, date, description):

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        
        vid_link = re.findall(r'class=\"btn\" href=\"(.*?)\" id=\"link\"', str(soup))[0].strip()
        
        self.addDirectoryItem(f'[B]{title}[/B]', f'play_movie&url={quote_plus(vid_link)}&title={title}&image_link={image_link}&link_type={link_type}&rating={rating}&date={date}&description={description}', image_link, 'DefaultMovies.png', isFolder=False, meta={'title': f'{title}\n{rating}', 'plot': description})

        self.endDirectory('movies')


    def getSeries(self, url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num):

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')        
        
        info_div = soup.find(id="info")
        description = info_div.find("div", class_="wp-content").text.strip()
        
        episodes_div = soup.find('div', id='episodes')
        seasons = episodes_div.find_all('div', class_='se-c')
        
        for season in seasons:
            season_num = season.find('span', class_='title').text.strip()
            season_num = int(re.findall(r'(\d+).*', str(season_num))[0].strip())
            
            episodes = season.find_all('li')
        
            for episode in episodes:
                episode_link = episode.find('a')['href']
                episode_title = episode.find('a').text.strip()
                episode_image = episode.find('img')['src']
                
                episode_num = episode.find('div', class_='numerando').text.strip()
                episode_num = int(re.findall(r'- (\d+)', str(episode_num))[0].strip())
                
                self.addDirectoryItem(f'[B]{title} - S{season_num:02d}E{episode_num:02d} - {episode_title}[/B]', f'extract_series_part1&url={quote_plus(episode_link)}&title={title}&image_link={image_link}&link_type={link_type}&rating={rating}&date={date}&description={description}&season_num={season_num}&episode_title={episode_title}&episode_image={episode_image}&episode_num={episode_num}', episode_image, 'DefaultMovies.png', isFolder=True, meta={'title': f'{title}\n{rating}', 'plot': description})

        self.endDirectory('movies')

    def extractSeriesPart1(self, url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num):

        season_num = int(season_num)
        episode_num = int(episode_num)

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')        
        
        info_div = soup.find(id="info")
        
        first_table = soup.find('div', {'id': 'videos', 'class': 'sbox'}).find('table')
        
        for idx, row in enumerate(first_table.find('tbody').find_all('tr'), start=1):
            link_x = row.find('a')['href']
            quality = row.find('strong', class_='quality').text
            language = row.find_all('td')[2].text
            prov_img = row.find('img')['src']
            provider = re.findall(r'domain=(.*)', str(prov_img))[0].strip()
            
            self.addDirectoryItem(f'{idx:02d} - [B]{provider} - {quality} - {language} - S{season_num:02d}E{episode_num:02d}[/B]', f'extract_series_part2&url={link_x}&title={title}&image_link={image_link}&link_type={link_type}&rating={rating}&date={date}&description={description}&season_num={season_num}&episode_title={episode_title}&episode_image={episode_image}&episode_num={episode_num}', image_link, 'DefaultMovies.png', isFolder=True, meta={'title': f'{title}\n{rating}', 'plot': description})

        self.endDirectory('movies')

    def extractSeriesPart2(self, url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num):
        
        season_num = int(season_num)
        episode_num = int(episode_num)        

        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')  
        
        vid_link = re.findall(r'class=\"btn\" href=\"(.*?)\" id=\"link\"', str(soup))[0].strip()
        
        self.addDirectoryItem(f'[B]{title} - S{season_num:02d}E{episode_num:02d} - {episode_title}[/B]', f'play_movie&url={quote_plus(vid_link)}&title={title}&image_link={image_link}&link_type={link_type}&rating={rating}&date={date}&description={description}', episode_image, 'DefaultMovies.png', isFolder=False, meta={'title': f'{title} - S{season_num:02d}E{episode_num:02d} - {episode_title}\n{rating}', 'plot': description})        
        
        self.endDirectory('movies')

    def playMovie(self, url):
        xbmc.log(f'{base_log_info}| playMovie | url | {url}', xbmc.LOGINFO)
        try:
            direct_url = urlresolver.resolve(url)
            
            xbmc.log(f'{base_log_info}| playMovie | direct_url: {direct_url}', xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)
        except:
            xbmc.log(f'{base_log_info}| playMovie | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("filmsarok.hu", "Törölt tartalom", time=5000)

    def doSearch(self):
        search_text = self.getSearchText()
        encoded_search = urllib.parse.quote(search_text)

        response = requests.get(f'https://www.filmsarok.hu/?s={encoded_search}', headers=headers)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_page = soup.find('div', class_='search-page')
        
        if search_page:
            result_items = soup.find_all('div', class_='result-item')

            for item in result_items:
                title = item.find('div', class_='title').get_text(strip=True)
                description = item.find('div', class_='contenido').get_text(strip=True)
                link_type = item.find('span', class_='tvshows') or item.find('span', class_='movies')
                link_type = link_type.get_text(strip=True) if link_type else 'unknown'
                
                url = item.find('div', class_='thumbnail').a['href']
                image_link_part1 = item.find('div', class_='thumbnail').img['src']
                image_link = re.findall(r'(http.*)-', str(image_link_part1))[0].strip()
                image_link = f'{image_link}.jpg'
                
                rating_element = item.find('span', class_='rating')
                if rating_element:
                    rating = rating_element.get_text(strip=True).replace('IMDb ', '')
                else:
                    rating = 'N/A'

                date_element = item.find('span', class_='year')
                if date_element:
                    date = date_element.get_text(strip=True)
                    if date:
                        date = f'- {date}'
                
                if link_type == 'Movie':
                    self.addDirectoryItem(f'|   Film   | {title} - ({rating}) {date}', f'get_movie&url={url}&title={title}&image_link={image_link}&rating={rating}&date={date}&description={description}', image_link, 'DefaultFolder.png', meta={'title': f'{title}\n{rating}', 'plot': description})
                elif link_type == 'TV':
                    self.addDirectoryItem(f'|Sorozat| {title} - ({rating}) {date}', f'get_series&url={url}&title={title}&image_link={image_link}&rating={rating}&date={date}&description={description}', image_link, 'DefaultFolder.png', meta={'title': f'{title}\n{rating}', 'plot': description})
        
        # try:
            # pagination_div = soup.find('div', class_='pagination')
            # if pagination_div:
                # current_page_span = pagination_div.find('span', class_='current')
                # if current_page_span:
                    # current_page = int(current_page_span.text.strip())

                    # next_page_number = current_page + 1
                    # next_page_link = pagination_div.find('a', text=str(next_page_number))
                    # if next_page_link:
                        # next_page_url = next_page_link['href']
                        
                        # self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')                        
        # except (AttributeError, requests.exceptions.ConnectionError):
            # xbmc.log(f'{base_log_info}| getItems | next_page_url | csak egy oldal található', xbmc.LOGINFO)

        self.endDirectory('movies')
    
    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)