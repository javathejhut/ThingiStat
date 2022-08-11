import json
import os
import numpy as np
import requests
import urllib
import logging
import time
from tqdm import tqdm
from db_structure import SRC_DIR, DB_DIR
from db_utils import ThingDB

PROJECT_ROOT = os.path.dirname(SRC_DIR)  # abspath root/
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")  # root/logs

URL_BASE = urllib.parse.ParseResult(
    scheme="https",
    netloc="api.thingiverse.com",
    path="/things/",
    params="",
    query="",
    fragment="",
)

# Logging params
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = logging.FileHandler(os.path.join(LOGS_DIR, 'downloads.log'), 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', '%m-%d-%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# API authentication
with open(os.path.join(PROJECT_ROOT, "auth.json"), 'r') as f:
    auth_config = json.load(f)

session = requests.Session()
session.headers.update({"Authorization": "Bearer %s" % (auth_config['access_token'])})


def make_request(url, thing_id, attempts=3):
    for i in range(attempts):
        try:
            r = session.request(method="GET", url=url)
            r.raise_for_status()

            json_content = json.loads(r.content)
            return json_content

        except requests.HTTPError as errh:
            if errh.response.status_code == 401:
                logger.warning("thing id <%d> forbidden (unpublished) -- %s" % (thing_id, str(errh)))
                return

            if errh.response.status_code == 404:
                logger.warning("thing id <%d> not found (invalid or deleted) -- %s" % (thing_id, str(errh)))
                return

            if errh.response.status_code == 401:
                logger.warning("thing id <%d> unauthorized access -- %s" % (thing_id, str(errh)))
                return

        except requests.exceptions.ConnectionError as errc:
            logger.warning("thing id <%d> forbidden (unpublished) -- %s" % (thing_id, str(errc)))

        except requests.exceptions.Timeout as errt:
            logger.warning("thing id <%d> timeout error -- %s" % (thing_id, str(errt)))

        except requests.exceptions.RequestException as err:
            logger.warning("thing id <%d> generic error -- %s" % (thing_id, str(err)))


def construct_url(thing_id, option=""):
    target_url = urllib.parse.urlunparse(URL_BASE._replace(path=URL_BASE.path + str(thing_id) + option))
    return target_url


def thing_download_sweep(last_id, ids_list, timeout=1, db_filename='default_thingistat.db'):
    db_path = os.path.join(DB_DIR, db_filename)
    thingistat_db = ThingDB(db_path)

    index_start = ids_list.index(last_id)
    print(index_start)
    index_end = len(ids_list)
    for thing_id_index in tqdm(range(index_start, index_end, 1), initial=index_start, total=index_end):
        thing_id = int(ids_list[thing_id_index])
        # API urls
        urls = {'thing': construct_url(thing_id), 'images': construct_url(thing_id, "/images"),
                'files': construct_url(thing_id, "/files"), 'likes': construct_url(thing_id, "/likes")}

        # performing API requests, conforming to default request limit of 300 per 5 minutes

        # first try extracting 'thing' json, only continuing if present
        json_dict = {'thing': make_request(urls['thing'], thing_id)}
        time.sleep(timeout)

        if json_dict['thing'] and json_dict['thing']['creator'] is not None:

            for key in list(urls.keys())[1:]:
                json_dict[key] = make_request(urls[key], thing_id)
                time.sleep(timeout)

            thingistat_db.add_thing(json_dict)


if __name__ == '__main__':

    db_path = os.path.join(DB_DIR, "default_thingistat.db")
    thing_ids_list = list(np.load(os.path.join(DB_DIR, "default_ids_list.npy")))

    if os.path.isfile(db_path):
        db = ThingDB(db_path)
        last_thing_id = db.get_last_thing_id()

    else:
        last_thing_id = int(thing_ids_list[0])

    print("last thing id", last_thing_id)
    thing_download_sweep(last_thing_id, thing_ids_list, 1, 'default_thingistat.db')
