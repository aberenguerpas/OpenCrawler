import requests
import utils
import json
import traceback
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class OpenDataSoftCrawler(interface):
    
    def __init__(self, domain):
        self.domain = domain

    def get_package_list(self):
        """Get all the packages ids"""
        try:
            total_ids = []
            response = requests.get(self.domain + '/api/v2/catalog/datasets?limit=100&lang=es&timezone=UTC')
            if response.status_code == 200:
                data = response.json()
                datasets = data['datasets']
                    
                for p in datasets:
                    id = p['dataset'].get('dataset_id', None)
                    total_ids.append(id)
            return total_ids
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None

    def get_package(self, id):
        """Build a dict of package metadata"""
        try:
            response = requests.get(self.domain + '/api/v2/catalog/datasets/' + str(id) + '/records?limit=100&lang=es&timezone=UTC')
            
            if response.status_code == 200:                
                meta_json = response.json()
                
                metadata = dict()
                
                metadata['identifier'] = id
                
                meta = meta_json['records']
                
                if meta is not None:
                    for p in meta:
                        print(p['record'].get('id', None))
                # Saving all meta in a json file
                try:
                    path = 'C:\\Users\\Usuario\\Desktop\\Crawler2.0\\OpenDataCrawler\\opendatacrawler\\prueba'
                    with open(path + "/all_" + str(metadata['identifier']) + '.json',
                            'w', encoding='utf-8') as f:
                        json.dump(meta_json, f, ensure_ascii=False, indent=4)
                except Exception as e:
                    logger.error('Error saving metadata  %s',
                                path + "/all_" + metadata['identifier'] + '.json')
                    logger.error(e)
                return metadata
            else:
                return None
        except Exception as e:
            print(traceback.format_exc())
            logger.info(e)
            return None
        
craw = OpenDataSoftCrawler('https://datosabiertos.dipcas.es')
for id in craw.get_package_list():
    print(craw.get_package(id))