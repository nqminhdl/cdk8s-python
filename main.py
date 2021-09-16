#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart

from k8s import AppChart
from kustomization import Kustomization

from handler import Yamldata

config = Yamldata(file_path='config.yaml')
services = config.return_data().keys()

ns = 'cdk8s-python'
app = App()
AppChart(app, ns=ns)
app.synth()

manifest = Kustomization(ns=ns, yaml_data_object=config)
for service in services:
    manifest.output_app_yaml(
        service_name=service,
        ns=ns,
        app_path='shared/app'
    )
