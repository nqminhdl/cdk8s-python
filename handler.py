#!/usr/bin/env python
import yaml
from yaml.loader import Loader
from pathlib import Path
from os import listdir


class Yamldata():
    def __init__(self, file_path):
        self.data = yaml.safe_load(open(file_path))

    def return_data(self):
        return self.data

    def return_service_name(self, service_name):
        return self.data.get(service_name)

    def return_service_component(self, service_name, component_name):
        return self.return_service_name(service_name).get(component_name)

    def return_generate_manifest(self, service_name, dist_file_path, generated_file_path):
        generated_data = list(yaml.load_all(
            open(dist_file_path), Loader=yaml.SafeLoader))
        for i in generated_data:
            if service_name in i['metadata']['name']:
                Path(
                    f"./dist/{generated_file_path}/{service_name}").mkdir(parents=True, exist_ok=True)
                kind = i['kind'].lower()
                file_name = f'./dist/{generated_file_path}/{service_name}/{kind}.yaml'
                with open(file_name, "w") as file:
                    yaml.dump(i, file)

        kustomization_template = {"apiVersion": "kustomize.config.k8s.io/v1beta1", "kind": "Kustomization",
                                  "resources": [""]}
        kustomization_template['resources'] = listdir(
            path=f'./dist/{generated_file_path}/{service_name}')
        with open(f'./dist/{generated_file_path}/{service_name}/kustomization.yaml', 'w') as file:
            yaml.dump(kustomization_template, file)
