# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## High-Level Architecture and Structure

This repository implements a complete infrastructure-as-code solution that:
- Provisions Ubuntu 24.04 VMs on LXD using Terraform with a reusable `lxd-vm` module
- Configures VMs with cloud-init for automated setup
- Deploys applications via Ansible playbooks and local roles
- Manages environments (dev/prod) with separate state management per VM in Seaweed S3 backend
- Provides CI/CD automation through local Gitea Actions workflows

The repository follows a module-based Terraform architecture where:
- Each environment (`dev`, `prod`) has its own root module under `terraform/env/<env>/` that calls the shared `lxd-vm` module
- The `lxd-vm` module encapsulates all LXD resource definitions and cloud-init rendering
- Ansible uses local roles — no Ansible Galaxy or centralised role server

## Key Components

### Terraform Structure
```
terraform/
├── env/
│   ├── dev/
│   │   ├── backend.tf          # S3 (Seaweed) backend configuration
│   │   ├── main.tf             # Calls the lxd-vm module  
│   │   ├── variables.tf        # All input variables for this environment
│   │   ├── outputs.tf          # VM name, IP, MAC, SSH command
│   │   └── dev01.tfvars        # Per-VM resource config (committed, no secrets)
│   └── prod/
│       └── ... same structure as dev
└── modules/
    └── lxd-vm/
        ├── main.tf             # lxd_instance resource + locals (instance name, cloud-init)
        ├── variables.tf        # Module input variables
        ├── outputs.tf          # vm_name, vm_ip, vm_mac_address, ansible_ssh_command
        └── cloud-init/
            └── user-data.yaml  # cloud-init template (ansible user, SSH hardening)
```

### Ansible Structure  
```
ansible/
├── inventory.yml               # Dynamic inventory via VM_IP env var
├── playbook.yml                # Entry playbook: common + docker roles
└── roles/
    ├── common/
    │   └── tasks/main.yml      # apt cache + base packages
    └── docker/
        └── tasks/main.yml      # Docker CE install from upstream repo
```

### Gitea Workflows
```
.gitea/workflows/
├── terraform-check.yml     # fmt + validate + tflint (PR trigger)
├── terraform-plan.yml      # plan only (manual trigger)  
├── terraform-apply.yml     # apply (manual trigger)
├── terraform-destroy.yml   # destroy with confirmation gate (manual trigger)
├── ansible-check.yml       # lint + syntax check (PR trigger)
└── ansible-deploy.yml      # run playbook against VM (manual trigger)
```

## Common Commands

### Terraform
```bash
# Validate Terraform configuration  
terraform validate

# Format all .tf files
terraform fmt -check -diff

# Initialize a Terraform environment (example for dev)
cd terraform/env/dev
terraform init -backend-config="endpoint=http://minio-host:9000" \
  -backend-config="bucket=terraform-state" \
  -backend-config="key=state/dev/dev01/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="access_key=<key>" \
  -backend-config="secret_key=<secret>" \
  -backend-config="skip_credentials_validation=true" \
  -backend-config="skip_metadata_api_check=true" \
  -backend-config="skip_requesting_account_id=true" \
  -backend-config="force_path_style=true"

# Plan Terraform changes
terraform plan -var-file="dev01.tfvars"

# Apply Terraform changes
terraform apply -auto-approve -var-file="dev01.tfvars"

# Show Terraform outputs
terraform output vm_ip

# Destroy a VM
terraform destroy -var-file="dev01.tfvars"
```

### Ansible  
```bash
# Run ansible-lint on playbook
ansible-lint ansible/playbook.yml

# Validate ansible playbook syntax
ansible-playbook ansible/playbook.yml --syntax-check

# Run playbook manually (example)
VM_IP=192.168.1.100
ansible-playbook -i "$VM_IP," \
  -u ansible \
  --private-key ~/.ssh/id_rsa \
  ansible/playbook.yml
```

## Local Development Workflow

1. Create a new `.tfvars` file under `terraform/env/<env>/` by copying an existing one and adjusting resources as needed (image, cpu, memory, disk)

2. Run Terraform Check and Plan via Gitea Actions — go to Actions → `Terraform Check` / `Terraform Plan`, select your feature branch, enter environment and VM name

3. Run Ansible Check via Gitea Actions — go to Actions → `Ansible Check`, select your feature branch to lint and syntax-check the playbook

4. Open a PR and merge to `main` — the Check workflows run automatically on the PR; merge once green

5. Run Terraform Apply via Gitea Actions — go to Actions → `Terraform Apply`, select `main` branch, enter environment and VM name; the VM is created on LXD

6. Run Ansible Deploy via Gitea Actions — go to Actions → `Ansible Deploy`, select `main` branch, enter environment and VM name; Ansible roles are applied to the live VM

## Secrets Management

All secrets configured at Gitea org level (Infra org) for workflows:
- LXD_ADDRESS, LXD_CLIENT_CERT, LXD_CLIENT_KEY
- S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY  
- ANSIBLE_SSH_PUBLIC_KEY, ANSIBLE_SSH_PRIVATE_KEY

## Key Design Notes

- VM naming convention: `<environment>-<os_type>-<vm_name>` (e.g. `dev-ubuntu-vm-dev01`, `prod-ubuntu-vm-prod02`)
- State is stored in Seaweed S3 at path: `s3://terraform-state/state/<environment>/<vm_name>/terraform.tfstate`
- SSH hardening enabled in cloud-init template
- Password authentication disabled for ansible user
- SSH keys used for both Terraform LXD connections and Ansible deployment
- All workflows run from the root directory of the repository
- Workflow inputs must match specific patterns (environment = dev/prod, vm_name = <name>.tfvars)

## Deployment Flow

1. Create/edit a .tfvars file under terraform/env/<env>/
2. Open a PR → terraform-check + ansible-check run automatically  
3. Merge to main
4. Manually trigger terraform-plan → review output
5. Manually trigger terraform-apply → VM is created via LXD
6. Manually trigger ansible-deploy → Ansible roles applied to the live VM

## Important Files to Know

- `terraform/modules/lxd-vm/cloud-init/user-data.yaml` - Cloud-init template with SSH hardening and ansible user setup
- `ansible/playbook.yml` - Main playbook that applies common and docker roles  
- `.gitea/workflows/ansible-deploy.yml` - Ansible deploy workflow that reads Terraform output to get VM IP
- `terraform/env/dev/dev01.tfvars` - Example dev environment configuration
- `terraform/env/prod/prod01.tfvars` - Example prod environment configuration