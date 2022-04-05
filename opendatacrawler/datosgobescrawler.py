from pickle import TRUE
import requests
import utils
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
                    print(skip)
                    for p in packages:
                        ids.append(p['_about'].split("/")[-1])
                else:
                    fin = True
            else:
                fin = True

        return ids

    def get_package(self, id):
    # Obtain a package with all their metadata
        try:
            url = "https://datos.gob.es/apidata/catalog/dataset/" + id
            response = requests.get(url)

            if response.status_code == 200:
                meta = response.json()['result']['items'][0]

                metadata = dict()

                metadata['identifier'] = meta['identifier']
                metadata['title'] = meta['title'][0]['_value']
                metadata['description'] = meta['description'][0]['_value']
                metadata['theme'] = meta['theme'].split("/")[-1]

                resource_list = []
                for res in meta['distribution']:
                    if (self.data_types is None or
                    res['format']['value'].lower() in self.data_types):
                        aux = dict()
                        aux['name'] = res['title']['_value']
                        aux['downloadUrl'] = res.get('accessURL', None)
                        aux['mediaType'] = res['format']['value']
                        resource_list.append(aux)

                metadata['resources'] = resource_list
                metadata['modified'] = meta['modified']
                metadata['license'] = meta['license']
                metadata['source'] = self.domain

                return metadata
            else:
                return None

        except Exception as e:
            logger.error(e)
            return None
