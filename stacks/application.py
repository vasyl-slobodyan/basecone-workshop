from constructs import Construct
from aws_cdk import Stack
import aws_cdk.aws_eks as eks
import aws_cdk.aws_iam as iam


class Application(Stack):
    def __init__(self, scope=Construct, construct_id=str, _cluster=eks.Cluster, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        eks_cluster = eks.Cluster.from_cluster_attributes(
            self, "cluster",
            cluster_name=_cluster.cluster_name,
            open_id_connect_provider=iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
                self, "{}-oidcProvider".format(construct_id),
                open_id_connect_provider_arn=_cluster.open_id_connect_provider.open_id_connect_provider_arn
            ),
            kubectl_role_arn=_cluster.kubectl_role.role_arn,
            kubectl_security_group_id=_cluster.cluster_security_group_id,
        )

        redis_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "namespace": "yelb",
                "name": "redis-server",
                "labels": {
                    "app": "redis-server",
                    "tier": "cache"
                }
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [
                    {
                        "port": 6379
                    }
                ],
                "selector": {
                    "app": "redis-server",
                    "tier": "cache"
                }
            }
        }

        db_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-db",
                "labels": {
                    "app": "yelb-db",
                    "tier": "backenddb"
                }
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [
                    {
                        "port": 5432
                    }
                ],
                "selector": {
                    "app": "yelb-db",
                    "tier": "backenddb"
                }
            }
        }

        app_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-appserver",
                "labels": {
                    "app": "yelb-appserver",
                    "tier": "middletier"
                }
            },
            "spec": {
                "type": "ClusterIP",
                "ports": [
                    {
                        "port": 4567
                    }
                ],
                "selector": {
                    "app": "yelb-appserver",
                    "tier": "middletier"
                }
            }
        }

        ui_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-ui",
                "labels": {
                    "app": "yelb-ui",
                    "tier": "frontend"
                }
            },
            "spec": {
                "type": "LoadBalancer",
                "ports": [
                    {
                        "port": 80,
                        "protocol": "TCP",
                        "targetPort": 80
                    }
                ],
                "selector": {
                    "app": "yelb-ui",
                    "tier": "frontend"
                }
            }
        }

        ui_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-ui"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "yelb-ui",
                        "tier": "frontend"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "yelb-ui",
                            "tier": "frontend"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "yelb-ui",
                                "image": "mreferre/yelb-ui:0.7",
                                "ports": [
                                    {
                                        "containerPort": 80
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "namespace": "yelb",
                "name": "redis-server"
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "redis-server",
                        "tier": "cache"
                    }
                },
                "replicas": 1,
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "redis-server",
                            "tier": "cache"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "redis-server",
                                "image": "redis:4.0.2",
                                "ports": [
                                    {
                                        "containerPort": 6379
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        db_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-db"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "yelb-db",
                        "tier": "backenddb"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "yelb-db",
                            "tier": "backenddb"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "yelb-db",
                                "image": "mreferre/yelb-db:0.5",
                                "ports": [
                                    {
                                        "containerPort": 5432
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        app_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-appserver"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "yelb-appserver",
                        "tier": "middletier"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "yelb-appserver",
                            "tier": "middletier"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "yelb-appserver",
                                "image": "mreferre/yelb-appserver:0.5",
                                "ports": [
                                    {
                                        "containerPort": 4567
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }

        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "yelb",
                "labels": {
                    "mesh": "yelb",
                    "appmesh.k8s.aws/sidecarInjectorWebhook": "enabled"
                }
            }
        }

        namespace = eks_cluster.add_manifest("namespace",
                                             namespace)

        application = eks_cluster.add_manifest("yelb", redis_deployment, redis_service, db_deployment, db_service,
                                               app_deployment, app_service, ui_deployment, ui_service)

        application.node.add_dependency(namespace)
