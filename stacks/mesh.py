from constructs import Construct
from aws_cdk import Stack
import aws_cdk.aws_eks as eks
import aws_cdk.aws_iam as iam


class Mesh(Stack):
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

        mesh = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "Mesh",
            "metadata": {
                "name": "yelb"
            },
            "spec": {
                "namespaceSelector": {
                    "matchLabels": {
                        "mesh": "yelb"
                    }
                }
            }
        }

        redis_virtual_node = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualNode",
            "metadata": {
                "name": "redis-server",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "redis-server-virtual-node",
                "podSelector": {
                    "matchLabels": {
                        "app": "redis-server"
                    }
                },
                "listeners": [
                    {
                        "portMapping": {
                            "port": 6379,
                            "protocol": "tcp"
                        }
                    }
                ],
                "serviceDiscovery": {
                    "dns": {
                        "hostname": "redis-server.yelb.svc.cluster.local"
                    }
                }
            }
        }

        redis_virtual_service = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualService",
            "metadata": {
                "name": "redis-server",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "redis-server",
                "provider": {
                    "virtualNode": {
                        "virtualNodeRef": {
                            "name": "redis-server"
                        }
                    }
                }
            }
        }

        db_virtual_node = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualNode",
            "metadata": {
                "name": "yelb-db",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-db-virtual-node",
                "podSelector": {
                    "matchLabels": {
                        "app": "yelb-db"
                    }
                },
                "listeners": [
                    {
                        "portMapping": {
                            "port": 5432,
                            "protocol": "tcp"
                        }
                    }
                ],
                "serviceDiscovery": {
                    "dns": {
                        "hostname": "yelb-db.yelb.svc.cluster.local"
                    }
                }
            }
        }

        db_virtual_service = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualService",
            "metadata": {
                "name": "yelb-db",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-db",
                "provider": {
                    "virtualNode": {
                        "virtualNodeRef": {
                            "name": "yelb-db"
                        }
                    }
                }
            }
        }

        app_virtual_node = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualNode",
            "metadata": {
                "name": "yelb-appserver",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-appserver-virtual-node",
                "podSelector": {
                    "matchLabels": {
                        "app": "yelb-appserver"
                    }
                },
                "listeners": [
                    {
                        "portMapping": {
                            "port": 4567,
                            "protocol": "http"
                        }
                    }
                ],
                "serviceDiscovery": {
                    "dns": {
                        "hostname": "yelb-appserver.yelb.svc.cluster.local"
                    }
                },
                "backends": [
                    {
                        "virtualService": {
                            "virtualServiceRef": {
                                "name": "yelb-db"
                            }
                        }
                    },
                    {
                        "virtualService": {
                            "virtualServiceRef": {
                                "name": "redis-server"
                            }
                        }
                    }
                ]
            }
        }

        app_virtual_router = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualRouter",
            "metadata": {
                "namespace": "yelb",
                "name": "yelb-appserver"
            },
            "spec": {
                "awsName": "yelb-appserver-virtual-router",
                "listeners": [
                    {
                        "portMapping": {
                            "port": 4567,
                            "protocol": "http"
                        }
                    }
                ],
                "routes": [
                    {
                        "name": "route-to-yelb-appserver",
                        "httpRoute": {
                            "match": {
                                "prefix": "/"
                            },
                            "action": {
                                "weightedTargets": [
                                    {
                                        "virtualNodeRef": {
                                            "name": "yelb-appserver"
                                        },
                                        "weight": 1
                                    }
                                ]
                            },
                            "retryPolicy": {
                                "maxRetries": 2,
                                "perRetryTimeout": {
                                    "unit": "ms",
                                    "value": 2000
                                },
                                "httpRetryEvents": [
                                    "server-error",
                                    "client-error",
                                    "gateway-error"
                                ]
                            }
                        }
                    }
                ]
            }
        }

        app_virtual_service = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualService",
            "metadata": {
                "name": "yelb-appserver",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-appserver",
                "provider": {
                    "virtualRouter": {
                        "virtualRouterRef": {
                            "name": "yelb-appserver"
                        }
                    }
                }
            }
        }

        ui_virtual_node = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualNode",
            "metadata": {
                "name": "yelb-ui",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-ui-virtual-node",
                "podSelector": {
                    "matchLabels": {
                        "app": "yelb-ui"
                    }
                },
                "listeners": [
                    {
                        "portMapping": {
                            "port": 80,
                            "protocol": "http"
                        }
                    }
                ],
                "serviceDiscovery": {
                    "dns": {
                        "hostname": "yelb-ui.yelb.svc.cluster.local"
                    }
                },
                "backends": [
                    {
                        "virtualService": {
                            "virtualServiceRef": {
                                "name": "yelb-appserver"
                            }
                        }
                    }
                ]
            }
        }

        ui_virtual_service = {
            "apiVersion": "appmesh.k8s.aws/v1beta2",
            "kind": "VirtualService",
            "metadata": {
                "name": "yelb-ui",
                "namespace": "yelb"
            },
            "spec": {
                "awsName": "yelb-ui",
                "provider": {
                    "virtualNode": {
                        "virtualNodeRef": {
                            "name": "yelb-ui"
                        }
                    }
                }
            }
        }

        mesh = eks_cluster.add_manifest("mesh", mesh)

        yelb_resources = eks_cluster.add_manifest("yelb-resources", redis_virtual_node, redis_virtual_service,
                                                  db_virtual_node, db_virtual_service, app_virtual_node,
                                                  app_virtual_service, app_virtual_router, ui_virtual_node,
                                                  ui_virtual_service)

        yelb_resources.node.add_dependency(mesh)