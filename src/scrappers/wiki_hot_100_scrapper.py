from bs4 import BeautifulSoup
import requests


class WikiHot100Scrapper:
    """[summary]
    """
    BASE_WIKI_URL = 'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_'

    def __init__(self, start_year: int, end_year: int):
        """[suzmmary]

        Args:
            start_year ([type]): [description]
            end_year ([type]): [description]
        """
        self.start_year = start_year
        self.end_year = end_year

    def scrape_all_tables(self):
        full_song_data = self._init_song_data()
  
        for year in range(self.start_year, self.end_year+1):
            self._scrape_year_table(year, full_song_data)

        return full_song_data

    def _scrape_year_table(self, year:int, song_data:dict):
        """Scrapes data from Billboard Top 100 table corresponding to the input year.

        Args:
            year (int): [description]
            song_data (dict): [description]

        Returns:
            [type]: [description]
        """
        song_table = self._get_song_table(year)
        
        if song_table is None:
            print(f'Wiki page for year {year} does not exist.')
            return 
        
        rows = song_table.select('tr td')
        for song_row_index in range(0, len(rows) - 3, 3):
            year, artist, song = self._get_song_attributes(year,
                rows, song_row_index)
            self._append_to_song_data(song_data, year, artist, song)

    def _generate_wiki_year_url(self, year: int):
        return f'{self.BASE_WIKI_URL}{year}'

    def _init_song_data(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        song_data = {}
        song_data['year'] = []
        song_data['artist'] = []
        song_data['song'] = []

        return song_data

    def _append_to_song_data(self, song_data, year, artist, song):
        """[summary]

        Args:
            song_data ([type]): [description]
            year ([type]): [description]
            artist ([type]): [description]
            song ([type]): [description]
        """
        song_data['year'].append(year)
        song_data['artist'].append(artist)
        song_data['song'].append(song)

    def _get_song_attributes(self, year, rows, song_row_index):
        """

        Args:
            year ([type]): [description]
            rows ([type]): [description]
            song_row_index ([type]): [description]

        Returns:
            [type]: [description]
        """
        song_name_index = song_row_index + 1
        song_artists_index = song_row_index + 2
        song_name_cell = rows[song_name_index]
        linked_song_name = song_name_cell.find('a')
        
        if not linked_song_name:
            song = song_name_cell.get_text().strip('"')
        else:
            song = linked_song_name.get_text().strip('"')
        artist_names_cell = rows[song_artists_index].find_all('a')
        
        if artist_names_cell:
            # merge all the authors if there are many linked authors in cell
            artist = [person.get_text() for person in artist_names_cell]
            artist = ', '.join(artist)
        else:
            artist = rows[song_artists_index].get_text().strip()
        
        return year, artist, song

    def _get_song_table(self, year):
        """[summary]

        Args:
            year ([type]): [description]

        Returns:
            [type]: [description]
        """
        wiki_year_url = self._generate_wiki_year_url(year)
        wiki_page_result = requests.get(wiki_year_url)

        if wiki_page_result.status_code != 200:
            return None

        page_html = wiki_page_result.content
        soup = BeautifulSoup(page_html, 'html.parser')

        song_table = soup.find(
            'table', {'class': ['wikitable', 'sortable', 'jquery-tablesorter']})
        
        return song_table
