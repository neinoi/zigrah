"""
Created on 25 août 2017

@author: julien
"""
import eyed3

def extract_tags(file):
    """
    Renvoie les informations id3 "artist", "album", "title" du fichier donné
    """
    audiofile = eyed3.load(file)

    artist = audiofile.tag.artist
    if artist is None:
        artist = audiofile.tag.album_artist

    return {'artist' : artist,
            'album' : audiofile.tag.album,
            'title' : audiofile.tag.title}
