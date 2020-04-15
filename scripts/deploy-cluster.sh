#!/bin/bash -e

usage() {
    cat << EOF
usage: $(basename "$0") -s <stack_name> -e <environment> -d <deploy_config> [-a <apply_changes>]

* stack_name         [required] CloudFormation Stack name for the ECS Cluster
* environment        [required] Environment to deploy to (ie. aws profile)
* deploy_config      [required] Deployment config file (relative to the current working directory)
* apply_changes      [optional] Apply the new changes
EOF
    exit 1
}

while getopts ":d:e:s:a?:" o; do
  case "${o}" in
    a)
      apply_changes=true
      ;;
    d)
      deploy_config=${OPTARG}
      ;;
    e)
      environment=${OPTARG}
      ;;
    s)
      stack_name=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done

if [[ -z ${environment} || -z ${stack_name} || -z ${deploy_config} ]]; then
  usage
fi

docker_compose_file="${BASH_SOURCE%/*}/cdk-docker-compose.yml"
config_file="/cwd/${deploy_config}"

setup_aws() {
  export AWS_ACCESS_KEY_ID="$(aws configure get aws_access_key_id --profile $environment)"
  export AWS_SECRET_ACCESS_KEY="$(aws configure get aws_secret_access_key --profile $environment)"
  export AWS_DEFAULT_REGION="$(aws configure get region --profile $environment)"
  #export AWS_SESSION_TOKEN="$(aws configure get aws_session_token --profile $environment)"
}

perform_deployment() {
  setup_aws

  docker-compose -f $docker_compose_file run cdk \
    -a "python3 app_cluster.py --stack-name $stack_name -d $config_file" diff

  if [ -n "${apply_changes}" ]; then
    docker-compose -f $docker_compose_file run cdk \
      -a "python3 app_cluster.py --stack-name $stack_name -d $config_file" \
      deploy --require-approval never
  fi
}

perform_deployment
