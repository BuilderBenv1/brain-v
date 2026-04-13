#!/bin/bash

# Project Brain — Setup Script
# Works on: Mac, Linux, Windows (Git Bash / WSL)
# Run once from the project-brain folder

echo "Setting up Project Brain..."

# Create folder structure
mkdir -p raw/architecture
mkdir -p raw/signals
mkdir -p raw/conversations
mkdir -p raw/research
mkdir -p wiki/layers
mkdir -p wiki/components
mkdir -p wiki/people
mkdir -p wiki/concepts
mkdir -p wiki/gaps
mkdir -p outputs/posts
mkdir -p outputs/reports
mkdir -p outputs/predictions

echo "Folders created."
echo ""
echo "Project Brain is ready."
echo ""
echo "Next: open Claude Code in this folder"
echo "  cd project-brain"
echo "  claude"
echo ""
echo "Then paste the wake-up prompt from GETTING-STARTED.md"
