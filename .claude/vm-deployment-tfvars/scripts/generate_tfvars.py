#!/usr/bin/env python3
"""Validate inputs and write terraform/env/<env>/<vm_name>.tfvars.

Usage:
  generate_tfvars.py --env dev --vm-name dev03 [--image ...] [--os-type ...]
      [--network ...] [--storage-pool ...] [--disk-size ...]
      [--cpu-count N] [--memory-size ...] [--out-root DIR] [--force]
"""
import argparse, re, sys
from pathlib import Path

DEFAULTS = dict(image="ubuntu-26.04-vm", os_type="ubuntu-vm", network="lxdbr0",
                storage_pool="default", disk_size="10GiB", cpu_count="2",
                memory_size="2GiB")

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr); sys.exit(1)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--env", required=True)
    p.add_argument("--vm-name", required=True)
    for k, v in DEFAULTS.items():
        p.add_argument("--" + k.replace("_", "-"), default=v)
    p.add_argument("--out-root", default=".")
    p.add_argument("--force", action="store_true")
    a = p.parse_args()

    env = a.env.strip().lower()
    vm = a.vm_name.strip()
    if env not in ("dev", "prod"):
        fail("environment must be 'dev' or 'prod' (workflows reject anything else)")
    if not re.fullmatch(r"[a-z0-9-]+", vm):
        fail("vm_name must match ^[a-z0-9-]+$ (lowercase letters, digits, hyphens)")
    if not vm.startswith(env):
        print(f"WARNING: vm_name '{vm}' does not start with '{env}' - convention is dev01/prod01", file=sys.stderr)
    if not re.fullmatch(r"\d+(\.\d+)?(KiB|MiB|GiB|TiB|KB|MB|GB|TB)", a.disk_size):
        fail("disk_size must look like 10GiB")
    if not re.fullmatch(r"\d+(\.\d+)?(KiB|MiB|GiB|TiB|KB|MB|GB|TB)", a.memory_size):
        fail("memory_size must look like 2GiB")
    if not re.fullmatch(r"[1-9]\d*", a.cpu_count):
        fail("cpu_count must be a positive integer")

    vals = dict(ENV=env, VM_NAME=vm, IMAGE=a.image, OS_TYPE=a.os_type, NETWORK=a.network,
                STORAGE_POOL=a.storage_pool, DISK_SIZE=a.disk_size,
                CPU_COUNT=a.cpu_count, MEMORY_SIZE=a.memory_size)
    text = (Path(__file__).parent.parent / "assets" / "template.tfvars").read_text()
    for k, v in vals.items():
        text = text.replace("{{" + k + "}}", v)

    out = Path(a.out_root) / "terraform" / "env" / env / f"{vm}.tfvars"
    if out.exists() and not a.force:
        fail(f"{out} already exists (use --force only if the user confirmed overwrite)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(out)
    print(f"Instance name will be: {env}-{a.os_type}-{vm}")

if __name__ == "__main__":
    main()
