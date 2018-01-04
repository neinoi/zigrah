'''
Created on 28 août 2017

@author: julien
'''
import Levenshtein

if __name__ == '__main__':
    # 'artist': 'Duke Ellington, Charles Mingus, Max Roach', 'album': 'Money Jungle'

    #INFOS = DiscoSearch().search('Duke Ellington, Charles Mingus, Max Roach', 'Money Jungle')
    #print(INFOS)

    print(Levenshtein.ratio('Pat Metheny Trio'.upper(), 'Pat Metheny'.upper()))
