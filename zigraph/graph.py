'''
Created on 25 août 2017

@author: julien
'''
import os
import csv

from grapheekdb.backends.data.kyotocab import KyotoCabinetGraph

from zigraph.config import CONFIG


class Graph:
    '''
    Classe de gestion du graphe de données musicales
    '''
    graph = None

    def __init__(self):
        self.graph = KyotoCabinetGraph(CONFIG.get('database', 'file'))

    def reset(self):
        '''
        fonction qui réinitialise la base grapheekdb
        '''
        self.graph.close()
        os.remove(CONFIG.get('database', 'file'))
        self.graph = KyotoCabinetGraph(CONFIG.get('database', 'file'))
        self.__init_roles()

    def __init_roles(self):
        '''
        Fonction qui charge les roles dans la base graphe au démarrage, à partir du csv "roles.csv"
        '''
        for node in self.graph.V(kind='credit'):
            node.remove()
        for node in self.graph.V(kind='credit heading'):
            node.remove()
        for node in self.graph.V(kind='credit subheading'):
            node.remove()

        i = 0
        with open(CONFIG.get('music', 'roles'), newline='') as csvfile:

            rolesreader = csv.reader(csvfile, delimiter=',')
            next(rolesreader, None)

            for credit, heading, subheading in rolesreader:
                i += 1
                print("line : ", i)
                try:
                    db_role = self.graph.V(kind='credit', name=credit).next()
                except StopIteration:
                    db_role = self.graph.add_node(kind='credit', name=credit)
                    if heading:
                        try:
                            db_heading = self.graph.V(kind='credit heading', name=heading).next()
                        except StopIteration:
                            db_heading = self.graph.add_node(kind='credit heading', name=heading)

                        self.graph.add_edge(db_role, db_heading, relation='credit_heading')

                        if subheading:
                            try:
                                db_subhead = self.graph \
                                    .V(kind='credit subheading', name=subheading).next()
                            except StopIteration:
                                db_subhead = self.graph \
                                    .add_node(kind='credit subheading', name=subheading)

                            self.graph \
                                .add_edge(db_role, db_subhead, relation='credit_subheading')

                            self.graph \
                                .add_edge(db_subhead, db_heading, relation='subheading_heading')

    def file_add(self, file, artist, album):
        '''
        Ajout d'un fichier mp3
        '''
        try:
            db_file = self.graph.V(kind='file', path=str(file)).next()
        except StopIteration:
            db_file = self.graph.add_node(kind='file', path=str(
                file), artist=artist, album=album)

        return db_file

    def album_add(self, ident, title, year, genres, styles):
        '''
        Ajout d'un album
        '''
        try:
            db_album = self.graph.V(kind='album', id=ident).next()
        except StopIteration:
            db_album = self.graph.add_node(
                kind='album', id=ident, name=title, year=year)

            for genre in genres:
                db_genre = self.genre_add(genre)
                self.album_genre(db_album, db_genre)

            for style in styles:
                db_style = self.style_add(style)
                self.album_style(db_album, db_style)

        return db_album

    def genre_add(self, genre):
        '''
        Ajout d'un genre
        '''
        try:
            db_genre = self.graph.V(kind='genre', name=genre).next()
        except StopIteration:
            db_genre = self.graph.add_node(kind='genre', name=genre)

        return db_genre

    def file_node_list(self):
        '''
        Renvoie la liste des fichiers physiques de la base
        '''
        return self.graph.V(kind='file')

    def genre_list(self, album_id=None):
        '''
        Liste des genres [par album]
        '''
        grs = []
        if album_id:
            grs = [{'name': g.name, 'albums': self.graph.V(kind='genre', name=g.name).inV().count(
            )} for g in
                   self.graph.V(kind='album', id=album_id)
                   .outE(relation='genre')
                   .outV(kind='genre')]
        else:
            grs = [{'name': g.name, 'albums': self.graph.V(
                kind='genre', name=g.name).inV().count()} for g in self.graph.V(kind='genre')]

        return sorted(grs, key=lambda genre: genre['albums'], reverse=True)

    def album_list(self, genre=None, style=None, album_id=None, artist_id=None):
        '''
        Liste des albums [par [genre, style, album, artist]]
        '''

        if album_id:
            db_album = self.graph.V(kind='album', id=album_id).next()
            return {'id': db_album.id,
                    'name': db_album.name,
                    'year': db_album.year,
                    'artists': self.artist_list(album_id=album_id, role='artist')}

        albs = []
        if genre:
            albs = [{'id': db_album.id,
                     'name': db_album.name,
                     'year': db_album.year,
                     'artists': self.artist_list(album_id=db_album.id, role='artist')}
                    for db_album
                    in self.graph.V(kind='genre', name=genre)
                    .inE(relation='genre')
                    .inV(kind='album')]

        else:
            if style:
                albs = [{'id': db_album.id,
                         'name': db_album.name,
                         'year': db_album.year,
                         'artists': self.artist_list(album_id=db_album.id, role='artist')}
                        for db_album in
                        self.graph.V(kind='style', name=style)
                        .inE(relation='style')
                        .inV(kind='album')]
            else:
                if artist_id:
                    albs = [{'id': db_album.id,
                             'name': db_album.name,
                             'year': db_album.year,
                             'artists': self.artist_list(album_id=db_album.id, role='artist'),
                             'roles': [r[0].role
                                       for r in self.graph.V(kind='artist', id=artist_id)
                                       .bothE(relation='playsIn').aka('rel')
                                       .bothV(kind='album', id=db_album.id).collect('rel')]
                            } for db_album
                            in self.graph.V(kind='artist', id=artist_id)
                            .bothE(relation='playsIn')
                            .bothV(kind='album').dedup()]
                else:
                    albs = [{'id': db_album.id,
                             'name': db_album.name,
                             'year': db_album.year,
                             'artists': self.artist_list(album_id=db_album.id, role='artist')}
                            for db_album in self.graph.V(kind='album')]

        return sorted(albs, key=lambda album: album['year'])

    def artist_list(self, artist_id=None, album_id=None, role=None):
        '''
        Liste des artistes [par album] ou un artiste
        '''
        if artist_id:
            db_artist = self.graph.V(kind='artist', id=artist_id).next()
            return {'id': db_artist.id, 'name': db_artist.name}

        if album_id and role:
            return [{'id': db_artist.id,
                     'name': db_artist.name} for db_artist
                    in self.graph.V(kind='album', id=album_id)
                    .inE(relation='playsIn', role=role)
                    .inV(kind='artist').dedup()]

        if album_id:
            return [{'id': db_artist.id,
                     'name': db_artist.name,
                     'roles': [r[0].role
                               for r in self.graph.V(kind='album', id=album_id)
                               .bothE(relation='playsIn').aka('rel')
                               .bothV(kind='artist', id=db_artist.id).collect('rel')]
                    } for db_artist
                    in self.graph.V(kind='album', id=album_id)
                    .inE(relation='playsIn')
                    .inV(kind='artist').dedup()]

        return [{'id': db_artist.id, 'name': db_artist.name}
                for db_artist
                in self.graph.V(kind='artist')]

    def style_add(self, style):
        '''
        Ajout d'un style
        '''
        try:
            db_style = self.graph.V(kind='style', name=style).next()
        except StopIteration:
            db_style = self.graph.add_node(kind='style', name=style)

        return db_style

    def style_list(self, album_id=None):
        '''
        Liste des styles [par album]
        '''
        if album_id:
            return [{
                'name': s.name,
                'albums': self.graph.V(kind='style', name=s.name).inV().count()
            } for s in self.graph.V(kind='album', id=album_id)
                    .outE(relation='style')
                    .outV(kind='style')]

        return [{'name': s.name, 'albums': self.graph.V(kind='style', name=s.name).inV().count()}
                for s in self.graph.V(kind='style')]

    def roles_heads(self, name=None, action=None):
        '''
        Liste des headers de rôles
        '''
        if name is None:
            return sorted([h.name for h in self.graph.V(kind='credit heading')])
        
        if action == 'credits':
            return [h.name for h in self.graph.V(kind='credit heading', name=name).bothE().bothV(kind='credit subheading')]
        if action == 'subheads':
            return [h.name for h in self.graph.V(kind='credit heading', name=name).bothE().bothV(kind='credit subheading').bothE().bothV(kind='credit')]
        
        return [h.name for h in self.graph.V(kind='credit heading', name=name)]

    def roles_subheads(self, name=None):
        '''
        Liste des sub-headers de rôles
        '''
        if name is None:
            return sorted([h.name for h in self.graph.V(kind='credit subheading')])

        return [h.name for h in self.graph.V(kind='credit subheading', name=name)]

    def roles_credits(self, name=None):
        '''
        Liste des rôles
        '''
        if name is None:
            return sorted([h.name for h in self.graph.V(kind='credit')])

        return [h.name for h in self.graph.V(kind='credit', name=name)]

    def artist_add(self, ident, name):
        '''
        Ajout d'un artiste
        '''
        try:
            db_artist = self.graph.V(kind='artist', id=ident).next()
        except StopIteration:
            db_artist = self.graph.add_node(kind='artist', id=ident, name=name)

        return db_artist

    def album_genre(self, album, genre):
        '''
        Ajout d'un genre à un album
        '''
        create = True
        try:
            for gen in album.outE(relation='genre').outV(kind='genre'):
                if gen == genre:
                    create = False
        except StopIteration:
            create = True

        if create:
            self.graph.add_edge(album, genre, relation='genre')

    def album_style(self, album, style):
        '''
        Ajout d'un style à un album
        '''
        create = True
        try:
            for sty in album.outE(relation='style').outV(kind='style'):
                if sty == style:
                    create = False
        except StopIteration:
            create = True

        if create:
            self.graph.add_edge(album, style, relation='style')

    def file_track_of(self, file, album):
        '''
        Ajout d'un fichier à un album
        '''
        create = True
        try:
            for salb in file.outE(relation='isTrackOf').outV(kind='album'):
                if salb == album:
                    create = False
        except StopIteration:
            create = True

        if create:
            self.graph.add_edge(file, album, relation='isTrackOf')

    def artist_role_in(self, artist, role, album):
        '''
        Ajout d'un artiste à un album
        '''
        create = True
        try:
            for salb in artist.outE(relation='playsIn', role=role).outV(kind='album'):
                if salb == album:
                    create = False
        except StopIteration:
            create = True

        if create:
            self.graph.add_edge(artist, album, relation='playsIn', role=role)

    def print_graph(self):
        '''
        Fonction utilitaire pour affichage du contenu de la base
        '''
        for node in self.graph.V():
            print(node)

        for edge in self.graph.E():
            print(edge)
