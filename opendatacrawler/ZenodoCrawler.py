import requests
import utils
import zenodopy
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class ZenodoCrawler(interface):
    
    def __init__(self, domain):
        self.domain = domain
        
        # Read token
        token = utils.read_token()['zenodo_token']
        if token == "None" or not token:
            token = None

    def get_package_list(self):
        """Get all the packages ids"""
        skip = 1
        ids = []
        fin = False
        while not fin:
            response = requests.get('https://zenodo.org/api/records/?size=200&page='+str(skip))
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
            response = requests.get('https://zenodo.org/api/records/' + str(id))
            
            if response.status_code == 200:
                meta_json = response.json()

                metadata = dict()
                
                metadata['identifier'] = id
                
                meta = meta_json.get('metadata', None)
                
                if meta is not None:
                    grants = meta.get('grants', None)
                    # 'Title' sometimes is in 'grants'->'title' but it also can be just in 'title'
                    if grants is not None:
                        metadata['title'] = grants[0].get('title', None)
                    else:
                        metadata['title'] = meta.get('title', None)
                    metadata['description'] = meta.get('description', None)
                    if meta.get('keywords', None) is not None:
                        metadata['theme'] = utils.extract_keywords(meta.get('keywords', None)[0])
                
                resource_list = []

                aux = dict()

                if meta_json.get('files', None) is not None:
                    url = meta_json.get('files', None)[0]
                    aux['downloadUrl'] = url.get('links', None).get('self', None)
                    aux['mediaType'] = url.get('type', None)

                resource_list.append(aux)

                metadata['resources'] = resource_list
                metadata['modified'] = meta_json.get('updated', None)
                #metadata['license'] = requests.get('https://zenodo.org/api/licenses/')
                metadata['license'] = None
                metadata['source'] = self.domain
                
                return metadata
            else:
                return None
        except Exception as e:
            logger.info(e)
            return None

craw = ZenodoCrawler('https://zenodo.org')

for id in craw.get_package_list():
    print(craw.get_package(id))