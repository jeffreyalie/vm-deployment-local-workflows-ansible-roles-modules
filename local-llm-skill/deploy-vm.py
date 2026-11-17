#!/usr/bin/env python3

import sys
import os
from datetime import datetime

def generate_tfvars(environment, vm_name, image_type):
    """Generate a .tfvars file for Terraform deployment"""

    # Validate inputs
    if environment not in ['dev', 'prod']:
        raise ValueError("Environment must be 'dev' or 'prod'")

    if not vm_name:
        raise ValueError("VM name is required")

    if not image_type:
        raise ValueError("Image type is required")

    # Define the content of the .tfvars file
    tfvars_content = f'''# Generated Terraform variables for {environment}-{vm_name}
# Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# VM Configuration
vm_name = "{vm_name}"
image = "{image_type}"

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
'''

    # Determine the file path
    file_path = f"terraform/env/{environment}/{vm_name}.tfvars"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the .tfvars file
    with open(file_path, 'w') as f:
        f.write(tfvars_content)

    return file_path

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python deploy-vm.py <environment> <vm_name> <image_type>")
        print("Example: python deploy-vm.py dev dev03 ubuntu:24.04")
        sys.exit(1)

    environment = sys.argv[1]
    vm_name = sys.argv[2]
    image_type = sys.argv[3]

    try:
        file_path = generate_tfvars(environment, vm_name, image_type)
        print(f"Successfully created {file_path}")
        print("You can now run Terraform commands to deploy this VM:")
        print(f"  cd terraform/env/{environment}")
        print(f"  terraform init")
        print(f"  terraform plan -var-file=\"{vm_name}.tfvars\"")
        print(f"  terraform apply -auto-approve -var-file=\"{vm_name}.tfvars\"")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)