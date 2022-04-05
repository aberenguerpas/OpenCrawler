import requests
import traceback
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class datosGobEsCrawler(interface):
    def __init__(self, domain, data_types):
        self.domain = domain
        self.data_types = data_types

    def get_package_list(self):
        """Get all the packages ids"""
        skip = 0
        ids = []
        fin = False

        while not fin:
            response = requests.get('https://datos.gob.es/apidata/catalog/dataset?_sort=title&_pageSize=200&_page='+str(skip))
            if response.status_code == 200:
                packages = response.json()['result']['items']
                if len(packages) > 0:
                    skip += 1
                    for p in packages:
                        ids.append(p['_about'].split("/")[-1])
                else:
                    fin = True
            else:
                fin = True

        return ids

    def add_source(self, meta):
        aux = dict()

        aux['name'] = meta['title'][0]['_value']
        aux['downloadUrl'] = meta.get('accessURL', None)
        aux['mediaType'] = meta['format']['value']

        return aux

    def get_package(self, id):
        # Obtain a package with all their metadata
        try:
            url = "https://datos.gob.es/apidata/catalog/dataset/" + id
            response = requests.get(url)

            if response.status_code == 200:
                meta = response.json()['result']['items'][0]

                metadata = dict()

                metadata['identifier'] = id
                metadata['title'] = meta['title'][0]['_value']
                metadata['description'] = meta['description'][0]['_value']

                if not isinstance(meta['theme'], list):
                    metadata['theme'] = meta.get('theme', None).split('/')[-1]
                else:
                    metadata['theme'] = [m.split('/')[-1] for m in meta['theme']]
                
                resource_list = []

                if not isinstance(meta['distribution'], list):
                    meta['distribution'] = [meta['distribution']]

                for res in meta['distribution']:
                    if self.data_types:
                        for t in self.data_types:
                            if t in res['format']['value'].lower():
                                aux = self.add_source(res)
                                resource_list.append(aux)
                    else:
                        aux = self.add_source(res)
                        resource_list.append(aux)

                metadata['resources'] = resource_list
                metadata['modified'] = meta.get('modified', None)
                metadata['license'] = meta.get('license', None)
                metadata['source'] = self.domain

                return metadata
            else:
                return None

        except Exception as e:
            print(traceback.format_exc())
            logger.error(e)
            return None
