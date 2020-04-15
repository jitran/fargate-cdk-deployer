import yaml
from mergedeep import merge


GLOBAL_CONFIG = 'conf/global.yml'
VPCS_CONFIG = 'conf/vpcs.yml'

SHARED_LB_DNS_NAME = 'SharedLoadBalancerDNSName'
SHARED_LB_HOSTED_ZONE_ID = 'SharedLoadBalancerCanonicalHostedZoneID'
SHARED_LB_LISTENER = 'SharedLoadBalancerListener'
SHARED_SERVICE_SECURITY_GROUP = 'SharedFargateServiceSecurityGroup'

NON_OVERRIDABLE_PREFIXES = ['whitelisted_actions']


class Config:

    def __init__(self, deploy_config, global_config=GLOBAL_CONFIG, vpcs_config=VPCS_CONFIG, overrides=[]):
        """ The interface to the configuration data model. """
        self._global = Config.dataload(global_config)
        self._deployment = Config.dataload(deploy_config)
        self._vpcs = Config.dataload(vpcs_config)
        self._combined = merge(
            {},
            self._global,
            self._vpcs[self._deployment['vpc_id']],
            self._deployment
        )
        self.configure_cli_overrides(overrides)

    def dataload(file_path) -> dict:
        """ Loads the given yaml file into a dictionary. """
        with open(file_path) as f:
            return yaml.safe_load(f)

    def configure_cli_overrides(self, overrides):
        """ Applies the overrides from the command line to the config. """
        for override in overrides:
            (path, value) = override.split('=')
            keys = path.split('.')
            item = self._combined
            if keys[0] not in NON_OVERRIDABLE_PREFIXES:
                for index, key in enumerate(keys):
                    if (index + 1) == len(keys):
                        item[key] = value
                    item = item[key]

    def containers(self) -> dict:
        """ Returns a dictionary of all the container definitions.
        Data structure layout:

        container_1:
          image: container_image
          port: container_app_port
          environment:
            ENVIRONMENT_VARIABLE_1: value_1
            ENVIRONMENT_VARIABLE_n: value_n
          depends_on: list_of_conditions
          health_check:
            path: health_check_path
            protocol: health_check_protocol
            interval: health_check_interval_seconds
            timeout: health_check_timeout_seconds
            retries: health_check_path_retry_count
          overrides:
            override_1: value_1
            ...
        container_n:
          ...
        """
        return self._combined['containers']

    def cluster_stack_name(self) -> str:
        """ Returns the ECS CFN cluster stack name. """
        return self._combined['cluster_stack_name']

    def execution_role_id(self) -> str:
        """ Returns the ECS task execution role logical id. """
        return self._combined['execution_role_id']

    def hosted_zone_name(self) -> str:
        """ Returns the Route53 Hosted Zone name. """
        return self._combined['hosted_zone_name']

    def ingress_security_group_ids(self) -> list:
        """ Returns a list of security group ids that are allowed to access the load balancer. """
        return self._combined['ingress_security_group_ids']

    def log_group_id(self) -> str:
        """ Returns the LogGroup logical id. """
        return self._combined['log_group_id']

    def log_retention_days(self) -> int:
        """ Returns the number of log return days. """
        return self._combined['log_retention_days']

    def private_subnet_ids(self) -> list:
        """ Returns a list of private subnet ids. """
        return self._combined['private_subnet_ids']

    def roles(self) -> dict:
        """ Returns a dictionary of all the roles.
        Data structure layout:

        role_id_1:
          policy_id_1:
            action:
              - iam:permission_1
              - iam:permission_n
            effect: [Allow|Deny]
            resource: string_or_list_of_resources
          policy_id_n:
            ...
        role_id_n:
          ...
        """
        return self._combined['roles']

    def service_desired_count(self) -> int:
        """ Returns the desired number of service instances. """
        return self._combined['desired_count']

    def service_health_check_path(self) -> str:
        """ Returns the health check path used by the load balancer. """
        return self.containers()[self.service_name()]['health_check']['path']

    def service_health_check_protocol(self) -> str:
        """ Returns the health check protocol used by the load balancer. """
        return self.containers()[self.service_name()]['health_check']['protocol']

    def service_name(self) -> str:
        """ Returns the container that is registered with the load balancer. """
        return self._combined['service_name']

    def service_overrides(self) -> dict:
        """ Returns a dictionary containing ECS Service properties overrides. """
        return self._combined['service_overrides']

    def service_paths(self) -> list:
        """ Returns a list of url paths that are served by the load balancer's registered container. """
        return self._combined['service_paths']

    def service_port(self) -> int:
        """ Returns the container port that is available to the load balancer. """
        return self._combined['containers'][self.service_name()]['port']

    def service_priority(self) -> int:
        """ Returns load balancer listener priority. """
        return self._combined['service_priority']

    def shared_lb_dns_name_export_name(self) -> str:
        """ Returns the CFN export name. """
        return f"{self.cluster_stack_name()}:{SHARED_LB_DNS_NAME}"

    def shared_lb_hosted_zone_id_export_name(self) -> str:
        """ Returns the CFN export name. """
        return f"{self.cluster_stack_name()}:{SHARED_LB_HOSTED_ZONE_ID}"

    def shared_lb_listener_export_name(self) -> str:
        """ Returns the CFN export name. """
        return f"{self.cluster_stack_name()}:{SHARED_LB_LISTENER}"

    def shared_service_security_group_export_name(self) -> str:
        """ Returns the CFN export name. """
        return f"{self.cluster_stack_name()}:{SHARED_SERVICE_SECURITY_GROUP}"

    def ssl_certificate_arn(self) -> str:
        """ Returns the ssl certificate arn to be used by the load balancer. """
        return self._combined['ssl_certificate_arn']

    def ssl_policy(self) -> str:
        """ Returns the ssl policy to be used by the load balancer. """
        return self._combined['ssl_policy']

    def tags(self) -> dict:
        """ Returns a dictionary containing tag pairs. """
        return self._combined['tags']

    def target_group_overrides(self) -> dict:
        """ Returns a dictionary containing TargetGroup properties overrides. """
        return self._combined['target_group_overrides']

    def task_cpu(self) -> str:
        """ Returns the cpu allocation for the task definition. """
        return self._combined['cpu']

    def task_memory(self) -> str:
        """ Returns the memory allocation for the task definition. """
        return self._combined['memory']

    def task_overrides(self) -> dict:
        """ Returns a dictionary containing TaskDefinition properties overrides. """
        return self._combined['task_definition_overrides']

    def task_role_id(self) -> str:
        """ Returns the ECS task role logical id. """
        return self._combined['task_role_id']

    def vpc_id(self) -> str:
        """ Returns the VPC ID required for the deployment. """
        return self._combined['vpc_id']

    def whitelisted_actions(self) -> str:
        """ Returns a list of the whitelisted IAM actions. """
        return self._combined['whitelisted_actions']
