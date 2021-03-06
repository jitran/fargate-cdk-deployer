import json
import pytest

from aws_cdk import core
from modules.stack.cluster_stack import ClusterStack
from modules.dataload.config import Config


DEPLOY_CONFIG = 'tests/fixtures/conf/cluster.yml'
GLOBAL_CONFIG = 'tests/fixtures/conf/global.yml'
VPCS_CONFIG = 'tests/fixtures/conf/vpcs.yml'


def get_template(deploy_config=DEPLOY_CONFIG, global_config=GLOBAL_CONFIG, vpcs_config=VPCS_CONFIG):
    app = core.App()
    config = Config(
        global_config=global_config,
        vpcs_config=vpcs_config,
        deploy_config=deploy_config
    )
    ClusterStack(
        scope=app,
        id='cluster',
        config=config,
        stack_name='fargate-cluster'
    )
    return json.dumps(app.synth().get_stack('fargate-cluster').template)


def test_ecs_cluster_created():
    assert('AWS::ECS::Cluster' in get_template())


def test_alb_created():
    assert('AWS::ElasticLoadBalancingV2::LoadBalancer' in get_template())


def test_alb_listener_created():
    assert('AWS::ElasticLoadBalancingV2::Listener' in get_template())


def test_security_groups_created():
    assert(get_template().count('AWS::EC2::SecurityGroup') > 2)


def test_snapshot():
    snapshot_template = Config.dataload('tests/fixtures/cluster.template')
    assert snapshot_template == json.loads(get_template())


def test_snapshot_with_no_default_vpcs():
    template = get_template(
        vpcs_config='tests/fixtures/conf/cluster/no_default_vpcs/vpcs.yml',
        deploy_config='tests/fixtures/conf/cluster/no_default_vpcs/cluster.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/cluster.template')
    assert snapshot_template == json.loads(template)


def test_snapshot_with_override_vpc_defaults():
    template = get_template(
        vpcs_config='tests/fixtures/conf/cluster/override_vpc_defaults/vpcs.yml',
        deploy_config='tests/fixtures/conf/cluster/override_vpc_defaults/cluster.yml'
    )
    snapshot_template = Config.dataload('tests/fixtures/cluster.template')
    assert snapshot_template == json.loads(template)


def test_new_application_port():
    template = get_template(
        global_config='tests/fixtures/conf/cluster/new_application_port/global.yml',
        deploy_config='tests/fixtures/conf/cluster/new_application_port/cluster.yml'
    )
    assert(template.count('"FromPort": 8080') == 2)
    assert(template.count('"ToPort": 8080') == 2)
