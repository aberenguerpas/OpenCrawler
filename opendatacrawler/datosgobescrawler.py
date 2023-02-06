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

        ids = []

        url = 'http://datos.gob.es/virtuoso/sparql'

        params = {
            'query': 'select distinct ?dataset where{?dataset a <http://www.w3.org/ns/dcat#Dataset>}'
        }
        header = {
            'Accept': 'application/sparql-results+json'
        }
        res = requests.get(url, params=params, headers=header)

        for dataset in res.json()['results']['bindings']:
            ids.append(dataset['dataset']['value'].split("/")[-1])


        return ids

    def add_source(self, meta):
        aux = dict()

        aux['name'] = meta.get('title', None)
        if aux['name'] is not None:
            aux['name'] = meta['title'][0]['_value']
        aux['downloadUrl'] = meta.get('accessURL', None)
        if aux['downloadUrl'] is None:
              aux['downloadUrl'] = meta.get('accessURL', None)
        aux['mediaType'] = meta['format']['value']
        aux['size'] = meta.get('byteSize', None)
        
        return aux

    def get_package(self, id):
        # Obtain a package with all their metadata
        try:
            url = "https://datos.gob.es/apidata/catalog/dataset/" + id
            response = requests.get(url)

            if response.status_code == 200:
                meta = response.json()['result']['items'][0]

                print(meta)

                metadata = dict()

                metadata['identifier'] = id
                metadata['img'] = 'https://avatars.githubusercontent.com/u/102170496?s=200&v=4'
                metadata['title'] = meta['title'][0]['_value']

                if len(meta['title'])>1:
                    for t in meta['title']:
                        if t['_lang']=='es':
                            metadata['title'] = t['_value']

                metadata['description'] = meta['description'][0]['_value']
                if len(meta['description'])>1:
                    for t in meta['description']:
                        if t['_lang']=='es':
                            metadata['description'] = t['_value']

               

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
                metadata['issued'] = meta.get('issued', None)
                metadata['license'] = meta.get('license', None)
                metadata['source'] = self.domain

                metadata['temporal'] = dict()
                if meta.get('temporal', None) is not None:
                    if 'startDate' in meta['temporal']:
                        metadata['temporal']['startDate'] = meta['temporal']['startDate']
                    else:
                        metadata['temporal']['startDate'] = None

                    if 'endDate' in meta['temporal']:
                        metadata['temporal']['endDate'] = meta['temporal']['endDate']
                    else:
                        metadata['temporal']['endtDate'] = None
                else:
                    metadata['temporal']['startDate'] = None
                    metadata['temporal']['endDate'] = None

                if meta.get('spatial', None) is not None:
                    if type(meta['spatial']) is list:
                        metadata['geo'] = [place.split("/")[-1:][0] for place in meta['spatial']]
                    else:
                        metadata['geo'] = meta['spatial'].split("/")[-1:]
                else:
                    metadata['geo'] = None

                return metadata
            else:
                return None

        except Exception as e:
            print(meta)
            print(traceback.format_exc())
            logger.error(e)
            return None
