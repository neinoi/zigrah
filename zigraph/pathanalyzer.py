'''
Outil d'analyse de dossier contenant des fichiers mp3
'''
from pathlib import Path
from zigraph.tagextractor import extract_tags
from zigraph.discosearch import DiscoSearch
from zigraph.config import CONFIG

def analyze(graph):
    '''
    Fonction principale qui recherche les fichiers et les ajoute au graphe
    '''
    path = Path(CONFIG.get('music', 'directory'))

    files = list(path.glob('**/*.mp3'))

    for file in files:

        try:
            tags = extract_tags(file)

            db_file = graph.file_add(file, tags['artist'], tags['album'])

            __refresh_file(graph, db_file)

        except Exception as exc:
            print("ERROR : ", exc, "FILE : ", file)

def refresh_metas(graph):
    '''
    Fonction pour rafraichir les méadonnées sans vider le graphe avant
    '''
    for db_file in graph.file_node_list():
        __refresh_file(graph, db_file)

def __refresh_file(graph, file_node):
    try:
        infos = DiscoSearch().search(file_node.artist, file_node.album)
        if len(infos) > 0 and isinstance(infos, dict):
            alb_id, alb_title, alb_year, alb_genres, alb_styles = infos['id'], infos['title'], \
                infos['year'], infos['genres'], infos.get('styles', [])

            db_album = graph.album_add(alb_id, alb_title, alb_year, alb_genres, alb_styles)
            graph.file_track_of(file_node, db_album)

            for art in infos['artists']:
                db_artist = graph.artist_add(art['id'], art['name'])
                graph.artist_role_in(db_artist, 'artist', db_album)

            for art in infos['extraartists']:
                db_artist = graph.artist_add(art['id'], art['name'])

                roles = art['role'].split(',')
                for role in roles:
                    graph.artist_role_in(db_artist, role, db_album)
        else:
            print("!!! KO : ", file_node)
            print("==> INFOS : ", infos)
    except Exception as exc:
        print("!!! KO : ", file_node, exc)
