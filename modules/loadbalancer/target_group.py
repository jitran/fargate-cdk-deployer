from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    core,
)


class TargetGroup(core.Construct):

    def __init__(self, scope: core.Construct, id: str, health_check_path, port, protocol, vpc_id, overrides):
        super().__init__(scope, id)

        target_group = elbv2.CfnTargetGroup(
            self,
            id=id,
            health_check_interval_seconds=20,
            health_check_path=health_check_path,
            health_check_port=str(port),
            health_check_timeout_seconds=10,
            healthy_threshold_count=3,
            unhealthy_threshold_count=5,
            matcher=elbv2.CfnTargetGroup.MatcherProperty(http_code='200'),
            port=port,
            protocol=protocol,
            target_type='ip',
            vpc_id=vpc_id
        )
        for property, value in overrides.items():
            target_group.add_override(property, value)
