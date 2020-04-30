"""
Created on 25 août 2017

@author: julien
"""

from flask import Flask
from flask_restful import Api, Resource

from zigraph.graph import Graph
from zigraph.pathanalyzer import analyze, refresh_metas

HEADERS = {'Access-Control-Allow-Origin': '*'}

APP = Flask(__name__)
API = Api(APP)
GRAPH = Graph()

class Genres(Resource):
    """
    Liste des genres
    """
    # pylint: disable=R0201
    def get(self):
        """
        GET
        """
        return GRAPH.genre_list(), HEADERS

class Styles(Resource):
    """
    Liste des styles
    """
    # pylint: disable=R0201
    def get(self):
        """
        GET
        """
        return GRAPH.style_list(), HEADERS

class GenresAlbums(Resource):
    """
    Liste des albums pour un genre
    """
    # pylint: disable=R0201
    def get(self, genre_name):
        """
        GET
        """
        return GRAPH.album_list(genre=genre_name), HEADERS

class StylesAlbums(Resource):
    """
    Liste des albums pour  un style
    """
    # pylint: disable=R0201
    def get(self, style_name):
        """
        GET
        """
        return GRAPH.album_list(style=style_name), HEADERS

class Albums(Resource):
    """
    Liste des albums
    """
    # pylint: disable=R0201
    def get(self, album_id):
        """
        GET
        """
        return GRAPH.album_list(album_id=int(album_id)), HEADERS

class AlbumArtists(Resource):
    """
    Liste des artistes pour un album
    """
    # pylint: disable=R0201
    def get(self, album_id):
        """
        GET
        """
        return GRAPH.artist_list(album_id=int(album_id)), HEADERS

class AlbumGenres(Resource):
    """
    Liste des genres pou run album
    """
    # pylint: disable=R0201
    def get(self, album_id):
        """
        GET
        """
        return GRAPH.genre_list(album_id=int(album_id)), HEADERS

class AlbumStyles(Resource):
    """
    Liste des styles pour un album
    """
    # pylint: disable=R0201
    def get(self, album_id):
        """
        GET
        """
        return GRAPH.style_list(album_id=int(album_id)), HEADERS

class Artists(Resource):
    """
    Liste des artistes
    """
    # pylint: disable=R0201
    def get(self, artist_id):
        """
        GET
        """
        return GRAPH.artist_list(artist_id=int(artist_id)), HEADERS

class ArtistAlbums(Resource):
    """
    Liste des album pour un artiste
    """
    # pylint: disable=R0201
    def get(self, artist_id):
        """
        GET
        """
        return GRAPH.album_list(artist_id=int(artist_id)), HEADERS

class RolesHeads(Resource):
    """
    Liste des headers pour les roles
    """
    # pylint: disable=R0201
    def get(self, name, action):
        """
        GET
        """
        print("RolesHeads : name = ", name, " - action = ", action)
        if name == '-':
            return GRAPH.roles_heads(), HEADERS
        
        return GRAPH.roles_heads(name, action), HEADERS
        
class RolesSubHeads(Resource):
    """
    Liste des subheaders pour les roles
    """
    # pylint: disable=R0201
    def get(self, name, action):
        """
        GET
        """
        print("RolesSubHeads : name = ", name, " - action = ", action)

        if name == '-':
            return GRAPH.roles_subheads(), HEADERS

        return GRAPH.roles_subheads(name), HEADERS

class RolesCredits(Resource):
    """
    Liste des credits pour les roles
    """
    # pylint: disable=R0201
    def get(self, name, action):
        """
        GET
        """
        print("RolesCredits : name = ", name, " - action = ", action)

        if name == '-':
            return GRAPH.roles_credits(), HEADERS
        
        return GRAPH.roles_credits(name), HEADERS

class InitDB(Resource):
    """
    Reinitialisation de la bdd
    """
    # pylint: disable=R0201
    def get(self):
        """
        GET
        """
        GRAPH.reset()
        analyze(GRAPH)
        return {'result': 'OK'}, HEADERS

class RefreshDB(Resource):
    """
    Rafraîchissement des métadonnées
    """
    # pylint: disable=R0201
    def get(self):
        """
        GET
        """
        print("RefreshDB")
        refresh_metas(GRAPH)
        return {'result': 'OK'}, HEADERS

API.add_resource(Albums, '/albums/<album_id>')
API.add_resource(AlbumArtists, '/albums/<album_id>/artists')
API.add_resource(AlbumGenres, '/albums/<album_id>/genres')
API.add_resource(AlbumStyles, '/albums/<album_id>/styles')

API.add_resource(Artists, '/artists/<artist_id>')
API.add_resource(ArtistAlbums, '/artists/<artist_id>/albums')

API.add_resource(Genres, '/genres')
API.add_resource(GenresAlbums, '/genres/<path:genre_name>/albums')

API.add_resource(RolesHeads, '/rolesheads/<name>/<action>')
API.add_resource(RolesSubHeads, '/rolessubheads/<name>/<action>')
API.add_resource(RolesCredits, '/rolescredits/<name>/<action>')

API.add_resource(Styles, '/styles')
API.add_resource(StylesAlbums, '/styles/<path:style_name>/albums')

API.add_resource(RefreshDB, '/refreshDB')

if __name__ == '__main__':
    APP.run()
