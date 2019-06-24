from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Numeric, Enum, Boolean

# Creates metadata where all tables will be written
metadata = MetaData()

# Table definitions
album_group = Table('album_group', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True))

album = Table('album', metadata,
              Column('id', Integer, primary_key=True, autoincrement=True),
              Column('site_id', String(50), nullable=False, unique=True),
              Column('rating', Numeric(20, 5), nullable=True),
              Column('year', Integer, nullable=True),
              Column('decade', Integer, nullable=True),
              Column('country', String(50), nullable=False),
              Column('id_album_group', ForeignKey('album_group.id'), nullable=False),
              Column('is_cyrillic', Boolean, nullable=False),
              Column('name', String(150), nullable=False))

album_format = Table('album_format', metadata,
                     Column('id', Integer, primary_key=True, autoincrement=True),
                     Column('content', String(50), nullable=False),
                     Column('id_album', ForeignKey('album.id'), nullable=False))

album_style = Table('album_style', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('content', String(50), nullable=False),
                    Column('id_album', ForeignKey('album.id'), nullable=False))

album_genre = Table('album_genre', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('content', String(50), nullable=False),
                    Column('id_album', ForeignKey('album.id'), nullable=False))

artist = Table('artist', metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('site_id', String(50), nullable=False, unique=True),
               Column('is_group', Boolean, nullable=False),
               Column('vocals', Integer, nullable=True),
               Column('name', String(100), nullable=False))

artist_web = Table('artist_web', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('id_artist', ForeignKey('artist.id'), nullable=False),
                   Column('web', String(200), nullable=False))

song = Table('song', metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('duration', Numeric(20), nullable=True),
             Column('name', String(200), nullable=False),
             Column('site_id', String(50), nullable=False, unique=True))

# Relation tables
song_on_album = Table('song_on_album', metadata,
                      Column('id_album', ForeignKey('album.id'), nullable=False, primary_key=True),
                      Column('id_song', ForeignKey('song.id'), nullable=False, primary_key=True))

artist_on_song = Table('artist_on_song', metadata,
                       Column('id_artist', ForeignKey('artist.id'), nullable=False, primary_key=True),
                       Column('id_song', ForeignKey('song.id'), nullable=False, primary_key=True),
                       Column('type', Enum('arranged', 'lyrics', 'music', 'vocals', name='contribution'),
                              default='vocals', primary_key=True))

artist_rating = Table('artist_rating', metadata,
                      Column('id_artist', ForeignKey('artist.id'), nullable=False, primary_key=True),
                      Column('id_album', ForeignKey('album.id'), nullable=False, primary_key=True))
