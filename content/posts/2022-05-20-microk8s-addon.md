---
title: "Microk8s NFS Addon"
date: 2022-05-20T14:15:05+07:00
slug: microk8s
description: How to develop Microk8s "Addon" and get it included in an official release.
image: images/microk8s-addon/big.png
categories:
  - tech
tags:
  - kubernetes
draft: false
---
[Microk8s](https://microk8s.io/) is a lightweight Kubernetes installation from Canonical easily extensible by "Addons". We recognize [Core](https://github.com/canonical/microk8s-core-addons) and [Community](https://github.com/canonical/microk8s-community-addons) Addons.
Addon is mostly a Helm Chart or set of Kubernetes manifests enabled and disabled in a user friendly way, as `microk8s enable MY_ADDON` and `microk8s disable MY_ADDON`.
This article describes end-to-end process of building multi-node Microk8s cluster for developing Microk8s Addon, testing and PR procedures.

Microk8s comes with `hostpath-storage` Core Addon which creates `microk8s-hostpath` Storage Class with ReadWriteOnce (RWO) access mode. This mode is fully sufficient of single-node setup where all Pods live on the same node and can share access to a common PVC in read-write mode. We are hitting multiple limits in multi-node cluster. That is why I am going to build Microk8s Addon for NFS Server Provisioner backed by hostpath Persistent Volume.

Real world usecase we are targeting is as follows:
- Multi-node Microk8s cluster
- One dedicated node acting as NFS Server with sufficiently large disk space
- Workloads spread on any other nodes being able to share common Persistance Volume Claim

My Addon will be re-using popular [nfs-server-provisioner](https://artifacthub.io/packages/helm/kvaps/nfs-server-provisioner) Helm Chart with parametrization customized for our setup.


## Installing Microk8s
I will use [multipass](https://multipass.run/), Canonical's native virtualization platform to launch two node Kubernetes cluster (`master` node and `worker1` node). Two nodes are needed to properly test ReadWriteMany access mode.

```
> multipass launch --name master -m 3G --disk 50G
> multipass launch --name worker1 -m 3G --disk 50G

❯ multipass list
Name                    State             IPv4             Image
master                  Running           10.66.64.198     Ubuntu 20.04 LTS
worker1                 Running           10.66.64.93      Ubuntu 20.04 LTS

❯ multipass shell master
ubuntu@master:~$ sudo snap install microk8s --classic --channel=1.24/stable
microk8s (1.24/stable) v1.24.0 from Canonical✓ installed

ubuntu@master:~$ sudo usermod -a -G microk8s $USER
ubuntu@master:~$ sudo chown -f -R $USER ~/.kube

# login/logout

ubuntu@master:~$ microk8s status
microk8s is running
...snipped...
```


Microk8s is now running as a single-node. Let's enable one of Core Addons - for DNS.

```
ubuntu@master:~$ microk8s enable dns
```


We are ready to install `worker1` node and join it to the cluster. For joining we will need a "join URL" generated on the `master` node.

```
ubuntu@master:~$ sudo microk8s add-node
...snipped
Use the '--worker' flag to join a node as a worker not running the control plane, eg:
microk8s join 10.66.64.198:25000/5011f5eb7649dd23100dd8284d4fb523/780b412277c2 --worker
...snipped...

❯ multipass shell worker1
ubuntu@worker1:~$ sudo snap install microk8s --classic --channel=1.24/stable
ubuntu@worker1:~$ sudo microk8s join 10.66.64.198:25000/5011f5eb7649dd23100dd8284d4fb523/780b412277c2 --worker
```


If all goes well, we should have 2-node cluster up and running. We can now manage our cluster from the `master` node.
For convenience let's avoid using `microk8s kubectl` or `microk8s.kubectl` and use bash aliases.

```
❯ multipass shell master
ubuntu@master:~$ echo "alias kubectl='microk8s kubectl'" >> ~/.bash_aliases
ubuntu@master:~$ source ~/.bash_aliases

ubuntu@master:~$ kubectl get node
NAME      STATUS   ROLES    AGE   VERSION
master    Ready    <none>   13m   v1.24.0-2+59bbb3530b6769
worker1   Ready    <none>   73s   v1.24.0-2+59bbb3530b6769
```


We can also export Microk8s kubeconfig using `microk8s config` command and operate the cluster from the host system.
Mind, that `microk8s` commands still have to be run from the `master` node (or any future control plane node), since `microk8s` binary is running just there.


## Developing Addon
### Process
The process can be summarized as follows:
- Fork [Community](https://github.com/canonical/microk8s-community-addons) Addons repository
- Develop your Addon in your repository in a feature branch
- Add your Addons repository into your cluster for manual test
- Develop programatic tests for your Addon using GitHub Workflows
- Run Github Workflows test in your repository
- If all good, raise PR to the source repo (Canonical)


### NFS Volume Provisioner
Addons are organized in the following structure:
```
addons.yaml         Authoritative list of addons included in this repository. See format below.
addons/
    <addon1>/
        enable      Executable script that runs when enabling the addon
        disable     Executable script that runs when disabling the addon
    <addon2>/
        enable
        disable
    ...
```


`addons.yaml` helps `microk8s` binary to identify your Addon in the repository and describes the Addon:
```
    - name: "nfs"
      description: "NFS Server Provisioner"
      version: "1.4.0"
      check_status: "statefulset.apps/nfs-server-provisioner"
      supported_architectures:
        - amd64
```


Individual Addons are maintained in own directory. Directory always contains `enable` and `disable` script and optionally any other files needed by the Addon, e.g. additional Kubernetes manifests.

Microk8s is distributed as a Snap package and Addons are managed through this Snap package as well. Each Snap package uses set of [Snap specific environment variables](https://snapcraft.io/docs/environment-variables)
which can be utilized by our `enable` and `disable` scripts. One of the most important Snap environment variable is `SNAP` variable which links our scripts to the native scripts, wrappers or binaried baked into the Microk8s Snap package itself.


### Enable Script
Full code can be found here: https://github.com/canonical/microk8s-community-addons/tree/main/addons/nfs.

Let's see some of the sections of the `enable` script for our Addon.

This is the example of Addon accessing `microk8s`'s binaries and configs, baked in the package or generated during the Snap installation.
```
KUBECTL="$SNAP/kubectl --kubeconfig=${SNAP_DATA}/credentials/client.config"
"$SNAP/microk8s-enable.wrapper" helm3
HELM="$SNAP_DATA/bin/helm3 --kubeconfig=$SNAP_DATA/credentials/client.config"
```


Now we are deploying the NFS Server Provisioner Helm Chart. Yes, it is simple as that.
```
if [ -z "$NODE_NAME" ]; then
   $HELM upgrade -i nfs-server-provisioner nfs-ganesha-server-and-external-provisioner/nfs-server-provisioner \
      --version $CHART_VERSION \
      --namespace $NAMESPACE --set persistence.enabled=true --set persistence.storageClass='-'
else
   $HELM upgrade -i nfs-server-provisioner nfs-ganesha-server-and-external-provisioner/nfs-server-provisioner \
      --version $CHART_VERSION \
      --namespace $NAMESPACE --set persistence.enabled=true --set persistence.storageClass='-' --set nodeSelector."kubernetes\.io/hostname"=$NODE_NAME
fi
```


Here I am using `helm repo add` and `helm install/upgrade` on-the-fly. You can however template Kubernetes manifests in advance,
update as needed and store them inside the Addon directory.
Since the Addon can be developed in any programming language which `microk8s` Snap is capable to run, options are pretty vast.

Parametrization is again up to the Addon developer. I prefer being user-friendly and maximize abstraction from the underlying Helm Chart.
In case the customer is technically skilled and needs detailed parametrization, then it is perhaps better to deploy Helm Chart directly and manage values files separately.

In my case, the Addon allows selection of Microk8s node on which the NFS Server Provisioner will be running and serving it's disk space.
```
microk8s enable nfs -n NODE_NAME
```


## Testing the Addon
For real testing, let's add our code as a new "addons repo" into the testing Microk8s cluster.
I recommend to remove primary community "addons repo" first (if  present on the cluster):
```
ubuntu@master:~$ microk8s disable community
ubuntu@master:~$ microk8s addons repo add mycommunity https://github.com/jkosik/microk8s-community-addons --reference MY-FEATURE-BRANCH
ubuntu@master:~$ microk8s addons repo list
```


This way only one set of community Addons will be present on the cluster.
Even though you can install Addon from defined a "addons repo" by calling `microk8s enable mycommunity/ADDON_NAME`, I experienced some glitches with duplicate Addon names.

Lets's confirm available "addons repos" and launch our new Addon (Addon name is `nfs` as defined previously in `addons.yaml`)
```
ubuntu@master:~$ microk8s addons repo list
REPO       ADDONS SOURCE
mycommunity     18 https://github.com/jkosik/microk8s-community-addons@880519
core           17 (built-in)

ubuntu@master:~$ microk8s enable nfs
Infer repository mycommunity for addon nfs
Infer repository core for addon helm3
Enabling Helm 3
...snipped...
NFS Server Provisioner is installed
```


At this point our Addon should be installed on the cluster and we can proceed with testing.
In case a bug is identified, just push the code to the feature branch and reload Addons repo:
```
microk8s addons repo update mycommunity
```


Optionally you can update files and folders directly in:
```
ubuntu@master:~/microk8s-community-addons$ ls /var/snap/microk8s/common/addons/
core  mycommunity
```


## Automated tests
Microk8s Core and Community Addons already contain GitHub workflows and `pytest`s for existing Addons.
It is pretty straightforward to extend them for out usecase.

## Publish
If all goes ok, finally you can raise PR from our repository to Canonical's base repository.
After merge, you Addon becomes part of Microk8s Community Addons. However nothing prevents you to share your own personal Addon repository directly to outside world.

Good luck with your new Addons!

(Addon described in this howto was merged and adopted in [MicroK8S v1.25](https://microk8s.io/docs/release-notes))