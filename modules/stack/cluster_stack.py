from aws_cdk import (
    aws_ecs as ecs,
    core
)
from modules.loadbalancer.shared_private_alb import SharedPrivateALB
from modules.aspect.identifiers import UseOriginalConstructID
from modules.dataload.config import Config


class ClusterStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, config: Config, **kwargs):
        super().__init__(scope, id, **kwargs)

        ecs.CfnCluster(
            self,
            id='ECSCluster',
            cluster_name=core.Aws.STACK_NAME
        )
        SharedPrivateALB(
            self,
            id='SharedPrivateALB',
            application_port=config.application_port(),
            ingress_security_group_ids=config.ingress_security_group_ids(),
            ssl_certificate_arn=config.ssl_certificate_arn(),
            ssl_policy=config.ssl_policy(),
            subnet_ids=config.private_subnet_ids(),
            vpc_id=config.vpc_id()
        )

        for key, value in config.tags().items():
            core.Tag.add(self, key, value)

        self.node.apply_aspect(UseOriginalConstructID())
