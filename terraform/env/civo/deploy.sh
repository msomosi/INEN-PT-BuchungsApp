#!/bin/bash
# deploy.sh - Automated Terraform deployment script
set -e  # Exit immediately if any command fails

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Apply cluster components
echo "Deploying Kubernetes cluster..."
terraform apply -target=module.cluster_civo -auto-approve

# Initial ArgoCD setup
echo "Deploying ArgoCD..."
terraform apply -target=module.argocd_apps -auto-approve

# First full apply
echo "First full apply..."
terraform apply -auto-approve

# Subsequent ArgoCD updates
echo "Updating ArgoCD applications..."
terraform apply -target=module.argocd_apps -auto-approve

# Final apply to ensure consistency
echo "Final apply..."
terraform apply -auto-approve

# Get ArgoCD admin password
echo "ArgoCD Admin Password:"
terraform output -raw argocd_admin_password

echo "Deployment completed successfully!"
