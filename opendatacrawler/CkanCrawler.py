import requests
import utils
from setup_logger import logger
from opendatacrawlerInterface import OpenDataCrawlerInterface as interface


class CkanCrawler(interface):

    def __init__(self, domain, data_types):
        self.domain = domain
        self.data_types = data_types

    def get_package_list(self):

        # Make a request to CKAN API to obtain the package list
        response = requests.get(self.domain+"/api/3/action/package_list")

        # Check if in the previous call there is a redirect
        # in this case, is used the package_searach endpoint
        if len(response.history) > 0:

            total = -1
            offset = 0
            packages = []

            # Iterate over the endpoint with the max of 1000 results until the end
            # and save the packages id on a list
            while total != len(packages):

                # Build query url
                url = "/api/3/action/package_search?rows=1000&start="
                url += str(offset)

                try:
                    response = requests.get(self.domain + url)
                except Exception as e:
                    logger.error(e)

                if response.status_code == 200:
                    response = response.json()['result']
                    for r in response['results']:
                        packages.append(r['id'])

                    total = response['count']
                    offset += 1000
                else:
                    break
            return packages

        elif response.status_code == 200:
            packages = response.json()['result']
            return packages
        else:
            return []

    def get_package(self, id):

        # Obtain a package with all their metadata
        try:
            url = self.domain + "/api/3/action/package_show?id=" + id
            response = requests.get(url)
    
            if response.status_code == 200:
                meta = response.json()['result']

                metadata = dict()

                metadata['identifier'] = id
                metadata['title'] = meta.get('title', None)
                metadata['description'] = meta.get('notes', None)
                metadata['theme'] = meta.get('category', None)

                if metadata['theme'] is None:
                    metadata['theme'] = utils.extract_tags(meta.get('tags', None))

                resource_list = []
                for res in meta['resources']:
                    if (self.data_types is None or
                    res['format'].lower() in self.data_types):
                        aux = dict()
                        aux['name'] = res.get('name', None)
                        aux['downloadUrl'] = res.get('url', None)
                        aux['mediaType'] = res['format'].lower()
                        id = res.get('url', None).split("/")[-1].split(".")[0]
                        resource_list.append(aux)

                metadata['resources'] = resource_list
                metadata['modified'] = meta.get('metadata_modified', None)
                metadata['license'] = meta.get('license_title', None)
                metadata['source'] = self.domain

                return metadata
            else:
                return None

        except Exception as e:
            logger.error(e)
            return None
