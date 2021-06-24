from youtubesearchpython import VideosSearch
import pandas as pd
import requests
from bs4 import BeautifulSoup
from config import OUTPUT_DIR

# init
BASE_WIKI_URL = 'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_'

def generate_url(year):
    return f'{BASE_WIKI_URL}{year}'

# song_table.select('tr td:nth-of-type(2) a')[1].get_text() # just get the songs

# scrape
years = list(range(1946, 2021))
song_data = []  # year -> song tuple (song_artist, song_name)
count = 0
for year in years:
    url_to_get = generate_url(year)
    html = requests.get(url_to_get).content
    soup = BeautifulSoup(html, 'html.parser')
    song_table = soup.find(
        'table', {'class': ['wikitable', 'sortable', 'jquery-tablesorter']})
    songs_from_table_raw = song_table.select('tr td')
    song_table_len = len(songs_from_table_raw)

    # for each row
    for song_table_row in range(0, song_table_len, 3):
        i = song_table_row
        song_name_raw = songs_from_table_raw[i+1]
        linked_song_name = song_name_raw.find('a')
        if not linked_song_name:
            song_name = song_name_raw.get_text()
        else:
            song_name = linked_song_name.get_text()

        song_name = song_name_raw.get_text()
        artist_names_raw = song_table.select(
            'tr td')[song_table_row].find_all('a')
        artist_names = [person.get_text() for person in artist_names_raw]
        artist_names = ' '.join(artist_names)
        print(f'{count} | {i} | Processing:', song_name, ' ', artist_names)
        song_data.append({
            'year': year,
            'artist': artist_names,
            'song': song_name
        })
        count += 1

song_df = pd.DataFrame(song_data, columns=['year', 'artist', 'song'])
song_df = song_df.set_index('year')


def get_song_search_query(song_df):
    return f'{song_df["artist"]} {song_df["song"]} instrumental'


def get_youtube_search_url(song_df):
    query = VideosSearch(get_song_search_query(song_df), limit=2)
    link = query.result()['result'][0]['link']
    print(f'Get link for:', song_df['song'])
    return link


song_df['youtube_search_url'] = song_df.apply(get_youtube_search_url, axis=1)
song_df.to_csv('billboard_top_100.csv')
