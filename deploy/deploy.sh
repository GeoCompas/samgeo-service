#!/bin/bash
set -x

## Defaults values
REGION="us-east-1"
DEFAULT_SUBNET_ID="subnet-026b4b9759be2fdc0"
DEFAULT_SECURITY_GROUP_ID="sg-0c763a0ca2cf71d20"
DEFAULT_INSTANCETYPE="t2.micro"
DEFAULT_IMAGEID="ami-0e86e20dae9224db8"
KEY_NAME="rub21-ec2"

# Variables
KEY_FILE="$KEY_NAME.pem"
STACK_NAME="geosam-service"
TEMPLATE_FILE="cloudformation.yaml"

create_stack() {
  echo "Deploying CloudFormation stack..."
  aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
    SubnetId="${SUBNET_ID:-$DEFAULT_SUBNET_ID}" \
    SecurityGroupId="${SECURITY_GROUP_ID:-$DEFAULT_SECURITY_GROUP_ID}" \
    InstanceType="${INSTANCETYPE:-$DEFAULT_INSTANCETYPE}" \
    ImageId="${IMAGEID:-$DEFAULT_IMAGEID}"

  if [ $? -eq 0 ]; then
    echo "CloudFormation stack deployed successfully."
  else
    echo "Failed to deploy CloudFormation stack."
    exit 1
  fi

  # Get the public IP of the created instance
  INSTANCE_PUBLIC_IP=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='PublicIP'].OutputValue" \
    --output text)

  echo "Connect: ssh -i $KEY_FILE  ubuntu@$INSTANCE_PUBLIC_IP"
}

# Function to delete the CloudFormation stack and key pair
delete_stack() {
  echo "Deleting CloudFormation stack..."
  aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
  echo "Waiting for CloudFormation stack to be deleted..."
  aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"
  if [ $? -eq 0 ]; then
    echo "CloudFormation stack deleted successfully."
  else
    echo "Failed to delete CloudFormation stack."
    exit 1
  fi
}

# Parse the input argument for create or delete
case $1 in
create)
  echo "Creating the stack ..."
  if [ -n "$2" ]; then
    INSTANCETYPE="$2"
  fi

  if [ -n "$3" ]; then
    IMAGEID="$3"
  fi

  if [ -n "$4" ]; then
    SUBNET_ID="$4"
  fi

  if [ -n "$5" ]; then
    SECURITY_GROUP_ID="$5"
  fi
  create_stack
  ;;
delete)
  echo "Deleting the stack ..."
  delete_stack
  ;;
*)
  echo "Usage: $0 {create [INSTANCETYPE] [IMAGEID] [SUBNET_ID] [SECURITY_GROUP_ID] | delete}"
  exit 1
  ;;
esac
