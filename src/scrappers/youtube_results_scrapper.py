from youtubesearchpython import VideosSearch


class YoutubeResultsScrapper:
    """Scrapper for retrieving Youtube instrumental urls from scrapped
    Hot 100 songs.
    """

    def get_first_result(self, song_record):
        """Retrieve the first Youtube search result for a given
        song record.

        Args:
            song_record (pandas.Series): song record from scrapped
            titles.

        Returns:
            str: the url of the first query result if the search goes
            through. If the search fails, then '' is returned.
        """
        song = song_record['song']
        artist = song_record['artist']

        try:
            query = VideosSearch(
                self._build_search_query(artist, song), limit=2)
            link = query.result()['result'][0]['link']

            return link
        except:
            print(f'Failed to get link for: {song}')

            return ''

    def _build_search_query(self, artist, song):
        """Generates the search query such that the instrumental verson 
        of the song is searched.

        Args:
            artist (str): name of the artist for the query.
            song (str): name of the song for the query.

        Returns:
            str: query such that the phrase "instrumental" is appended
            at for a artist & song record.
        """
        return f'{artist} {song} instrumental'
