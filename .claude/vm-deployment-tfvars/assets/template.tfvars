# ---------------------------------------------------------------
# Per-VM resource config for: {{ENV}}-{{OS_TYPE}}-{{VM_NAME}}
# No secrets here. lxd_address and ansible_ssh_public_key are
# injected as TF_VAR_* from Gitea org secrets / OpenBao.
# vm_name and environment are passed in by the workflow inputs.
# ---------------------------------------------------------------

image        = "{{IMAGE}}"
os_type      = "{{OS_TYPE}}"
network      = "{{NETWORK}}"
storage_pool = "{{STORAGE_POOL}}"
disk_size    = "{{DISK_SIZE}}"
cpu_count    = {{CPU_COUNT}}
memory_size  = "{{MEMORY_SIZE}}"
