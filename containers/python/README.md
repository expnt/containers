# Python IAC

```
ghcr.io/expnt/containers/xep-python-iac:[BASE_VERSION]-bookworm
```

Pre-configured Python image for Infrastructure as Code (IAC) CI/CD pipelines. Includes:

- Python 3.12 on Debian Bookworm
- pipx, poetry (pinned version), pre-commit (pinned version)
- OpenTofu (pinned version) - Terraform fork
- tflint (pinned version) - Terraform linter

This image follows the naming convention: `xep-[main image]-[flavor]:[upstream tag]`

All dependencies are pinned to specific versions for stability. This image is optimized for GitLab CI pre-commit jobs to avoid installing dependencies on every pipeline run.
