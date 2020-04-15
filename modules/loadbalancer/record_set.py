from aws_cdk import (
    aws_route53 as route53,
    core,
)


class RecordSet(core.Construct):

    def __init__(self, scope: core.Construct, id: str, hosted_zone_name, dns_name_import_name, hosted_zone_id_import_name):
        super().__init__(scope, id)

        record = route53.CfnRecordSet(
            self,
            id=id,
            name=f"{core.Aws.STACK_NAME}.{hosted_zone_name}",
            hosted_zone_name=hosted_zone_name,
            type='A',
            alias_target=route53.CfnRecordSet.AliasTargetProperty(
                dns_name=core.Fn.import_value(dns_name_import_name),
                hosted_zone_id=core.Fn.import_value(hosted_zone_id_import_name)
            )
        )
        core.CfnOutput(
            self,
            id='RecordSetName',
            description='Record Set Name',
            export_name=f"{core.Aws.STACK_NAME}:RecordSetName",
            value=record.name
        )
