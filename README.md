# Udacity EKS deployment walkthrough

<!-- TOC -->

- [Udacity EKS deployment walkthrough](#udacity-eks-deployment-walkthrough)
    - [what is this ?](#what-is-this-)
        - [what's in the box ?](#whats-in-the-box-)
        - [prerequisites](#prerequisites)
    - [steps to deploy an app' on EKS](#steps-to-deploy-an-app-on-eks)
        - [preliminary step: having an EKS cluster at the ready](#preliminary-step-having-an-eks-cluster-at-the-ready)
            - [auth issues with kubectl](#auth-issues-with-kubectl)
        - [manual procedure](#manual-procedure)
            - [build and push an image to Dockerhub](#build-and-push-an-image-to-dockerhub)
            - [deploy to Kubernetes](#deploy-to-kubernetes)
        - [automatic procedure](#automatic-procedure)
    - [! think of deleting unused resources](#-think-of-deleting-unused-resources)

<!-- /TOC -->

## what is this ?

This forkable repo aims at giving a walkthrough on how to deploy applications on Amazon EKS. Here, we just deploy a very simple sample Flask app'.

### what's in the box ?

- an `app.py` containing the app' to deploy
- a `Dockerfile`, containing the image that we are to build from
- a `deployment.yml` that we will use to deploy the app' on kube

### prerequisites

- you use GitHub
- Docker Desktop and `kubectl` installed
- have the AWS cli installed on your computer and be authenticated (you can do this by running `aws configure`)

## steps to deploy an app' on EKS

### preliminary step: having an EKS cluster at the ready

- [install `eksctl`](https://eksctl.io/introduction/#installation)
- check that `eksctl` is indeed in your path by running `eksctl` in your terminal
- `eksctl create cluster --name udacity-test` (this may take a while)
- get the details about the newly created cluster with `eksctl get cluster --name=udacity-test`
- run `kubectl get nodes` to check if your `kubectl` is wired to your newly created cluster

#### auth issues with `kubectl`

- when you have created a cluster with `eksctl`, a specific role is created to interact with the Kubernetes cluster RBAC system
- if you are not able to connect with `kubectl` by default; you may need to run an update of your kube config with =>

    ```bash
    aws eks update-kubeconfig \
    --region <region> \
    --name udacity-test \
    --role-arn <eksctl-cluster-nodegroup-role>
    ```

### manual procedure

#### build and push an image to Dockerhub

- create a repo in Dockerhub
- login to Dockerhub in your terminal => `docker login`
- build the app's docker image => `docker build <docker-user>/<dockerhub-repo-name>:<tag-name>`
- test the image locally => `docker run -p 80:5000 <image>`
- if there is an output @ localhost then you're all set
- now push the image to Dockerhub with a `docker push <docker-user>/<dockerhub-repo-name>:<tag-name>`

#### deploy to Kubernetes

- `kubectl apply -f deployment.yml`
- expose your deployment via a service by running => `kubectl expose deployment eks-walkthrough-deployment --type=LoadBalancer --name=eks-walkthrough-service`
- `kubectl get svc,pods,nodes` should give you the external ip of your load balancer
- in your browser, go this external ip at port `5000` (you may have to wait a few moments before the API is online)

### automatic procedure

- create a `codebuild-trust.json` file to specify trusting account details, you can copy the template example and fill in your account id, you can get your account id with `aws sts get-caller-identity --query Account --output text`
- next create a role that gives permissions to do stuff on the root account behalf => `aws iam create-role --role-name CodeBuildRolePolicy --assume-role-policy-document file://codebuild-trust.json --output text --query 'Role.Arn'`
- with the output role arn, we can now attach a policy that allows to read data from EKS and to get secrets to this role => `aws iam put-role-policy --role-name CodeBuildRolePolicy --policy-name eks-describe-secrets-get --policy-document file://codebuild-role-policy.json`
- now we need to authorize this role to perform actions against the Kubernetes cluster, the kube RBAC system is configured through a `ConfigMap` that was created when using `eksctl`, to get the current config of your cluster and save it in a file => `kubectl get -n kube-system configmap/aws-auth -o yaml > aws-auth.yml`
- the initial config map should look like => `aws-auth.before-example.yml`
- now you can modify the `aws-auth.yml` file to include your newly created role in the kube RBAC system as in `aws-auth.after-example.yml`
- you are now able to patch your cluster with a `kubectl patch configmap/aws-auth -n kube-system --patch "$(cat ./aws-auth.yml)"`
- now you can create a GitHub access token so that CodeBuild can monitor changes in your repository, you can do this in the profile level developer settings by creating a personal access token
- token should have these scopes:
  - `repo`
  - `admin:org`
- store the token in a safe place as you wont be able to see it again
- now we need to configure CloudFormation so we can create CodeBuild and CodePipeline resources; this configuration is to be updated in `cloud-formation.yml` (values to update are marked with `# ! UPDATE`); to understand better what's happening in this file, you can check the [CloudFormation template reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-reference.html)
- you can now go ahead and create a CloudFormation stack in the AWS console by uploading `cloud-formation.yml` as a standard stack with new resources
- this is the AWS UI that you will input your GitHub access token and other values so it is not versioned and accessible by others
- CodeBuild will look for a `buildspec.yml` file at the root of your project to perform the build steps; in there, you should verify that the `kubectl` client you are downloading matches the described specs; to get this version => `kubectl version --short --client`
- now you can do whatever you want in your build spec to specify if you want your app' to be released, sky is the limit ! 🌠

## ! think of deleting unused resources

- to delete a cluster and associated resources (VPC, subnets, etc.) created with `eksctl` your can run => `eksctl delete cluster --name=udacity-test`
