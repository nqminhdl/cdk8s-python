#!/usr/bin/env python
import yaml
from yaml.loader import Loader


class Yamldata():
    def __init__(self, file_path):
        self.data = yaml.safe_load(open(file_path))

    def return_data(self):
        return self.data

    def return_service_name(self, service_name):
        return self.data.get(service_name)

    def return_service_component(self, service_name, component_name):
        return self.return_service_name(service_name).get(component_name)
