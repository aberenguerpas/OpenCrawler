import requests
import utils
import time
import traceback
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class ZenodoCrawler(interface):
    
    def __init__(self, domain):
        self.domain = domain
        
        # Read token
        token = utils.read_token()['zenodo_token']
        if token == "None" or not token:
            token = None
        self.token = token

    def get_package_list(self):
        """Get all the packages ids"""
        skip = 1
        ids = []
        fin = False
        while not fin:
            response = requests.get('https://zenodo.org/api/records/?type=dataset&size=200&page='+str(skip)+'&access_token='+str(self.token))
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
                # Timer start counting
                utils.timer_start()
                
                meta_json = response.json()

                metadata = dict()
                
                if meta_json.get('files', None) is not None:
                    url = meta_json.get('files', None)[0]
                    mediaType = url.get('type', None)
                
                    if mediaType == "csv" or mediaType == "zip" or mediaType == "excel":
                        
                        metadata['identifier'] = id
                        
                        meta = meta_json.get('metadata', None)
                        
                        if meta is not None:
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
                        metadata['modified'] = meta.get('publication_date', None)
                        #metadata['license'] = requests.get('https://zenodo.org/api/licenses/')
                        metadata['license'] = None
                        metadata['source'] = self.domain
                        
                        return metadata
                    else:
                        # No es tipo csv, zip o excel
                        print('Buscando siguiente id...')
                        cont = 1
                        next_id = ''
                        for x in craw.get_package_list():
                            if id == craw.get_package_list()[cont-1]:
                                next_id = craw.get_package_list()[cont]
                                print('Siguiente id encontrada: ' + str(next_id))
                            cont = cont + 1
                        return(self.get_package(next_id))
                else:
                    return('files es none')
            else:
                # Timer stops when it can't make any more calls to the API
                rest = utils.timer_stop()
                if rest < 60:
                    time.sleep(60 - rest)
                    return (self.get_package(id))
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None
        
craw = ZenodoCrawler('https://zenodo.org')

for id in craw.get_package_list():
    print(craw.get_package(id))