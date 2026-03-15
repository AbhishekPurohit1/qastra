"""
Maintenance Bot - Automatically fixes broken tests and creates pull requests.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from .code_modifier import CodeModifier
from .pr_creator import PRCreator


class MaintenanceBot:
    """AI-powered maintenance bot that automatically fixes broken tests."""
    
    def __init__(self, repo_path: str = ".", cache_dir: str = ".qastra_cache"):
        self.repo_path = repo_path
        self.cache_dir = cache_dir
        self.code_modifier = CodeModifier(os.path.join(cache_dir, "backups"))
        self.pr_creator = PRCreator(repo_path)
        
        # Create cache directories
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "backups"), exist_ok=True)
        
        # Configuration
        self.config = {
            'auto_commit': True,
            'auto_pr': True,
            'backup_enabled': True,
            'max_fixes_per_pr': 10,
            'pr_base_branch': 'main'
        }
    
    def load_locator_fixes(self, fixes_file: str = None) -> List[Dict[str, Any]]:
        """Load locator fixes from cache file."""
        if fixes_file is None:
            fixes_file = os.path.join(self.cache_dir, "locator_fixes.json")
        
        try:
            with open(fixes_file, 'r') as f:
                fixes = json.load(f)
            
            print(f"📋 Loaded {len(fixes)} locator fix(es) from {fixes_file}")
            return fixes
        
        except FileNotFoundError:
            print(f"⚠️  No fixes file found: {fixes_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in fixes file: {e}")
            return []
    
    def save_locator_fix(self, file_path: str, old_locator: str, new_locator: str, 
                        confidence: float = 0.0) -> str:
        """Save a locator fix to the cache."""
        fixes_file = os.path.join(self.cache_dir, "locator_fixes.json")
        
        # Load existing fixes
        fixes = []
        if os.path.exists(fixes_file):
            try:
                with open(fixes_file, 'r') as f:
                    fixes = json.load(f)
            except:
                fixes = []
        
        # Add new fix
        fix = {
            'file_path': file_path,
            'old_locator': old_locator,
            'new_locator': new_locator,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'applied': False
        }
        
        fixes.append(fix)
        
        # Save updated fixes
        with open(fixes_file, 'w') as f:
            json.dump(fixes, f, indent=2)
        
        print(f"💾 Saved locator fix: {old_locator} → {new_locator}")
        return fixes_file
    
    def apply_fixes(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply locator fixes to test files."""
        print(f"🔧 Applying {len(fixes)} locator fix(es)...")
        
        # Filter fixes that haven't been applied yet
        pending_fixes = [f for f in fixes if not f.get('applied', False)]
        
        if not pending_fixes:
            print("✅ All fixes have already been applied")
            return []
        
        # Apply fixes using code modifier
        updates = []
        for fix in pending_fixes:
            update_result = self.code_modifier.update_locator(
                fix['file_path'],
                fix['old_locator'],
                fix['new_locator'],
                self.config['backup_enabled']
            )
            
            # Mark fix as applied if successful
            if update_result['success']:
                fix['applied'] = True
                fix['applied_at'] = datetime.now().isoformat()
            
            updates.append(update_result)
        
        # Update fixes file with applied status
        self._update_fixes_status(fixes)
        
        return updates
    
    def _update_fixes_status(self, fixes: List[Dict[str, Any]]):
        """Update the status of fixes in the cache file."""
        fixes_file = os.path.join(self.cache_dir, "locator_fixes.json")
        
        with open(fixes_file, 'w') as f:
            json.dump(fixes, f, indent=2)
    
    def commit_changes(self, fixes: List[Dict[str, Any]]) -> bool:
        """Commit the applied fixes."""
        if not self.config['auto_commit']:
            print("⏸️  Auto-commit disabled")
            return False
        
        # Check if there are changes to commit
        git_status = self.pr_creator.check_git_status()
        
        if not git_status['has_changes']:
            print("⚠️  No changes to commit")
            return False
        
        # Generate commit message
        applied_fixes = [f for f in fixes if f.get('applied', False)]
        commit_message = f"🤖 Qastra auto-fix: Update {len(applied_fixes)} broken locator(s)"
        
        # Add details to commit message
        if len(applied_fixes) <= 3:
            for fix in applied_fixes:
                file_name = os.path.basename(fix['file_path'])
                commit_message += f"\n  - {file_name}: {fix['old_locator']} → {fix['new_locator']}"
        
        author = "Qastra Bot <bot@qastra.ai>"
        
        success = self.pr_creator.commit_changes(commit_message, author)
        
        if success:
            print(f"✅ Committed {len(applied_fixes)} fix(es)")
        
        return success
    
    def create_pull_request(self, fixes: List[Dict[str, Any]]) -> bool:
        """Create a pull request for the fixes."""
        if not self.config['auto_pr']:
            print("⏸️  Auto-PR disabled")
            return False
        
        # Check if we have too many fixes for one PR
        applied_fixes = [f for f in fixes if f.get('applied', False)]
        
        if len(applied_fixes) > self.config['max_fixes_per_pr']:
            print(f"⚠️  Too many fixes ({len(applied_fixes)}) for single PR")
            print(f"   Consider batching into multiple PRs")
            return False
        
        # Create PR
        success = self.pr_creator.create_auto_fix_pr(applied_fixes)
        
        if success:
            print(f"✅ Created PR for {len(applied_fixes)} fix(es)")
        
        return success
    
    def run_maintenance_cycle(self) -> Dict[str, Any]:
        """Run a complete maintenance cycle."""
        print("🤖 Qastra Maintenance Bot Starting...")
        print("=" * 50)
        
        cycle_result = {
            'start_time': datetime.now().isoformat(),
            'fixes_loaded': 0,
            'fixes_applied': 0,
            'changes_committed': False,
            'pr_created': False,
            'success': False,
            'error': None
        }
        
        try:
            # Load fixes
            fixes = self.load_locator_fixes()
            cycle_result['fixes_loaded'] = len(fixes)
            
            if not fixes:
                print("✅ No fixes to apply - maintenance complete")
                cycle_result['success'] = True
                return cycle_result
            
            # Apply fixes
            updates = self.apply_fixes(fixes)
            applied_count = len([u for u in updates if u['success']])
            cycle_result['fixes_applied'] = applied_count
            
            if applied_count == 0:
                print("⚠️  No fixes were successfully applied")
                cycle_result['success'] = True
                return cycle_result
            
            # Commit changes
            if self.commit_changes(fixes):
                cycle_result['changes_committed'] = True
            
            # Create PR
            if self.create_pull_request(fixes):
                cycle_result['pr_created'] = True
            
            cycle_result['success'] = True
            
            print("\n✅ Maintenance cycle completed successfully!")
            print(f"   Fixes loaded: {cycle_result['fixes_loaded']}")
            print(f"   Fixes applied: {cycle_result['fixes_applied']}")
            print(f"   Changes committed: {cycle_result['changes_committed']}")
            print(f"   PR created: {cycle_result['pr_created']}")
        
        except Exception as e:
            cycle_result['error'] = str(e)
            print(f"❌ Maintenance cycle failed: {e}")
        
        finally:
            cycle_result['end_time'] = datetime.now().isoformat()
            
            # Save cycle results
            self._save_cycle_results(cycle_result)
        
        return cycle_result
    
    def _save_cycle_results(self, results: Dict[str, Any]):
        """Save maintenance cycle results."""
        results_file = os.path.join(self.cache_dir, "maintenance_results.json")
        
        try:
            # Load existing results
            existing_results = []
            if os.path.exists(results_file):
                with open(results_file, 'r') as f:
                    existing_results = json.load(f)
            
            # Add new results
            existing_results.append(results)
            
            # Keep only last 10 results
            if len(existing_results) > 10:
                existing_results = existing_results[-10:]
            
            # Save updated results
            with open(results_file, 'w') as f:
                json.dump(existing_results, f, indent=2, default=str)
        
        except Exception as e:
            print(f"❌ Failed to save cycle results: {e}")
    
    def add_fix_from_test_failure(self, test_file: str, failed_locator: str, 
                                 healed_locator: str, confidence: float = 0.0):
        """Add a fix from a test failure."""
        print(f"🔧 Adding fix from test failure:")
        print(f"   File: {test_file}")
        print(f"   Failed: {failed_locator}")
        print(f"   Healed: {healed_locator}")
        print(f"   Confidence: {confidence:.2f}")
        
        self.save_locator_fix(test_file, failed_locator, healed_locator, confidence)
    
    def get_maintenance_status(self) -> Dict[str, Any]:
        """Get current maintenance status."""
        status = {
            'cache_directory': self.cache_dir,
            'config': self.config,
            'pending_fixes': 0,
            'applied_fixes': 0,
            'last_cycle': None,
            'git_status': None
        }
        
        # Count fixes
        fixes = self.load_locator_fixes()
        status['pending_fixes'] = len([f for f in fixes if not f.get('applied', False)])
        status['applied_fixes'] = len([f for f in fixes if f.get('applied', False)])
        
        # Get last cycle results
        results_file = os.path.join(self.cache_dir, "maintenance_results.json")
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r') as f:
                    results = json.load(f)
                if results:
                    status['last_cycle'] = results[-1]
            except:
                pass
        
        # Get git status
        status['git_status'] = self.pr_creator.check_git_status()
        
        return status
    
    def print_status(self):
        """Print current maintenance status."""
        status = self.get_maintenance_status()
        
        print("🤖 Qastra Maintenance Bot Status")
        print("=" * 40)
        print(f"Cache directory: {status['cache_directory']}")
        print(f"Pending fixes: {status['pending_fixes']}")
        print(f"Applied fixes: {status['applied_fixes']}")
        
        git_status = status['git_status']
        if git_status['is_git_repo']:
            print(f"Git branch: {git_status['current_branch']}")
            print(f"Has changes: {git_status['has_changes']}")
        else:
            print("Git: Not a repository")
        
        if status['last_cycle']:
            last_cycle = status['last_cycle']
            print(f"Last cycle: {last_cycle['end_time']}")
            print(f"Last result: {'Success' if last_cycle['success'] else 'Failed'}")
        
        print(f"\nConfiguration:")
        print(f"  Auto-commit: {status['config']['auto_commit']}")
        print(f"  Auto-PR: {status['config']['auto_pr']}")
        print(f"  Backups: {status['config']['backup_enabled']}")
    
    def configure(self, **kwargs):
        """Update bot configuration."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                print(f"✅ Updated {key}: {value}")
            else:
                print(f"⚠️  Unknown config key: {key}")
    
    def cleanup_old_backups(self, keep_days: int = 7):
        """Clean up old backup files."""
        backup_dir = self.code_modifier.backup_dir
        
        if not os.path.exists(backup_dir):
            return
        
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        cleaned_files = 0
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned_files += 1
                except:
                    continue
        
        if cleaned_files > 0:
            print(f"🧹 Cleaned up {cleaned_files} old backup files")


# Convenience functions
def run_maintenance_bot(repo_path: str = ".", cache_dir: str = ".qastra_cache") -> Dict[str, Any]:
    """Quick function to run the maintenance bot."""
    bot = MaintenanceBot(repo_path, cache_dir)
    return bot.run_maintenance_cycle()


def add_locator_fix(test_file: str, failed_locator: str, healed_locator: str, 
                   confidence: float = 0.0, cache_dir: str = ".qastra_cache") -> str:
    """Quick function to add a locator fix."""
    bot = MaintenanceBot(cache_dir=cache_dir)
    return bot.add_fix_from_test_failure(test_file, failed_locator, healed_locator, confidence)
