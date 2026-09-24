#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
IAM_TEST_PYTHON="${IAM_TEST_PYTHON:-python3}"
"$IAM_TEST_PYTHON" scripts/test_eks_upgrade_permissions.py
"$IAM_TEST_PYTHON" -m cfnlint union-ai-admin/aws/union-ai-admin-role.template.yaml
git diff --check
