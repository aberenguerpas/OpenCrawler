import configparser
from w3lib.url import url_query_cleaner
from url_normalize import url_normalize
import os
import pathlib
import time


def clean_url(u):
    """Clean a url string to obtain the mainly domain without protocols."""

    u = url_normalize(u)
    parameters = ['utm_source',
                  'utm_medium',
                  'utm_campaign',
                  'utm_term',
                  'utm_content']

    u = url_query_cleaner(u, parameterlist=parameters,
                          remove=True)

    if u.startswith("http://"):
        u = u[7:]
    if u.startswith("https://"):
        u = u[8:]
    if u.startswith("www."):
        u = u[4:]
    if u.endswith("/"):
        u = u[:-1]
    return u.split('/')[0]


def extract_tags(tags):
    """ Extract the tag names from tag list"""
    return [tag['display_name'] for tag in tags]

def extract_keywords(keywords):
    """ Extract the keywords from keyword list"""
    if len(keywords) > 0:
        theme = keywords.split(", ")
        return theme
    else:
        return None


def read_config():
    d = dict()

    config = configparser.ConfigParser()

    current_path = pathlib.Path(__file__).parent.resolve()
    config.read(str(current_path) + '/config.ini')

    d['soda_token'] = config['Soda']['token']

    return d

def read_token():
    d = dict()

    config = configparser.ConfigParser()

    current_path = pathlib.Path(__file__).parent.resolve()
    config.read(str(current_path) + '/config.ini')

    d['zenodo_token'] = config['Zenodo']['token']

    return d


def check_url(url):
    """ Check if exist a well-formed url"""
    if url[:8] == "https://" or url[:7] == "http://":
        return True
    else:
        return False


def lower_list(li):
    """ Convert all element of a list to lowercase"""
    if li:
        return [x.lower() for x in li]
    else:
        return None


def create_folder(path):
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the dir %s failed" % path)
            return False
        else:
            print("Successfully created the dir %s " % path)
            return True
    else:
        return True


def print_intro():

    """ Print the content inside intro.txt"""
    path = os.path.dirname(os.path.abspath(__file__))
    f = open(path + "/intro.txt", "r")
    for x in f:
        print(x, end='')


def load_resume_id(path):
    try:
        f = open(path, "r")
        return f.read()

    except Exception:
        return None


def save_resume_id(path, id):
    f = open(path, "w")
    f.write(id)
    f.close()


def remove_resume_id(path):

    if os.path.exists(path):
        os.remove(path)
