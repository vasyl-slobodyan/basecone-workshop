#!/usr/bin/env python3

import aws_cdk as cdk

from stacks.infra import Infra
from stacks.application import Application
from stacks.mesh import Mesh

app = cdk.App()

infra_stack = Infra(app, "infra")
application_stack = Application(app, "application", _cluster=infra_stack.cluster)
mesh_stack = Mesh(app, "mesh", _cluster=infra_stack.cluster)

app.synth()
