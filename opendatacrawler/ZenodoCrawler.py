import requests
import utils
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class ZenodoCrawler(interface):
    
    def __init__(self, domain, data_types):
        self.domain = domain
        self.data_types = data_types        

    def get_package_list(self):
        """Get all the packages ids"""
        skip = 1
        ids = []
        fin = False
        while not fin:
            response = requests.get('https://zenodo.org/api/records/?size=100&page='+str(skip))
            if response.status_code == 200:
                packages = response.json()['hits']['hits']
                if len(packages) > 0:
                    skip += 1
                    for p in packages:
                        ids.append(p['id'])
                else:
                    fin = True
            else:
                fin = True

        return ids

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get('https://zenodo.org/api/records/' + id)
        except Exception as e:
            logger.info(e)

        if response.status_code == 200:
            meta = response.json()

            metadata = dict()

            metadata['identifier'] = id
            aux_grants = meta.get('metadata', None).get('grants', None)[0]
            metadata['title'] = aux_grants.get('title', None)
            metadata['description'] = meta.get('metadata', None).get('description', None)
            metadata['theme'] = utils.extract_tags(meta.get('metadata', None).get('keywords', None))

            resource_list = []

            aux = dict()

            url = meta.meta.get('files', None)[0]
            aux['downloadUrl'] = url.get('links', None).get('self', None)
            aux['mediaType'] = url.get('type', None)

            resource_list.append(aux)

            metadata['resources'] = resource_list
            metadata['modified'] = meta.get('update', None)
            #metadata['license'] = requests.get('https://zenodo.org/api/licenses/')
            metadata['source'] = self.domain

            return metadata
        else:
            return None