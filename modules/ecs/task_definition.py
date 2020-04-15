from aws_cdk import (
    aws_ecs as ecs,
    core,
)


class TaskDefinition(core.Construct):

    def __init__(self, scope: core.Construct, id: str, containers, cpu, execution_role_id, log_group_id, memory, task_role_id, overrides):
        super().__init__(scope, id)

        container_definitions = []
        for name, item in containers.items():
            definition = {}
            definition['name'] = name
            definition['image'] = item['image']
            definition['portMappings'] = [{'containerPort': item['port']}]
            definition['environment'] = self.add_environment(item['environment'])
            definition['healthCheck'] = self.add_health_check(item['health_check'], item['port'])
            definition['logConfiguration'] = self.add_logging(log_group_id, name)
            definition['dependsOn'] = item['depends_on']
            self.add_container_definition_overrides(definition, item['overrides'])
            container_definitions.append(definition)

        task_def = ecs.CfnTaskDefinition(
            self,
            id=id,
            family=core.Aws.STACK_NAME,
            cpu=cpu,
            memory=memory,
            network_mode='awsvpc',
            requires_compatibilities=['FARGATE'],
            execution_role_arn=core.Fn.ref(execution_role_id),
            task_role_arn=core.Fn.ref(task_role_id),
            container_definitions=container_definitions
        )
        for property, value in overrides.items():
            task_def.add_override(property, value)

    def add_environment(self, environment) -> list:
        if environment:
            return [{'name': k, 'value': v} for k, v in environment.items()]

    def add_health_check(self, health_check, port) -> dict:
        url = f"{health_check['protocol']}://localhost:{port}{health_check['path']}"
        return {
            'command': ['CMD-SHELL', f"curl -f -k {url} || exit 1"],
            'interval': health_check['interval'],
            'timeout': health_check['timeout'],
            'retries': health_check['retries'],
        }

    def add_logging(self, log_group_id, prefix) -> dict:
        return {
            'logDriver': 'awslogs',
            'options': {
                'awslogs-group': core.Fn.ref(log_group_id),
                'awslogs-region': core.Aws.REGION,
                'awslogs-stream-prefix': prefix
            }
        }

    def add_container_definition_overrides(self, definition, overrides):
        if overrides:
            for property, value in overrides.items():
                definition[property] = value
