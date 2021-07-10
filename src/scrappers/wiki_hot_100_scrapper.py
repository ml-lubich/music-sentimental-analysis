from bs4 import BeautifulSoup
import requests


class WikiHot100Scrapper:
    """Scrapper that fetches the "Hot 100 tracks" from a subset of
    valid years. Metadata from the table includes the artist(s) along
    with the name of the track.
    """
    BASE_WIKI_URL = 'https://en.wikipedia.org/wiki/Billboard_Year-End_Hot_100_singles_of_'

    def __init__(self, start_year, end_year):
        """Constructor.

        Args:
            start_year (int): start year bound for the scrapper.
            end_year (int): end year bound for the scrapper.
        """
        if end_year < start_year:
            end_year = start_year
        
        self.start_year = self.check_bound_year(start_year)
        self.end_year = self.check_bound_year(end_year)

    def scrape_all_tables(self):
        """Scraps all of the selected years and returns the
        scrapped data.

        Returns:
            dict: Scrapped data as a mapping of {year, artist, song}.
        """
        full_song_data = self._init_song_data()

        for year in range(self.start_year, self.end_year+1):
            self._scrape_year_table(year, full_song_data)

        return full_song_data

    def _scrape_year_table(self, year, song_data):
        """Scrapes data from Billboard Top 100 table for the
        specified year.

        Args:
            year (int): year to scrape.
            song_data (dict): data structure that will store the output of the
            scrapped data.
        """
        song_table = self._get_song_table(year)

        if song_table is None:  # no song table found for this year or error occured
            print(f'Wiki page for year {year} does not exist.')
            return

        rows = song_table.select('tr td')
        # go through every row in table
        for song_row_index in range(0, len(rows) - 3, 3):
            year, artist, song = self._get_song_attributes(year,
                                                           rows, song_row_index)
            self._append_to_song_data(song_data, year, artist, song)

    def _generate_wiki_year_url(self, year):
        """Generate the Wiki url for the given year.

        Args:
            year (int): year for which url should be generated for.

        Returns:
            str: the Wiki Hot 100 year for that year.
        """
        return f'{self.BASE_WIKI_URL}{year}'

    def _init_song_data(self):
        """Instantiates the data stucture that will store the scrapped data
        from the wiki tables.

        Returns:
            song_data (dict): data structure that will store the output of the
            scrapped data.
        """
        song_data = {}
        song_data['year'] = []
        song_data['artist'] = []
        song_data['song'] = []

        return song_data

    def _append_to_song_data(self, song_data, year, artist, song):
        """Appends scrapped data to the data structure that holds
        all of the scrapped data.

        Args:
            song_data (dict): data structure used for storing scrapped data.
            year (int): year the track hit Hot 100.
            artist (str): name of the artist of the track.
            song (str): title of the track.
        """
        song_data['year'].append(year)
        song_data['artist'].append(artist)
        song_data['song'].append(song)

    def _get_song_attributes(self, year, rows, song_row_index):
        """Intelligently get the row contents. Since the DOM will look
        differently depending on whether the row's cell are hyperlinks
        to other Wiki pages, the parse behaves differently depending on
        the case.

        Args:
            year (int): year of the Hot 100 scrapper.
            rows (list): scrapped rows from the table.
            song_row_index (int): index on which the record is one. This will
            be a multiple of 3 since scrapper internally pulls by cell instead of
            row. Since there are 3 cells {year, song, artist} in each table row,
            it will thus be a multiple of 3.

        Returns:
            tuple(int, str, str): scrapped data of the tuple {year, artist, song}
        """
        song_name_index = song_row_index + 1
        song_artists_index = song_row_index + 2
        song_name_cell = rows[song_name_index]
        linked_song_name = song_name_cell.find('a')

        if not linked_song_name:  # song name is not a hyperlink to another wiki page
            song = song_name_cell.get_text().strip('"')
        else:
            song = linked_song_name.get_text().strip('"')
        artist_names_cell = rows[song_artists_index].find_all('a')

        if artist_names_cell:  # if multiple artists for a song
            # merge all the authors if there are many linked authors in cell
            artist = [person.get_text() for person in artist_names_cell]
            artist = ', '.join(artist)
        else:
            artist = rows[song_artists_index].get_text().strip()

        return year, artist, song

    def _get_song_table(self, year):
        """Locates and returns the DOM of the Hot 100 table
        if it was found on the page.

        Args:
            year (int): year of the table to fetch.

        Returns:
            None|BeautifulSoup.Tag: none if the table wasn't found or
            the a DOM reference if otherwise.
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

    def check_bound_year(self, year):
        """Check if the input year is within bounds. Currently valid years
        are is any year in the range [1946, 2020] of Z-+.

        Args:
            year (int): year to check.

        Returns:
            int: either the original year if within bounds or the capped year
            if outside of bounds.
        """
        if year < 1946:
            return 1946
        elif year > 2020:
            return 2020

        return year
