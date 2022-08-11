import sqlite3
import os
import numpy as np
import json
from db_structure import DB_TABLES, DB_DIR


def get_wildcards(cursor_instance, table_name):
    """
    A wrapper function that returns a wildcard string of the appropriate size for an existing table.
    Used for SQLite INSERT commands.

    Args:
        cursor_instance: cursor
            Instance of SQLite cursor
        table_name: str
            Name of existing SQL table
    Returns:
        wildcards: str
            String of format "?,?,?,?,....,?" of appropriate length for table.
    """
    cursor_instance.execute("PRAGMA table_info(%s)" % table_name)
    wildcards = ','.join(['?'] * len(cursor_instance.fetchall()))
    return wildcards


def convert_empty_to_null(entry):
    """
    Converts empty strings to "NULL" string for consistency in SQL tables.
    """
    if isinstance(entry, str):
        return entry or "NULL"
    else:
        return entry


def convert_none_dict_to_empty(entry):
    """
    Converts none entry (sometimes returned by API) to empty dictionary.
    """
    if entry:
        return entry
    else:
        return {}


class DBCursor:
    """
    This class saves having to write code to connect to the database and create
    a cursor every time. Instead, use with DBCursor(file) as cursor:
        cursor.execute()
    Once outside of the with statement it will commit and close the database
    automatically too.
    """

    def __init__(self, db_filename):
        self.db_filename = db_filename

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_filename)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.commit()
        self.connection.close()
        if exc_type is not None:
            print(exc_type, exc_value)
        return


class ThingDB:
    """
    This database class creates tables and includes methods to populate them.
    Input
        db_filename (str) : file where database is/will be saved.
    """

    def __init__(self, db_filename):
        self.db_dir = DB_DIR
        self.db_path = os.path.join(self.db_dir, db_filename)

        if not os.path.isdir(self.db_dir):
            os.makedirs(self.db_dir)

        with DBCursor(self.db_path) as cursor:
            for tables in DB_TABLES:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {tables}")

    def get_last_thing_id(self):
        query = 'SELECT id FROM things ORDER BY rowid DESC LIMIT 1'
        with DBCursor(self.db_path) as cursor:
            cursor.execute(query)
            cursor.row_factory = lambda cur, row: row[0]
            output = cursor.fetchall()
            if len(output) > 0:
                return_id = output[0]
            else:
                return_id = 1

        return return_id

    def add_thing(self, json_dict):

        # extract some (seemingly important to me) non-explicit features
        creator_id = json_dict['thing']['creator']['id']
        added_images_count = len(convert_none_dict_to_empty(json_dict['images'])) - \
                             len(convert_none_dict_to_empty(json_dict['files']))

        likes_count = len(convert_none_dict_to_empty(json_dict['likes']))

        if json_dict['files']:
            average_downloads_count = int(np.mean([ele["download_count"] for ele in json_dict['files']]))
        else:
            average_downloads_count = 0

        ancestors_list = [ele['id'] for ele in json_dict['thing']['ancestors']]
        if len(ancestors_list) > 0:
            ancestor_ids = json.dumps(ancestors_list)
        else:
            ancestor_ids = "NULL"

        tags_list = [ele['tag'] for ele in json_dict['thing']['tags']]
        if len(tags_list) > 0:
            tags = json.dumps(tags_list)
        else:
            tags = "NULL"

        likes_id_list = [ele['id'] for ele in json_dict['likes']]
        if len(likes_id_list) > 0:
            likes_ids = json.dumps(likes_id_list)
        else:
            likes_ids = "NULL"



        with DBCursor(self.db_path) as cursor:

            thing_dict = json_dict['thing']

            # populate creators table
            creator_dict = thing_dict['creator']
            creator_attributes = tuple(map(convert_empty_to_null, (creator_dict.get('id', "NULL"),
                                                                   creator_dict.get('name', "NULL"),
                                                                   creator_dict.get('first_name', "NULL"),
                                                                   creator_dict.get('last_name', "NULL"),
                                                                   creator_dict.get('public_url', "NULL"),
                                                                   creator_dict.get('count_of_followers', "NULL"),
                                                                   creator_dict.get('count_of_following', "NULL"),
                                                                   creator_dict.get('count_of_designs', "NULL"),
                                                                   creator_dict.get('accepts_tips', "NULL"),
                                                                   creator_dict.get('location', "NULL"),
                                                                   )))

            cursor.execute("INSERT OR IGNORE INTO creators VALUES (%s)" % get_wildcards(cursor, "creators"),
                           creator_attributes)

            # populate things table
            thing_attributes = tuple(map(convert_empty_to_null, (thing_dict.get('id', "NULL"),
                                                                 thing_dict.get('name', "NULL"),
                                                                 thing_dict.get('thumbnail', "NULL"),
                                                                 thing_dict.get('public_url', "NULL"),
                                                                 thing_dict.get('added', "NULL"),
                                                                 thing_dict.get('modified', "NULL"),
                                                                 thing_dict.get('is_wip', "NULL"),
                                                                 thing_dict.get('is_featured', "NULL"),
                                                                 thing_dict.get('is_nsfw', "NULL"),
                                                                 thing_dict.get('like_count', "NULL"),
                                                                 thing_dict.get('collect_count', "NULL"),
                                                                 thing_dict.get('comment_count', "NULL"),
                                                                 thing_dict.get('description', "NULL"),
                                                                 thing_dict.get('instructions', "NULL"),
                                                                 thing_dict.get('details', "NULL"),
                                                                 thing_dict.get('license', "NULL"),
                                                                 thing_dict.get('allows_derivatives', "NULL"),
                                                                 thing_dict.get('file_count', "NULL"),
                                                                 thing_dict.get('print_history_count', "NULL"),
                                                                 thing_dict.get('download_count', "NULL"),
                                                                 thing_dict.get('view_count', "NULL"),
                                                                 thing_dict.get('remix_count', "NULL"),
                                                                 thing_dict.get('make_count', "NULL"),
                                                                 thing_dict.get('root_comment_count', "NULL"),
                                                                 thing_dict.get('is_derivative', "NULL"),
                                                                 thing_dict.get('can_comment', "NULL"),
                                                                 added_images_count,
                                                                 likes_count,
                                                                 likes_ids,
                                                                 average_downloads_count,
                                                                 tags,
                                                                 ancestor_ids,
                                                                 creator_id
                                                                 )))

            cursor.execute("INSERT OR IGNORE INTO things VALUES (%s)" % get_wildcards(cursor, "things"),
                           thing_attributes)

            # populate tags table
            tags_dict = thing_dict['tags']
            for entry in tags_dict:
                tags_attributes = tuple(map(convert_empty_to_null, (entry['name'],
                                                                    entry['tag'],
                                                                    entry['absolute_url'],
                                                                    entry['count']
                                                                    )))
                cursor.execute("INSERT OR IGNORE INTO tags VALUES (%s)" % get_wildcards(cursor, "tags"),
                               tags_attributes)
