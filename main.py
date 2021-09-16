#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart

from k8s import AppChart, ImageRepositoryChart, ImagePoliciesChart
from kustomization import Kustomization

from handler import Yamldata

config = Yamldata(file_path='config.yaml')
services = config.return_data().keys()

ns = 'cdk8s-python'
manifest = Kustomization(ns=ns, yaml_data_object=config)

""" Generate app manifests """
app = App()
AppChart(app, ns=ns)
app.synth()

for service in services:
    manifest.output_app_yaml(
        service_name=service,
        ns=ns,
        app_path='shared/app',
        kustomization=True
    )

""" Generate image repository manifests """
repository = App()
ImageRepositoryChart(repository, ns=ns)
repository.synth()

for service in services:
    manifest.output_app_yaml(
        service_name=service,
        ns=ns,
        app_path='shared/registries',
        kustomization=False
    )

""" Generate image policy manifests """
policy = App()
ImagePoliciesChart(policy, ns=ns)
policy.synth()

for service in services:
    manifest.output_app_yaml(
        service_name=service,
        ns=ns,
        app_path='shared/polices',
        kustomization=False
    )
