# Config

The following configuration files form the basis of Fargate CDK Deployer.

They are merged together during run time where the order of priority is:
  1. deploy
  1. vpcs
  1. global


## global.yml

Defines all the mandatory resources:
  * Side-car containers
  * Roles
  * IAM whitelisted actions
  * Resource overrides

Refer to [global.yml](global.yml) for a detailed description of each setting.

*Note: If you're deploying via the docker-compose (deploy\*.sh scripts), changes to this config file will require a rebuild of the cdk container.*


## vpcs.yml

Contains Account and VPC specific configuration.

Refer to [vpcs.yml](vpcs.yml) for a detailed description of each setting.

*Note: If you're deploying via the docker-compose (deploy\*.sh scripts), changes to this config file will require a rebuild of the cdk container.*


## deploy/

### deploy/cluster/\<env\>.yml

Contains the VPC, load balancer ingress, and application port information for building a Shared ECS Cluster and Application Load balancer.

This config file resides in the API repository under the deploy/cluster/ directory.

Refer to [cluster.yml](examples/cluster.yml) for a detailed description of each setting.


### deploy/fargate/\<env\>.yml

Contains the Fargate Container deployment information:
  * Container definitions
  * CPU, Memory, and VPC requirements
  * Log retention days
  * Service paths and health checks
  * Additional IAM permissions
  * Tags for your AWS resources

This config file resides in the API repository under the deploy/fargate/ directory.

Refer to [deploy.yml](examples/deploy.yml) for a detailed description of each setting.


## Overrides

The stacks are configured with basic defaults. If the standard settings in the configuration files are not adequate for your needs,
consider the following:
  * Container overrides
  * Target Group overrides
  * Task Definition overrides
  * ECS Service overrides

Refer to [global.yml](global.yml) for a detailed description of the above options.


## IAM Permissions

Additional IAM permissions can be granted to the containers.
See [deploy.yml](examples/deploy.yml) for an example 'send-mail' policy that was added to the TaskRole.

A list of IAM whitelisted actions is available under the `whitelisted_actions` list inside [global.yml](global.yml).
Update this list if your applications require further permissions beyond the standard set.
Additional permissions should be reviewed thoroughly.


## Examples
More examples are available in the [tests directory](../tests/fixtures/conf/)
