# -*- coding: utf-8 -*-

'''
    Filmsarok.hu Add-on
    Copyright (C) 2020 heg, vargalex

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')

##

title = params.get('title')
image_link = params.get('image_link')
link_type = params.get('link_type')
rating = params.get('rating')
date = params.get('date')
description = params.get('description')
vid_link = params.get('vid_link')
season_num = params.get('season_num')
episode_title = params.get('episode_title')
episode_image = params.get('episode_image')
episode_num = params.get('episode_num')


if action is None:
    navigator.navigator().root()

elif action == 'categories':
    navigator.navigator().getCategories()

elif action == 'num_categories':
    navigator.navigator().getNumCategories()



elif action == 'items':
    navigator.navigator().getItems(url, title, image_link, link_type, rating, date)

##
elif action == 'get_movie':
    navigator.navigator().getMovieInfo(url, title, image_link, link_type, rating, date, description)

elif action == 'extr_movie':
    navigator.navigator().extrMovie(url, title, image_link, link_type, rating, date, description)

##
elif action == 'get_series':
    navigator.navigator().getSeries(url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num)

elif action == 'extract_series_part1':
    navigator.navigator().extractSeriesPart1(url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num)

elif action == 'extract_series_part2':
    navigator.navigator().extractSeriesPart2(url, title, image_link, link_type, rating, date, description, season_num, episode_title, episode_image, episode_num)



elif action == 'play_movie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()