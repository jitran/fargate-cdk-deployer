from aws_cdk import (
    core
)
import jsii


@jsii.implements(core.IAspect)
class UseOriginalConstructID:

    def visit(self, element):
        """ Traverses all the Construct elements and resets their resource logical ID to their original construct ID
        Note:
          * If this method is not applied, the synthesised template will contain resource logical IDs with hashes
          * appended to them. This method will reset each explicitly defined resource back to their original
          * construct ID.
          * Dependent (implicit) resources that were auto generated such as the patterns constructs, contain hashes
          * in their original construct IDs; these can't be rectified and it may cause issues with this method.
        """
        # If you create an AWS Resource Construct it will create a CfnResource too
        # i.e. aws_cdk.aws_ecs.TaskDefinition > aws_cdk.aws_ecs.CfnTaskDefinition
        # The resource will have a user defined ID, while the CfnResource will have an ID of 'Resource'

        # AWS Resource Constructs
        if hasattr(element.node.default_child, 'override_logical_id'):
            element.node.default_child.override_logical_id(element.node.id)
        # CFN Resource Constructs
        elif hasattr(element, 'override_logical_id'):
            if element.node.id != 'Resource':
                element.override_logical_id(element.node.id)
