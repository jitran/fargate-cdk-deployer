from aws_cdk import (
    aws_iam as iam,
    core,
)


class ServiceRole(core.Construct):

    def __init__(self, scope: core.Construct, id: str, policies, service, whitelisted_actions):
        super().__init__(scope, id)

        self.role = iam.CfnRole(
            self,
            id=id,
            assume_role_policy_document={
                'Statement': [{
                    'Action': 'sts:AssumeRole',
                    'Effect': 'Allow',
                    'Principal': {'Service': service}
                }]
            },
            policies=ServiceRole.add_policies(policies, whitelisted_actions)
        )

    def validate_actions(actions, whitelisted_actions):
        disallowed_actions = set(actions) - set(whitelisted_actions)
        if len(disallowed_actions) > 0:
            raise ValueError(f"The following actions are not allowed: {sorted(disallowed_actions)}")

    def add_policies(policies, whitelisted_actions) -> list:
        iam_policies = []
        for name, document in policies.items():
            ServiceRole.validate_actions(document['action'], whitelisted_actions)

            policy = {}
            policy['policyName'] = name
            policy['policyDocument'] = {
                'Statement': {
                    'Action': document['action'],
                    'Effect': document['effect'],
                    'Resource': document['resource']
                }
            }
            iam_policies.append(policy)
        return iam_policies
