import json
import requests

from ..models import CKANResource, CKANInstance

def get_ckan_info(ckan_field):

    ckan_resource = CKANResource.objects.get(pk=ckan_field.ckan_resource_id)
    ckan_instance = CKANInstance.objects.get(pk=ckan_resource.ckan_instance_id)
    return ckan_resource, ckan_instance


def get_ckan_data(ckan_field):
    ckan_resource, ckan_instance = get_ckan_info(ckan_field)

    url = ckan_instance.url + "/api/action/datastore_search"
    params = {'resource_id': ckan_resource.resource_id}
    response = requests.request("GET", url, params=params)
    return (json.loads(response.text)['result']['records'])