from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    core,
)
from modules.dataload.config import (
    SHARED_LB_DNS_NAME,
    SHARED_LB_HOSTED_ZONE_ID,
    SHARED_LB_LISTENER,
    SHARED_SERVICE_SECURITY_GROUP
)


class SharedPrivateALB(core.Construct):

    def __init__(self, scope: core.Construct, id: str, ingress_security_group_ids, private_subnet_ids, service_port, ssl_certificate_arn, ssl_policy, vpc_id):
        super().__init__(scope, id)

        # Use low level constructs to build security groups as it allows us to name the
        # ingress rules properly. It's also easier to map the low level construct params
        # to their cfn equivalent
        app_sg = ec2.CfnSecurityGroup(
            self,
            id='SharedApplicationSecurityGroup',
            group_description='Shared Fargate Security Group',
            vpc_id=vpc_id
        )
        app_lb_sg = ec2.CfnSecurityGroup(
            self,
            id='SharedApplicationLBSecurityGroup',
            group_description='Shared ALB Security Group',
            vpc_id=vpc_id,
            security_group_egress=[{
                'ipProtocol': 'tcp',
                'fromPort': service_port,
                'toPort': service_port,
                'destinationSecurityGroupId': app_sg.ref
            }]
        )
        app_sg_ingress = ec2.CfnSecurityGroupIngress(
            self,
            id='SharedApplicationSecurityGroupIngress',
            group_id=app_sg.ref,
            source_security_group_id=app_lb_sg.ref,
            ip_protocol='tcp',
            from_port=service_port,
            to_port=service_port
        )
        for index, sg in enumerate(ingress_security_group_ids):
            ec2.CfnSecurityGroupIngress(
                self,
                id=f"SharedApplicationLBSecurityGroupIngress{index}",
                group_id=app_lb_sg.ref,
                source_security_group_id=sg,
                ip_protocol='tcp',
                from_port=443,
                to_port=443
            )
        lb = elbv2.CfnLoadBalancer(
            self,
            id='SharedLoadBalancer',
            scheme='internal',
            security_groups=[app_lb_sg.ref],
            subnets=private_subnet_ids
        )
        listener = elbv2.CfnListener(
            self,
            id='SharedListener',
            certificates=[{'certificateArn': ssl_certificate_arn}],
            default_actions=[{
                'type': 'fixed-response',
                'fixedResponseConfig': {
                    'contentType': 'text/plain',
                    'messageBody': 'You have reached the the Load Balancer, but not matched any of the listener rules',
                    'statusCode': '200'
                }
            }],
            load_balancer_arn=lb.ref,
            port=443,
            protocol='HTTPS',
            ssl_policy=ssl_policy
        )

        core.CfnOutput(
            self,
            id=SHARED_LB_DNS_NAME,
            description='Shared Load Balancer DNS Name',
            export_name=f"{core.Aws.STACK_NAME}:{SHARED_LB_DNS_NAME}",
            value=lb.attr_dns_name
        )
        core.CfnOutput(
            self,
            id=SHARED_LB_HOSTED_ZONE_ID,
            description='Shared Load Balancer Canonical Hosted Zone ID',
            export_name=f"{core.Aws.STACK_NAME}:{SHARED_LB_HOSTED_ZONE_ID}",
            value=lb.attr_canonical_hosted_zone_id
        )
        core.CfnOutput(
            self,
            id=SHARED_LB_LISTENER,
            description='Shared Load Balancer Listener',
            export_name=f"{core.Aws.STACK_NAME}:{SHARED_LB_LISTENER}",
            value=listener.ref
        )
        core.CfnOutput(
            self,
            id=SHARED_SERVICE_SECURITY_GROUP,
            description='Shared Fargate Security Group',
            export_name=f"{core.Aws.STACK_NAME}:{SHARED_SERVICE_SECURITY_GROUP}",
            value=app_sg.ref
        )
