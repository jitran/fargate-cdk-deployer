import json
import pytest

from aws_cdk import core
from modules.stack.fargate_stack import FargateStack
from modules.dataload.config import Config


DEPLOY_CONFIG = 'tests/fixtures/conf/deploy.yml'
GLOBAL_CONFIG = 'tests/fixtures/conf/global.yml'
VPCS_CONFIG = 'tests/fixtures/conf/vpcs.yml'


def get_template(deploy_config=DEPLOY_CONFIG, global_config=GLOBAL_CONFIG, vpcs_config=VPCS_CONFIG):
    app = core.App()
    config = Config(
        global_config=global_config,
        vpcs_config=vpcs_config,
        deploy_config=deploy_config
    )
    FargateStack(
        scope=app,
        id='fargate',
        config=config,
        stack_name='fargate-api'
    )
    return json.dumps(app.synth().get_stack('fargate-api').template)


def test_log_group_created():
    assert('AWS::Logs::LogGroup' in get_template())


def test_iam_roles_created():
    assert(get_template().count('AWS::IAM::Role') == 2)


def test_task_definition_created():
    assert('AWS::ECS::TaskDefinition' in get_template())


def test_ecs_service_created():
    assert('AWS::ECS::Service' in get_template())


def test_target_group_created():
    assert('AWS::ElasticLoadBalancingV2::TargetGroup' in get_template())


def test_listener_rule_created():
    assert('AWS::ElasticLoadBalancingV2::ListenerRule' in get_template())


def test_record_set_created():
    assert('AWS::Route53::RecordSet' in get_template())


def test_invalid_permissions():
    with pytest.raises(ValueError, match="The following actions are not allowed: \\['ec2:\\*', 'iam:\\*'\\]"):
        template = get_template(
            deploy_config='tests/fixtures/conf/fargate/invalid_permissions/deploy.yml'
        )


def test_snapshot():
    snapshot_template = Config.dataload('tests/fixtures/fargate.template')
    assert snapshot_template == json.loads(get_template())


def test_snapshot_with_extended_task_role():
    template = get_template(
        deploy_config='tests/fixtures/conf/fargate/extended_task_role/deploy.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/fargate_extended_task_role.template')
    assert snapshot_template == json.loads(template)


def test_snapshot_with_single_container():
    template = get_template(
        global_config='tests/fixtures/conf/fargate/single_container/global.yml',
        vpcs_config='tests/fixtures/conf/fargate/single_container/vpcs.yml',
        deploy_config='tests/fixtures/conf/fargate/single_container/deploy.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/fargate_single_container.template')
    assert snapshot_template == json.loads(template)


def test_snapshot_with_no_default_vpcs():
    template = get_template(
        global_config='tests/fixtures/conf/fargate/single_container/global.yml',
        vpcs_config='tests/fixtures/conf/fargate/no_default_vpcs/vpcs.yml',
        deploy_config='tests/fixtures/conf/fargate/no_default_vpcs/deploy.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/fargate_single_container.template')
    assert snapshot_template == json.loads(template)


def test_snapshot_with_override_vpc_defaults():
    template = get_template(
        global_config='tests/fixtures/conf/fargate/single_container/global.yml',
        vpcs_config='tests/fixtures/conf/fargate/override_vpc_defaults/vpcs.yml',
        deploy_config='tests/fixtures/conf/fargate/override_vpc_defaults/deploy.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/fargate_single_container.template')
    assert snapshot_template == json.loads(template)


def test_snapshot_with_overrides():
    template = get_template(
        global_config='tests/fixtures/conf/fargate/with_overrides/global.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/fargate_with_overrides.template')
    assert snapshot_template == json.loads(template)
