# Environment Setup

Required items:
1. [IDE](#IDE)
2. [Python3 installed](#python3)
3. [Miniconda](#miniconda)
4. [Node and npm](#Node)
5. [AWS CDK installed](#cdk)
6. [Configure CDK](#Environment)

IDE
===

Any text editor will work depending on OS that you are using and familiar with.

---

python3
=======

Python3 installation.

Go to the python [python](https://www.python.org/downloads/ "Python Website") and download python for your OS.

---

miniconda
=========

Download miniconda from official [website](https://docs.conda.io/en/latest/miniconda.html "Miniconda Website").

---

Node
====

Download and Install [node and npm](https://nodejs.org/en/download/ "Node")

--- 

cdk
===

Download CDK using npm

```bash
npm install -g aws-cdk
```

----

Environment
===========

Open terminal and run this command in a new directory.

```bash
cdk init app --language=python
```

This will create a new project structure for CDK application.

Create new virtual environment using miniconda.

```bash
conda create -n aws-cdk python=3 -y
```

Activate the new environment

```bash
conda activate aws-cdk
```

Install required packages for python

```bash
pip install -r requirements.txt
```

Enable the account link in cdk

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### Next

- [EKS Cluster Creation](./EKS%20Cluster%20Creation.MD)