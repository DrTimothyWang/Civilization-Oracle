#!/usr/bin/env python3
"""
v14d_deploy_script.py — UPSI Dashboard Deployment Helper
=========================================================
Guides the user through creating a GitHub repo, initializing git,
setting the remote, pushing code, and verifying GitHub Actions.

Usage:
    python3 v14d_deploy_script.py

Requirements:
    - git installed locally
    - A GitHub account (free)
    - This script run from inside the v14d_dashboard_repo/ directory

No GitHub CLI or API tokens required.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_cmd(cmd: list, cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"   stderr: {result.stderr}")
        sys.exit(1)
    return result


def check_git() -> bool:
    """Check if git is installed."""
    result = subprocess.run(["git", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Git found: {result.stdout.strip()}")
        return True
    else:
        print("❌ Git is not installed or not in PATH.")
        print("   Please install git first: https://git-scm.com/downloads")
        return False


def main() -> int:
    print("=" * 60)
    print(" UPSI Dashboard v14d — GitHub Deployment Helper")
    print("=" * 60)
    print()

    # Determine repo directory
    script_dir = Path(__file__).parent.resolve()
    repo_dir = script_dir / "v14d_dashboard_repo"
    if not repo_dir.exists():
        # Maybe we are already inside the repo
        if (script_dir / "src").exists() and (script_dir / ".github").exists():
            repo_dir = script_dir
        else:
            print(f"❌ Could not find dashboard repo directory.")
            print(f"   Expected: {repo_dir}")
            print(f"   Please run this script from the v14_迭代研究/04_dashboard_deploy/ folder.")
            return 1

    print(f"📁 Dashboard repo directory: {repo_dir}")
    print()

    # Step 1: Check git
    if not check_git():
        return 1
    print()

    # Step 2: Check if already a git repo
    git_dir = repo_dir / ".git"
    if git_dir.exists():
        print("⚠️  This directory is already a git repository.")
        print("   If you want to start fresh, delete the .git/ folder first.")
        print()
    else:
        print("Step 1/5: Initializing local git repository...")
        run_cmd(["git", "init"], cwd=repo_dir)
        run_cmd(["git", "branch", "-M", "main"], cwd=repo_dir)
        print("✅ Local git repo initialized (branch: main)")
        print()

    # Step 3: Guide user to create GitHub repo
    print("-" * 60)
    print(" MANUAL STEP REQUIRED: Create a GitHub repository")
    print("-" * 60)
    print()
    print(" 1. Open https://github.com/new in your browser")
    print(" 2. Repository name: upsi-dashboard (or any name you prefer)")
    print(" 3. Select 'Public' (required for free GitHub Pages)")
    print(" 4. Check 'Add a README file'")
    print(" 5. Click 'Create repository'")
    print()
    username = input("Enter your GitHub username: ").strip()
    repo_name = input("Enter the repository name you chose [upsi-dashboard]: ").strip() or "upsi-dashboard"
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    print()
    print(f"🔗 Remote URL will be: {remote_url}")
    print()

    # Step 4: Add remote and push
    print("Step 2/5: Configuring remote origin...")
    # Remove existing remote if present
    subprocess.run(["git", "remote", "remove", "origin"], cwd=repo_dir, capture_output=True)
    run_cmd(["git", "remote", "add", "origin", remote_url], cwd=repo_dir)
    print("✅ Remote origin configured")
    print()

    print("Step 3/5: Staging files...")
    run_cmd(["git", "add", "."], cwd=repo_dir)
    print("✅ All files staged")
    print()

    print("Step 4/5: Committing...")
    run_cmd(["git", "commit", "-m", "Initial commit: UPSI Dashboard v14d"], cwd=repo_dir)
    print("✅ Commit created")
    print()

    print("Step 5/5: Pushing to GitHub...")
    print("   (You may be prompted for your GitHub username and password)")
    print("   Note: Use a Personal Access Token as your password if you have 2FA enabled.")
    print()
    result = subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_dir)
    if result.returncode != 0:
        print()
        print("❌ Push failed. Common causes:")
        print("   - Wrong username/password or token")
        print("   - Repository does not exist yet (create it first)")
        print("   - Remote URL is incorrect")
        print()
        print("To retry manually:")
        print(f"   cd {repo_dir}")
        print(f"   git push -u origin main")
        return 1
    print("✅ Code pushed to GitHub successfully!")
    print()

    # Step 5: Verify Actions
    print("=" * 60)
    print(" Post-Push Verification")
    print("=" * 60)
    print()
    print(" Next steps (manual):")
    print()
    print(" 1. Open your repo on GitHub:")
    print(f"    https://github.com/{username}/{repo_name}")
    print()
    print(" 2. Click the 'Actions' tab and enable workflows if prompted.")
    print()
    print(" 3. Trigger your first run:")
    print("    - Click 'UPSI Dashboard v14d' on the left")
    print("    - Click 'Run workflow' → 'Run workflow'")
    print()
    print(" 4. Wait for the green checkmark (≈ 3–5 minutes).")
    print()
    print(" 5. Enable GitHub Pages:")
    print("    - Go to Settings → Pages")
    print("    - Source: Deploy from a branch → gh-pages → / (root)")
    print("    - Click Save")
    print()
    print(" 6. View your live dashboard:")
    print(f"    https://{username}.github.io/{repo_name}/dashboard_latest.html")
    print()
    print("=" * 60)
    print(" Deployment helper finished!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
