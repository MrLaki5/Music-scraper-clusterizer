from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, Numeric, Enum

# Creates metadata where all tables will be written
metadata = MetaData()

# Table definitions
artist = Table('artist', metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('site_id', String(50), nullable=False))

artist_name = Table('artist_name', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('id_artist', ForeignKey('artist.id'), nullable=False),
                    Column('name', String(200), nullable=False))

artist_web = Table('artist_web', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('id_artist', ForeignKey('artist.id'), nullable=False),
                   Column('web', String(200), nullable=False))

person = Table('person', metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('site_id', String(50), nullable=False),
               Column('vocals_num', Integer, nullable=False, default=0))

person_name = Table('person_name', metadata,
                    Column('id', Integer, primary_key=True, autoincrement=True),
                    Column('id_person', ForeignKey('person.id'), nullable=False),
                    Column('name', String(200), nullable=False))

person_web = Table('person_web', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('id_person', ForeignKey('person.id'), nullable=False),
                   Column('web', String(200), nullable=False))

album = Table('album', metadata,
              Column('id', Integer, primary_key=True, autoincrement=True),
              Column('id_artist', ForeignKey('artist.id'), nullable=False),
              Column('rating', Numeric(20, 5), nullable=True),
              Column('genre', String(50), nullable=False),
              Column('style', String(50), nullable=False),
              Column('style', String(5), nullable=False),
              Column('country', String(50), nullable=False),
              Column('format', String(100), nullable=True),
              Column('site_id', String(50), nullable=False))

album_name = Table('album_name', metadata,
                   Column('id', Integer, primary_key=True, autoincrement=True),
                   Column('id_album', ForeignKey('album.id'), nullable=False),
                   Column('name', String(200), nullable=False))

song = Table('song', metadata,
             Column('id', Integer, primary_key=True, autoincrement=True),
             Column('duration', Numeric(20), nullable=True),
             Column('name', String(200), nullable=False),
             Column('site_id', String(50), nullable=False))

# Relation tables
song_on_album = Table('song_on_album', metadata,
                      Column('id_album', ForeignKey('album.id'), nullable=False, primary_key=True),
                      Column('id_song', ForeignKey('song.id'), nullable=False, primary_key=True))

person_on_artist = Table('person_on_artist', metadata,
                         Column('id_artist', ForeignKey('artist.id'), nullable=False, primary_key=True),
                         Column('id_person', ForeignKey('person.id'), nullable=False, primary_key=True))

person_on_song = Table('person_on_song', metadata,
                       Column('id_person', ForeignKey('person.id'), nullable=False, primary_key=True),
                       Column('id_song', ForeignKey('song.id'), nullable=False, primary_key=True))
