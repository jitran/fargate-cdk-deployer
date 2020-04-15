from aws_cdk import (
    aws_ecs as ecs,
    core,
)


class Service(core.Construct):

    def __init__(self, scope: core.Construct, id: str, cluster_name, desired_count, private_subnet_ids, service_name, service_port, security_group_import_name, target_group_id, task_def_id, overrides):
        super().__init__(scope, id)

        service = ecs.CfnService(
            self,
            id=id,
            cluster=cluster_name,
            deployment_configuration={'maximumPercent': 200, 'minimumHealthyPercent': 100},
            deployment_controller={'type': 'ECS'},
            desired_count=desired_count,
            launch_type='FARGATE',
            load_balancers=[{
                'containerName': service_name,
                'containerPort': service_port,
                'targetGroupArn': core.Fn.ref(target_group_id)
            }],
            network_configuration={
                'awsvpcConfiguration': {
                    'assignPublicIp': 'DISABLED',
                    'securityGroups': [core.Fn.import_value(security_group_import_name)],
                    'subnets': private_subnet_ids
                }
            },
            task_definition=core.Fn.ref(task_def_id)
        )
        for property, value in overrides.items():
            service.add_override(property, value)
