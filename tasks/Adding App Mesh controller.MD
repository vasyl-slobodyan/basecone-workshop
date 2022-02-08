# Adding App Mesh controller

Adding the CRDs for App AppMesh

```bash
kubectl apply -k "https://github.com/aws/eks-charts/stable/appmesh-controller/crds?ref=master"
```

This would extend kubernetes and allow it to create custom resources needed for AppMesh.

Lets create a namespace for AppMesh:

## Load the AppMesh helm chart

We would add this code to the `infra.py`

```python
        self.cluster.add_helm_chart('appmesh-controller',
                chart='appmesh-controller',
                repository='https://aws.github.io/eks-charts',
                release='appmesh-controller',
                create_namespace=True,
                namespace='appmesh-system',
                )
```

deploy changes with cdk

```bash
cdk deploy infra
```

Once this is deployed we have AppMesh enabled EKS cluster. Next step would be to deploy an application.

---

### Next

- [Adding yelb application](./Adding%20yelb%20application.MD)
