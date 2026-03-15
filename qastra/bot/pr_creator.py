"""
PR Creator - Automatically creates pull requests for test fixes on GitHub.
"""

import os
import subprocess
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class PRCreator:
    """Creates pull requests for automatic test fixes."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.branch_prefix = "qastra-auto-fix"
        
    def check_git_status(self) -> Dict[str, Any]:
        """Check if we're in a git repository and get status."""
        result = {
            'is_git_repo': False,
            'has_changes': False,
            'current_branch': None,
            'remote_url': None,
            'error': None
        }
        
        try:
            # Check if we're in a git repo
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         check=True, capture_output=True, cwd=self.repo_path)
            result['is_git_repo'] = True
            
            # Get current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                          capture_output=True, text=True, cwd=self.repo_path)
            result['current_branch'] = branch_result.stdout.strip()
            
            # Check if there are changes
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                           capture_output=True, text=True, cwd=self.repo_path)
            result['has_changes'] = len(status_result.stdout.strip()) > 0
            
            # Get remote URL
            remote_result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                          capture_output=True, text=True, cwd=self.repo_path)
            if remote_result.returncode == 0:
                result['remote_url'] = remote_result.stdout.strip()
        
        except subprocess.CalledProcessError as e:
            result['error'] = str(e)
        
        return result
    
    def create_branch(self, branch_name: str) -> bool:
        """Create and checkout a new branch."""
        try:
            # Create and checkout new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         check=True, cwd=self.repo_path)
            print(f"✅ Created and checked out branch: {branch_name}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            return False
    
    def commit_changes(self, message: str, author: Optional[str] = None) -> bool:
        """Commit changes with a message."""
        try:
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True, cwd=self.repo_path)
            
            # Commit with message
            commit_cmd = ['git', 'commit', '-m', message]
            if author:
                commit_cmd.extend(['--author', author])
            
            subprocess.run(commit_cmd, check=True, cwd=self.repo_path)
            print(f"✅ Committed changes: {message}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to commit changes: {e}")
            return False
    
    def push_branch(self, branch_name: str) -> bool:
        """Push branch to remote repository."""
        try:
            subprocess.run(['git', 'push', '-u', 'origin', branch_name], 
                         check=True, cwd=self.repo_path)
            print(f"✅ Pushed branch: {branch_name}")
            return True
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to push branch: {e}")
            return False
    
    def create_pr_with_gh_cli(self, title: str, body: str, head: str, base: str = 'main') -> bool:
        """Create pull request using GitHub CLI."""
        try:
            # Check if gh CLI is available
            subprocess.run(['gh', '--version'], check=True, capture_output=True)
            
            # Create PR
            cmd = [
                'gh', 'pr', 'create',
                '--title', title,
                '--body', body,
                '--head', head,
                '--base', base
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                print(f"✅ Pull request created: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Failed to create PR: {result.stderr}")
                return False
        
        except subprocess.CalledProcessError as e:
            if e.returncode == 127:  # Command not found
                print("❌ GitHub CLI (gh) not found. Install with: brew install gh")
                return False
            else:
                print(f"❌ GitHub CLI error: {e}")
                return False
    
    def create_pr_with_git_commands(self, title: str, body: str, head: str, base: str = 'main') -> bool:
        """Create pull request using git commands (fallback method)."""
        try:
            # This is a simplified fallback - in reality, you'd need to use GitHub API
            # For now, we'll just print the PR information
            
            print(f"📋 Pull Request Information:")
            print(f"   Title: {title}")
            print(f"   Body: {body}")
            print(f"   Head: {head}")
            print(f"   Base: {base}")
            print(f"   Please create the PR manually on GitHub")
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to create PR info: {e}")
            return False
    
    def create_pr(self, title: str, body: str, head: str, base: str = 'main') -> bool:
        """Create pull request using available method."""
        # Try GitHub CLI first
        if self.create_pr_with_gh_cli(title, body, head, base):
            return True
        
        # Fallback to git commands
        return self.create_pr_with_git_commands(title, body, head, base)
    
    def create_auto_fix_pr(self, fixes: List[Dict[str, Any]], repo_url: Optional[str] = None) -> bool:
        """Create a pull request for automatic locator fixes."""
        # Generate branch name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        branch_name = f"{self.branch_prefix}_{timestamp}"
        
        # Generate PR title and body
        title = "🤖 Qastra Auto-Fix: Updated Broken Locators"
        
        body_parts = [
            "## 🤖 Automatic Test Fix",
            "",
            f"This PR was automatically created by Qastra's Maintenance Bot.",
            f"Fixed {len(fixes)} broken locator(s) that were causing test failures.",
            "",
            "### 🔧 Changes Made:"
        ]
        
        for fix in fixes:
            file_path = fix.get('file_path', 'Unknown')
            old_locator = fix.get('old_locator', 'Unknown')
            new_locator = fix.get('new_locator', 'Unknown')
            changes = fix.get('changes_made', 0)
            
            body_parts.extend([
                f"- **{os.path.basename(file_path)}**: {changes} change(s)",
                f"  - `{old_locator}` → `{new_locator}`"
            ])
        
        body_parts.extend([
            "",
            "### 🧪 Testing",
            "- All affected tests should now pass",
            "- No functional changes, only locator updates",
            "- Self-healing engine verified the new locators",
            "",
            "### 🤖 About Qastra Auto-Fix",
            "Qastra's Maintenance Bot automatically detects and fixes broken locators:",
            "1. Tests are run and failures are detected",
            "2. Self-healing engine finds correct elements", 
            "3. Locators are updated in test files",
            "4. Pull request is created for review",
            "",
            "---",
            f"*Generated by Qastra v1.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        body = "\n".join(body_parts)
        
        # Check git status
        git_status = self.check_git_status()
        
        if not git_status['is_git_repo']:
            print("❌ Not in a git repository")
            return False
        
        if not git_status['has_changes']:
            print("⚠️  No changes to commit")
            return False
        
        # Create branch
        if not self.create_branch(branch_name):
            return False
        
        # Commit changes
        commit_message = f"🤖 Qastra auto-fix: Update {len(fixes)} broken locator(s)"
        author = "Qastra Bot <bot@qastra.ai>"
        
        if not self.commit_changes(commit_message, author):
            return False
        
        # Push branch
        if not self.push_branch(branch_name):
            return False
        
        # Create PR
        if self.create_pr(title, body, branch_name):
            return True
        
        return False
    
    def save_pr_info(self, pr_info: Dict[str, Any], output_file: str = ".qastra_cache/pr_info.json"):
        """Save PR information to a file."""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(pr_info, f, indent=2, default=str)
            
            print(f"💾 PR info saved: {output_file}")
        
        except Exception as e:
            print(f"❌ Failed to save PR info: {e}")
    
    def get_pr_status(self, pr_number: Optional[str] = None) -> Dict[str, Any]:
        """Get status of pull requests."""
        try:
            if pr_number:
                # Get specific PR
                result = subprocess.run(['gh', 'pr', 'view', pr_number, '--json', 'number,title,state,url'], 
                                      capture_output=True, text=True, cwd=self.repo_path)
                if result.returncode == 0:
                    return json.loads(result.stdout)
            else:
                # Get all PRs
                result = subprocess.run(['gh', 'pr', 'list', '--json', 'number,title,state,url'], 
                                      capture_output=True, text=True, cwd=self.repo_path)
                if result.returncode == 0:
                    return json.loads(result.stdout)
        
        except Exception as e:
            print(f"❌ Failed to get PR status: {e}")
        
        return {'error': str(e)}
    
    def merge_pr(self, pr_number: str, merge_method: str = 'squash') -> bool:
        """Merge a pull request."""
        try:
            cmd = ['gh', 'pr', 'merge', pr_number, '--merge-method', merge_method, '--delete-branch']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode == 0:
                print(f"✅ Merged PR #{pr_number}")
                return True
            else:
                print(f"❌ Failed to merge PR: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to merge PR: {e}")
            return False
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are available."""
        deps = {
            'git': False,
            'gh_cli': False
        }
        
        try:
            subprocess.run(['git', '--version'], check=True, capture_output=True)
            deps['git'] = True
        except:
            pass
        
        try:
            subprocess.run(['gh', '--version'], check=True, capture_output=True)
            deps['gh_cli'] = True
        except:
            pass
        
        return deps
    
    def setup_environment(self) -> bool:
        """Set up the environment for PR creation."""
        deps = self.check_dependencies()
        
        if not deps['git']:
            print("❌ Git is not installed or not in PATH")
            return False
        
        if not deps['gh_cli']:
            print("⚠️  GitHub CLI (gh) not found. Install with: brew install gh")
            print("   You can still create PRs manually")
        
        return True


# Convenience functions
def create_auto_fix_pr(fixes: List[Dict[str, Any]], repo_path: str = ".") -> bool:
    """Quick function to create an auto-fix PR."""
    creator = PRCreator(repo_path)
    return creator.create_auto_fix_pr(fixes)


def check_git_status(repo_path: str = ".") -> Dict[str, Any]:
    """Quick function to check git status."""
    creator = PRCreator(repo_path)
    return creator.check_git_status()
