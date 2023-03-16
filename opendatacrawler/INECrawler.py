import requests
import utils
import json
import numpy as np
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class INECrawler(interface):
    
    def __init__(self, domain, path):
        self.domain = domain
        self.path = path
        self.tourism_operations = [61, 62, 63, 132, 180, 238, 239, 240, 241, 328, 329, 330, 334]
        
    def get_package_list(self):
        """Get all the operations ids"""
        total_ids = []
        response = requests.get(self.domain + '/wstempus/js/ES/OPERACIONES_DISPONIBLES')
        if response.status_code == 200:
            operations = response.json()
            if len(operations) > 0:
                for p in operations:
                    total_ids.append(p['Id'])
        return total_ids
    
    def get_package(self, id):
        """Build a dict of elements metadata"""
        # operation_id = id
        operation_name = utils.get_operation_name(id)

        try:
            response = requests.get('https://servicios.ine.es/wstempus/js/ES/TABLAS_OPERACION/' + str(id))
            if response.status_code == 200:
                meta = response.json()
                
                if len(meta) > 0:
                    packages = []
                    for x in meta:
                        metadata = dict()
                        
                        table_id = str(x.get('Id', None))
                        metadata['identifier'] = str(id) + '_' + table_id
                        metadata['title'] = x.get('Nombre', None)
                        metadata['description'] = operation_name + ': ' + x.get('Nombre', None)
                        
                        if id in self.tourism_operations:
                            metadata['theme'] = 'Turismo'
                        else:
                            metadata['theme'] = None
                        
                        aux = dict()
                        aux['name'] = 'Datos tabla: ' + metadata['title']
                        aux['downloadUrl'] = 'https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/' + table_id + '.csv?nocab=1'
                        aux['mediaType'] = 'csv'
                        
                        metadata['resources'] = [aux]
                        metadata['modified'] = x.get('Ultima_Modificacion')
                        metadata['license'] = 'INE License'
                        metadata['source'] = self.domain
                        
                        logger.info('Actual Metadata:')
                        logger.info(metadata)
                        packages.append(metadata)
                
                # Saving all meta in a json file        
                utils.save_all_metadata(id, meta, self.path)
                
                logger.info(packages)        
                return packages
              
            else:
                return None
        except Exception as e:
            logger.info(e)
            return None