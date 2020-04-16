# Fargate CDK Deployer

This deploys:
  * a shared ECS Cluster
  * a shared private Application Load balancer
  * and one or more Fargate Containers into the same cluster

This architecture is based off Nathan Peck's [AWS Cloudformation Fargate examples](https://github.com/nathanpeck/aws-cloudformation-fargate):
  * [Public + Private VPC + Cluster](https://github.com/nathanpeck/aws-cloudformation-fargate/blob/master/fargate-networking-stacks/public-private-vpc.yml)
  * [Private Subnet, Private Load Balancer + Fargate Container](https://github.com/nathanpeck/aws-cloudformation-fargate/blob/master/service-stacks/private-subnet-private-loadbalancer.yml)


## Usage

Follow [README.md](conf/README.md) to setup the configuration files.

Build the cdk container and publish it to your registry:
```bash
./ci/build.sh <docker-image-uri>
```

Copy the [scripts](scripts/) directory into each of your API repositories.
This will be the interface to the Fargate-CDK-Deployer.

Deploy the Shared ECS Cluster and Load balancer stack:
```bash
./scripts/deploy-cluster.sh -s <fargate-cluster-stack-name> -e <env> -d deploy/cluster/<env>.yml -a
```

Deploy the Fargate Container stacks:
```bash
./scripts/deploy.sh -s <fargate-container-stack-name> -e <env> -d deploy/fargate/<env>.yml -a
```
Note: the `-a` option applies the changes. Remove the option if you wish to view the changes only.

When the Fargate Container stack completes it will output a domain name for you to access your underlying API.


## Design

  * An App is composed of a Stack
  * A Stack is composed of modules and constructs
  * A module is composed of one of more constructs


## Development

### Setup local environment

```bash
pyenv install 3.7.6
pyenv local 3.7.6
brew install node
npm install -g aws-cdk@1.32.2
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

### Testing

#### Python tests

Once you've implemented your changes and have written tests for it, run `./ci/ci.sh`. This will:
  * Test that your code conforms to PEP8 standards
  * Run the python test suite

Build the cdk container from the development branch:
```bash
./ci/build.sh
```

Ensure the tests passes in a clean container environment by running:
```bash
export BUILD_TAG=<BUILD_TAG_from_build_output>
docker-compose run tests
```

#### CDK tests

Deploy the Shared ECS Cluster and Load balancer stack into your test account:
```bash
# Using cdk directly
export AWS_PROFILE=<env>
export AWS_DEFAULT_REGION=<aws-region>
cdk -a "python3 app_cluster.py -s <fargate-cluster-stack-name> -d deploy/cluster/<env>.yml" synth
cdk -a "python3 app_cluster.py -s <fargate-cluster-stack-name> -d deploy/cluster/<env>.yml" deploy

# Or via the cdk container
export BUILD_TAG=<BUILD_TAG_from_build_output>
./scripts/deploy-cluster.sh -s <fargate-cluster-stack-name> -e <env> -d deploy/cluster/<env>.yml -a
```

Deploy the Fargate Container stacks into your test account:
```bash
# Using cdk directly
export AWS_PROFILE=<env>
export AWS_DEFAULT_REGION=<aws-region>
cdk -a "python3 app_fargate.py -s <fargate-container-stack-name> -d deploy/fargate/<env>.yml" synth
cdk -a "python3 app_fargate.py -s <fargate-container-stack-name> -d deploy/fargate/<env>.yml" deploy

# Or via the cdk container
export BUILD_TAG=<BUILD_TAG_from_build_output>
./scripts/deploy.sh -s <fargate-container-stack-name> -e <env> -d deploy/fargate/<env>.yml -a
```

### Release a new version

Update [version.txt](version.txt) and [CHANGELOG.md](CHANGELOG.md) to reflect your changes.

Build the cdk container from the master branch and publish it to your registry:
```bash
./ci/build.sh <docker-image-uri>
```


## Thoughts

You'll notice that the code doesn't make full use of the AWS Resource and Patterns constructs.
The AWS Resource constructs have many convenience functions, however their usage needs to be
documented thoroughly. I spent more time fighting the developer kit rather than building the things
I want.

I prefer to use the low level CDK constructs, i.e. CfnResource which is cloudformation described in
python syntax. It's not great because you're essentially writing cloudformation in python, but at
least you can name your resource IDs properly, reference external resources by their ARN/ID/Name
easily, and have more control on defining the resources.


It's also easier to map the low level constructs to its cloudformation equivalent as the property
names are the same in CDK but are in the camel case form. As the low level constructs align closely
to cloudformation, they are less susceptible to future CDK breaking changes :)

Overall CDK is not too bad. You get the flexibility and power of a programming language, but what I
really like the most is the ability to do a diff of the pending changes, deploy a change set, and
view the stack update events in real time.
