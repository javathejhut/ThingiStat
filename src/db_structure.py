import os
import sys

SRC_DIR = os.path.dirname(os.path.abspath(__file__))  # abspath root/src/
PROJECT_ROOT = os.path.dirname(SRC_DIR)  # abspath root/
DB_DIR = os.path.join(PROJECT_ROOT, "thing_db")  # root/thing_db
sys.path.append(PROJECT_ROOT)
# db schema

DB_TABLES = ['''things (
                    id INT PRIMARY KEY,
                    name TEXT,
                    thumbnail TEXT,
                    public_url TEXT,
                    added TEXT,
                    modified TEXT,
                    is_wip INT,
                    is_featured INT,
                    is_nsfw INT,
                    like_count INT,
                    collect_count INT,
                    comment_count INT,
                    description TEXT,
                    instructions TEXT,
                    details TEXT,
                    license TEXT,
                    allows_derivatives INT,
                    file_count INT,
                    print_history_count INT,
                    download_count INT,
                    view_count INT,
                    remix_count INT,
                    make_count INT,
                    root_comment_count INT,
                    is_derivative INT,
                    can_comment INT,
                    added_images_count INT,
                    likes_count INT,
                    likes_ids TEXT,
                    average_download_count INT,
                    tags TEXT,
                    ancestor_ids TEXT,
                    creator_id INT,
                    accessed TEXT,
                    categories TEXT,
                    
                    FOREIGN KEY(creator_id) REFERENCES creators (id)
                    ) ''',
             '''creators (
                    id INT PRIMARY KEY,
                    name TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    public_url TEXT,
                    count_of_followers INT,
                    count_of_following INT,
                    count_of_designs INT,
                    accepts_tips INT,
                    location TEXT
                    )''',
             '''tags (
                    name TEXT PRIMARY KEY,
                    tag TEXT,
                    absolute_url TEXT,
                    count INT
                    )''',
             '''categories (
                    id INT PRIMARY KEY,
                    name TEXT,
                    count INT,
                    slug TEXT
                    )'''
             ]
