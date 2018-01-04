'''
Created on 25 août 2017

@author: julien
'''

import hashlib
import json
import time
import requests

from zigraph.config import CONFIG

USER_AGENT = 'ZicGraphLib/0.1'


PER_PAGE = 10

SEARCH_URL = 'https://api.discogs.com/database/search?'

class DiscoSearch():
    '''
    classdocs
    '''
    remaining_calls = 0
    search_cache = {}

    def search(self, artist, album):
        '''
        searchdoc
        '''
        search_hash = hashlib.sha256(str(artist + '///' + album).encode('utf-8')).hexdigest()
        if search_hash not in self.search_cache:
            res = json.JSONEncoder().encode('{}')

            url = SEARCH_URL \
                + 'artist=' + artist \
                + '&title=' + album \
                + '&PER_PAGE=' + str(PER_PAGE)

            search_results = self.__load(url)

            if search_results['pagination']['items'] > 0:
                # print("pag_items = ", search_results['pagination']['items'], search_results)
                rel = self.__load(search_results['results'][0]['resource_url'])
                if 'main_release_url' in rel:
                    res = self.__load(rel['main_release_url'])
                else:
                    if 'master_url' in rel:
                        master = self.__load(rel['master_url'])
                        res = self.__load(master['main_release_url'])
                    else:
                        res = rel

            self.search_cache[search_hash] = res

        return  self.search_cache[search_hash]

    def __load(self, url):
        if self.remaining_calls < 5:
            time.sleep(1)

        lurl = url
        if '?' in url:
            lurl += '&'
        else:
            lurl += '?'
        lurl += 'token=' + CONFIG.get('discogs', 'token')

        req = requests.get(lurl, headers={'user_agent': USER_AGENT})
        self.remaining_calls = int(req.headers['X-Discogs-Ratelimit-Remaining'])
        # print('Remaining : ', self.remaining_calls)
        return json.loads(req.content.decode('utf-8'))
