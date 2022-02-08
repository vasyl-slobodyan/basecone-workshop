from constructs import Construct
from aws_cdk import Stack, aws_ec2
import aws_cdk.aws_eks as eks
import aws_cdk as cdk


class Infra(Stack):

    def __init__(self, scope=Construct, construct_id=str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cluster = eks.Cluster(self, "demo-cluster",
                                   cluster_name="demo-cluster",
                                   version=eks.KubernetesVersion.V1_21,
                                   default_capacity=2,
                                   default_capacity_instance=aws_ec2.InstanceType.of(aws_ec2.InstanceClass.BURSTABLE3,
                                                                                     aws_ec2.InstanceSize.SMALL)
                                   )

        self.default_nodegroup_role = self.cluster.default_nodegroup.role

        self.default_nodegroup_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshEnvoyAccess"))
        self.default_nodegroup_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSAppMeshFullAccess"))
        self.default_nodegroup_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("AWSXRayDaemonWriteAccess"))
        self.default_nodegroup_role.add_managed_policy(
            cdk.aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryFullAccess"))


        self.cluster.add_helm_chart('appmesh-controller',
                                    chart='appmesh-controller',
                                    repository='https://aws.github.io/eks-charts',
                                    release='appmesh-controller',
                                    create_namespace=True,
                                    namespace='appmesh-system',
                                    values={
                                        "tracing": {
                                            "enabled": "true",
                                            "provider": "x-ray"
                                        }
                                    }
                                    )