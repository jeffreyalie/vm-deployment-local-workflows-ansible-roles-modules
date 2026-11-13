#!/bin/bash

# Simple script to deploy a new VM using Terraform configuration

echo "=== VM Deployment Script ==="
echo

# Check if we're in the right directory
if [ ! -d "terraform/env" ]; then
    echo "Error: This script must be run from the root of the repository"
    exit 1
fi

# Ask for environment
echo "Select environment:"
echo "1) dev"
echo "2) prod"
read -p "Enter choice (1 or 2): " env_choice

case $env_choice in
    1)
        ENV="dev"
        ;;
    2)
        ENV="prod"
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Ask for VM name
read -p "Enter VM name (e.g., dev01, prod01): " VM_NAME

# Ask for image type
read -p "Enter image type (e.g., ubuntu:24.04, debian:12): " IMAGE_TYPE

echo
echo "Creating configuration for:"
echo "  Environment: $ENV"
echo "  VM Name: $VM_NAME"
echo "  Image Type: $IMAGE_TYPE"
echo

# Create the .tfvars file
cat > "terraform/env/$ENV/${VM_NAME}.tfvars" << EOF
# Generated Terraform variables for ${ENV}-${VM_NAME}
# Generated on $(date)

# VM Configuration
vm_name = "${VM_NAME}"
image = "${IMAGE_TYPE}"

# Resource allocation
cpu = 2
memory = 4096
disk = 20

# Network settings
network_mode = "bridged"
network_device = "lxdbr0"

# Cloud-init configuration
cloud_init_user = "ansible"
cloud_init_password_auth = false
EOF

echo "✓ Successfully created terraform/env/$ENV/${VM_NAME}.tfvars"

echo
echo "Next steps:"
echo "1. Review the generated .tfvars file"
echo "2. Navigate to terraform/env/$ENV/"
echo "3. Run: terraform init && terraform plan -var-file=\"${VM_NAME}.tfvars\""
echo "4. Run: terraform apply -auto-approve -var-file=\"${VM_NAME}.tfvars\""