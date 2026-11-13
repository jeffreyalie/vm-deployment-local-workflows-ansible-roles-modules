---
name: deploy-vm
description: |
  Deploy a new VM using Terraform with LXD backend. This skill helps create new .tfvars configuration files for VM deployments, asking for environment, VM name, and image type to generate the appropriate configuration. It's triggered when users want to provision new virtual machines in dev or prod environments.
compatibility: 
  - Read
  - Write
  - Bash
---

# Deploy New VM with Terraform

This skill helps you deploy new VMs using the existing Terraform infrastructure-as-code setup. It will generate a .tfvars file for your new VM based on your inputs.

## When to use this skill

Use this skill when:
- You want to provision a new virtual machine in the dev or prod environment
- You need to create a configuration file (.tfvars) for Terraform deployment
- You're starting a new VM deployment workflow

## How it works

1. The skill will ask for:
   - Environment (dev or prod)
   - VM name 
   - Image type for the VM
2. It will generate a properly formatted .tfvars file in the correct directory
3. You can then use this file with Terraform to create your new VM

## Prerequisites

Before using this skill, ensure:
- You have access to the repository with Terraform configuration files
- You understand the existing environment structure (dev/prod)
- You know what image you want to use for your VM

## Usage

When prompted, provide the following information:
- Environment: "dev" or "prod"
- VM name: e.g., "dev01", "prod02", etc.
- Image type: e.g., "ubuntu:24.04", "debian:12", etc.

The skill will then create a .tfvars file in the appropriate directory with your configuration.

## Example

If you want to deploy a dev VM named "dev03" using Ubuntu 24.04 image:
- Environment: dev
- VM name: dev03  
- Image type: ubuntu:24.04

This will create a file at terraform/env/dev/dev03.tfvars with the appropriate configuration.