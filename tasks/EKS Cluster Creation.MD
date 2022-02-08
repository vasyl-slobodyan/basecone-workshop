# EKS Cluster Creation

Edit the app.py file and change the content to this.

```python
#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.infra import Infra

app = cdk.App()

infra_stack = Infra(app, "infra")

app.synth()
```

Create a directory called `stacks` and create a file called `infra.py`

Insert this python code inside the `infra.py`

```python
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
                                   output_cluster_name=True,
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

```

This will create an EKS cluster with 2 nodes running on t3.small instance size.

Cluster is created with default roles for EC2 instances and no roles for pods. Those can be added in the future if required.

The default role is extended with permissions to allow Appmesh, XRAY and ECR access. We need those in the future.

---

Run the app with command and approve the changes. This would take 15-20 minutes

```bash
cdk deploy infra
```

Once the creating finished, copy two commands from the output to enable kubectl access to the cluster.

---

### Next

- [Adding App Mesh controller](./Adding%20App%20Mesh%20controller.MD)