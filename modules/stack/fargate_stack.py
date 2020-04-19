from aws_cdk import (
    aws_logs as logs,
    core
)
from modules.aspect.identifiers import UseOriginalConstructID
from modules.dataload.config import Config
from modules.ecs.service import Service
from modules.ecs.task_definition import TaskDefinition
from modules.loadbalancer.listener_rule import ListenerRule
from modules.loadbalancer.record_set import RecordSet
from modules.loadbalancer.target_group import TargetGroup
from modules.roles.service_role import ServiceRole


class FargateStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: Config, **kwargs):
        super().__init__(scope, id, **kwargs)

        logs.CfnLogGroup(
            self,
            id=config.log_group_id(),
            retention_in_days=config.log_retention_days()
        )
        for role, policies in config.roles().items():
            ServiceRole(
                self,
                id=role,
                policies=policies,
                service='ecs-tasks.amazonaws.com',
                whitelisted_actions=config.whitelisted_actions()
            )
        TaskDefinition(
            self,
            id='TaskDefinition',
            containers=config.containers(),
            cpu=config.task_cpu(),
            memory=config.task_memory(),
            log_group_id=config.log_group_id(),
            execution_role_id=config.execution_role_id(),
            task_role_id=config.task_role_id(),
            overrides=config.task_overrides()
        )
        TargetGroup(
            self,
            id='TargetGroup',
            health_check_path=config.service_health_check_path(),
            port=config.service_port(),
            protocol=str.upper(config.service_health_check_protocol()),
            vpc_id=config.vpc_id(),
            overrides=config.target_group_overrides()
        )
        Service(
            self,
            id='Service',
            cluster_name=config.cluster_stack_name(),
            desired_count=config.service_desired_count(),
            service_name=config.service_name(),
            service_port=config.service_port(),
            security_group_import_name=config.shared_service_security_group_export_name(),
            subnet_ids=config.private_subnet_ids(),
            target_group_id='TargetGroup',
            task_def_id='TaskDefinition',
            overrides=config.service_overrides()
        )
        ListenerRule(
            self,
            id='ListenerRule',
            listener_import_name=config.shared_lb_listener_export_name(),
            paths=config.service_paths(),
            priority=config.service_priority(),
            target_group_id='TargetGroup'
        )
        RecordSet(
            self,
            id='RecordSet',
            hosted_zone_name=config.hosted_zone_name(),
            dns_name_import_name=config.shared_lb_dns_name_export_name(),
            hosted_zone_id_import_name=config.shared_lb_hosted_zone_id_export_name()
        )

        for key, value in config.tags().items():
            core.Tag.add(self, key, value)

        self.node.apply_aspect(UseOriginalConstructID())
