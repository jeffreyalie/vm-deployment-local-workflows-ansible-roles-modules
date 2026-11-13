---
name: vm-deployment-tfvars
description: Create a new per-VM Terraform .tfvars file (e.g. dev03.tfvars, prod03.tfvars) for the local-workflows-ansible-roles-modules homelab repo that deploys Ubuntu VMs on LXD via Gitea Actions. Use whenever the user wants to add, create, deploy, provision or spin up a new VM, new dev/prod environment VM, or a new tfvars file for this repo - even if they only say "I need dev03" or "new prod VM" and don't mention tfvars. Asks for the environment and the VM resource inputs, then writes terraform/env/ENV/VM_NAME.tfvars.
---

# VM tfvars creator

Adds one file to the repo: `terraform/env/<env>/<vm_name>.tfvars`. The Gitea workflows (`terraform-plan/apply/destroy`, `ansible-deploy`) find a VM by that filename, so the filename must exactly equal the `vm_name` workflow input.

## Steps

1. **Ask for the inputs.** If `ask_user_input_v0` is available, use it for choices (environment, sizing preset); otherwise ask in one short message. Don't ask for anything the user already gave. Needed:
   - **environment**: `dev` or `prod` (nothing else is accepted by the workflows)
   - **vm_name**: e.g. `dev03`, `prod03` (lowercase letters, digits, hyphens). Convention: starts with the environment.
   - **Resources**, offering the defaults below so the user can just accept them:

     | Variable | Default | Notes |
     |---|---|---|
     | `image` | `ubuntu-26.04-vm` | LXD image alias |
     | `os_type` | `ubuntu-vm` | becomes part of the instance name |
     | `network` | `lxdbr0` | |
     | `storage_pool` | `default` | |
     | `disk_size` | `10GiB` | |
     | `cpu_count` | `2` | number, unquoted in the file |
     | `memory_size` | `2GiB` | |

   If the user says "same as dev01/prod01" or "defaults", use the defaults without further questions.

2. **Generate the file** with the script (it validates and refuses to overwrite):
   ```bash
   python scripts/generate_tfvars.py --env dev --vm-name dev03 \
     --cpu-count 2 --memory-size 2GiB --disk-size 10GiB \
     --out-root /mnt/user-data/outputs
   ```
   Omit flags to take defaults. If the file exists, ask before re-running with `--force`. If the user's repo is available locally, point `--out-root` at its root instead.

3. **Present the file** (`present_files`) and tell the user the resulting instance name: `<env>-<os_type>-<vm_name>`, e.g. `dev-ubuntu-vm-dev03`. It must be unique on the LXD host.

4. **Give the next steps**, briefly: copy to `terraform/env/<env>/` in the repo, branch + PR (Terraform Check runs), run **Terraform Plan**, then **Terraform Apply**, then **Ansible Deploy** with the same environment and vm_name inputs.

## Rules

- Never put secrets in the file. `lxd_address` and `ansible_ssh_public_key` come from `TF_VAR_*` (Gitea secrets or OpenBao). `vm_name` and `environment` come from workflow inputs, so don't add them to tfvars either.
- Don't quote `cpu_count`; do quote the other values.
- If the user asks for a nonstandard image alias, network or pool, use it as given but remind them it must exist on the LXD host.
- Only create the tfvars file. Don't edit workflows, modules or playbooks unless asked.
