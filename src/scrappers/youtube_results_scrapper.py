from youtubesearchpython import VideosSearch

class YoutubeResultsScrapper:
    """
    """     
    
    def get_first_result(self, song_record):
        """[summary]

        Args:
            song_record ([type]): [description]

        Returns:
            [type]: [description]
        """
        song = song_record['song']
        artist = song_record['artist']

        try:
            query = VideosSearch(self._build_search_query(artist, song), limit=2)
            link = query.result()['result'][0]['link']

            return link
        except:
            print(f'Failed to get link for: {song}')
            
            return ''
    
    def _build_search_query(self, artist, song):
        """Generates the search query such that the instrumental verson 
        of the song is searched.

        Args:
            artist ([type]): [description]
            song ([type]): [description]

        Returns:
            [type]: [description]
        """
        return f'{artist} {song} instrumental'
