from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
    core,
)


class ListenerRule(core.Construct):

    def __init__(self, scope: core.Construct, id: str, listener_import_name, paths, priority, target_group_id):
        super().__init__(scope, id)

        elbv2.CfnListenerRule(
            self,
            id=id,
            actions=[{
                'type': 'forward',
                'targetGroupArn': core.Fn.ref(target_group_id)
            }],
            conditions=[{
                'field': 'path-pattern',
                'pathPatternConfig': {
                    'values': paths
                }
            }],
            listener_arn=core.Fn.import_value(listener_import_name),
            priority=priority
        )
