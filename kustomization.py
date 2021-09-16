class Kustomization():
    def __init__(self, ns, yaml_data_object):
        self.ns = ns
        self.yaml_data_object = yaml_data_object

    def output_app_yaml(self, service_name, ns, app_path):
        self.yaml_data_object.return_generate_manifest(
            service_name,
            dist_file_path=f'./dist/{self.ns}.k8s.yaml',
            generated_file_path=f'{app_path}'
        )
