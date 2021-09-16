from constructs import Construct
from cdk8s import App, Chart

from imports import k8s
from imports import imagepolicy
from imports import imagerepository

from handler import Yamldata

config = Yamldata(file_path='config.yaml')
services = config.return_data().keys()


class AppChart(Chart):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        for service in services:
            label = {'app': f'{service}'}

            k8s.ServiceAccount(
                self, f'{service}-serviceaccount',
                metadata=k8s.ObjectMeta(
                    name=f'{service}'
                )
            )

            k8s.Service(
                self, f'{service}-service',
                metadata=k8s.ObjectMeta(
                    name=f'{service}'
                ),
                spec=k8s.ServiceSpec(
                    type='ClusterIP',
                    ports=[
                        k8s.ServicePort(
                            name='http',
                            port=8080,
                            protocol='TCP',
                            target_port=k8s.IntOrString.from_number(8080)
                        )
                    ],
                    selector=label
                )
            )

            k8s.Deployment(
                self, f'{service}-deployment',
                metadata=k8s.ObjectMeta(
                    name=f'{service}'
                ),
                spec=k8s.DeploymentSpec(
                    replicas=2,
                    selector=k8s.LabelSelector(
                        match_labels=label
                    ),
                    template=k8s.PodTemplateSpec(
                        metadata=k8s.ObjectMeta(
                            labels=label
                        ),
                        spec=k8s.PodSpec(
                            service_account_name=f'{service}',
                            image_pull_secrets=[
                                k8s.LocalObjectReference(
                                    name='registry-intl.cn-hongkong.aliyuncs.com'
                                ),
                            ],
                            restart_policy='Always',
                            volumes=[
                                k8s.Volume(
                                    name='socker-volume',
                                    empty_dir=k8s.EmptyDirVolumeSource(
                                        size_limit=k8s.Quantity.from_string(
                                            '100M')
                                    )
                                )
                            ],
                            containers=[
                                k8s.Container(
                                    name=f'{service}',
                                    image=str(config.return_service_component(service_name=f'{service}',
                                                                              component_name='image')),
                                    image_pull_policy='Always',
                                    ports=[
                                        k8s.ContainerPort(
                                            container_port=8080
                                        )
                                    ],
                                    env=[
                                        k8s.EnvVar(
                                            name='datacenterId',
                                            value='12factor'
                                        ),
                                        k8s.EnvVar(
                                            name='terminationTimeout',
                                            value='30'
                                        ),
                                        k8s.EnvVar(
                                            name='ASPNETCORE_ENVIRONMENT',
                                            value='production'
                                        ),
                                        k8s.EnvVar(
                                            name='TRACING_ENABLED',
                                            value='true'
                                        ),
                                        k8s.EnvVar(
                                            name='TRACING_CONNECTION_STRING',
                                            value='http://opentelemetry-collector.open-telemetry:4317'
                                        ),
                                        k8s.EnvVar(
                                            name='TRACING_EXPORT_TIMEOUT',
                                            value='1000'
                                        ),
                                    ],
                                    env_from=[
                                        k8s.EnvFromSource(
                                            secret_ref=k8s.SecretEnvSource(
                                                name='covergo=database'
                                            )
                                        )
                                    ],
                                    resources=k8s.ResourceRequirements(
                                        requests={
                                            'cpu': k8s.Quantity.from_string(config.return_service_component(service_name=service,
                                                                                                            component_name='resources')['requests']['cpu']),
                                            'memory': k8s.Quantity.from_string(config.return_service_component(service_name=service,
                                                                                                               component_name='resources')['requests']['memory'])
                                        },
                                        limits={
                                            'cpu': k8s.Quantity.from_string(config.return_service_component(service_name=service,
                                                                                                            component_name='resources')['limits']['cpu']),
                                            'memory': k8s.Quantity.from_string(config.return_service_component(service_name=service,
                                                                                                               component_name='resources')['limits']['memory'])
                                        }
                                    ),
                                    readiness_probe=k8s.Probe(
                                        http_get=k8s.HttpGetAction(
                                            port=k8s.IntOrString.from_string(
                                                '8080'
                                            ),
                                            path='/readyz'
                                        )
                                    ),
                                    liveness_probe=k8s.Probe(
                                        http_get=k8s.HttpGetAction(
                                            port=k8s.IntOrString.from_string(
                                                '8080'
                                            ),
                                            path='/healthz'
                                        )
                                    ),
                                    volume_mounts=[
                                        k8s.VolumeMount(
                                            name='socker-volume',
                                            mount_path='/tmp'
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                )
            )
            if service == 'covergo-gateway':
                k8s.Ingress(
                    self, f'{service}-ingress',
                    metadata=k8s.ObjectMeta(
                        name=f'{service}'
                    ),
                    spec=k8s.IngressSpec(
                        backend=k8s.IngressBackend(
                            service_name=f'{service}',
                            service_port=k8s.IntOrString.from_string('8080')
                        ),
                        rules=[
                            k8s.IngressRule(
                                host=str(config.return_service_component(
                                    service_name=service, component_name='ingress')['host']),
                                http=k8s.HttpIngressRuleValue(
                                    paths=[
                                        k8s.HttpIngressPath(
                                            backend=k8s.IngressBackend(
                                                service_name='covergo-gateway',
                                                service_port=k8s.IntOrString.from_string(
                                                    '8080')
                                            ),
                                            path='/'
                                        )
                                    ]
                                )
                            )
                        ],
                        tls=[
                            k8s.IngressTls(
                                hosts=[
                                    str(config.return_service_component(
                                        service_name=service, component_name='ingress')['host'])
                                ],
                                secret_name=str(config.return_service_component(
                                    service_name=service, component_name='ingress')['host']).replace(
                                    '.', '-') + '-cert'
                            )
                        ]
                    )
                )
