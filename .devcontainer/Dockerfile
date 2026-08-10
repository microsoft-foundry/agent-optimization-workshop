# Agent Optimization Workshop — dev container image.
#
# Base image is pinned here so we can customize freely later (system packages,
# CLIs, tools) without touching devcontainer.json. Post-create actions (env
# activation, azd extensions, first-time verifications) live in post-create.sh.

FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# System tools we use across labs: curl (already present), jq (parsing outputs),
# git (already present), zip/unzip (bundling artifacts).
#
# The base image pre-configures the Yarn apt repo, whose signing key has since
# rotated and now breaks `apt-get update` (NO_PUBKEY 62D54FD4003F6525). We don't
# use Yarn, so remove that source before updating.
RUN rm -f /etc/apt/sources.list.d/yarn.list /usr/share/keyrings/yarn*.gpg \
    && apt-get update && apt-get install -y --no-install-recommends \
      jq \
      zip \
      unzip \
    && rm -rf /var/lib/apt/lists/*

# Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Azure Developer CLI (azd)
RUN curl -fsSL https://aka.ms/install-azd.sh | bash

# GitHub CLI
RUN (type -p wget >/dev/null || apt-get install -y wget) \
    && mkdir -p -m 755 /etc/apt/keyrings \
    && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Base Python packages (kept small; requirements.txt / requirements-dev.txt
# install lab-specific deps in post-create.sh).
RUN pip install --upgrade pip

WORKDIR /workspaces
