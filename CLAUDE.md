# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal "junk drawer" repository for small utility scripts and tools that solve specific problems. As described in the README, these are primarily single-use or small utility scripts, often ChatGPT-generated, saved for future reuse.

## Repository Structure

- **Root directory**: Contains standalone Python scripts
  - `getWordpressLinks.py` - WordPress post link harvester

- **Dropbox/**: Dropbox-related utilities
  - `dboxls` - Dropbox file listing utility (requires `dropbox` Python package)
  - `dropdeps` - Debian/Ubuntu dependency installer for old Dropbox installs
  - `dropinst` - Dropbox installation script for Linux x86_64

- **mybin/**: Collection of ~45 small utilities and installation scripts
  - Database migration tools: `mariadb2mysql`, `mysql2sqlite.sh`
  - Installation helpers: `dockinst`, `instclaude`, `ndinst`, `pbxinst`, `podinst`, `tinst`
  - Browser/proxy tools: `pchrome`
  - Configuration files: `tmux.conf`, `sysctl.conf`, `limits.conf`, `zfs.conf`, `fstab-nfs`
  - Various small utilities: mix of shell scripts and text snippets

## Key Characteristics

- **No build system**: This repository has no package.json, Makefile, or build configuration
- **No tests**: These are utility scripts without test infrastructure
- **Mixed languages**: Primarily bash scripts and Python, with some configuration files
- **Self-contained**: Each script is generally independent and self-documenting

## Working with Python Scripts

Python scripts may have dependencies noted in comments (e.g., `# pip install requests beautifulsoup4`). Install dependencies directly as needed:

```bash
pip install <package-name>
```

Example for WordPress harvester:
```bash
pip install requests beautifulsoup4
python getWordpressLinks.py <wordpress_site_url>
```

## Working with Shell Scripts

Most utilities in `mybin/` are shell scripts or installation snippets. They typically:
- Don't require execution permissions to be useful (many are copy/paste references)
- Contain installation commands or configuration snippets
- Are meant to be read and adapted rather than executed directly

## Security Note

Some scripts contain hardcoded credentials or tokens (e.g., `Dropbox/dboxls` has a Dropbox access token). These should be treated as examples and credentials should be rotated/removed before any production use or public sharing.