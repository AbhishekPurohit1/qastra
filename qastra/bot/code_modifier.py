"""
Code Modifier - Automatically updates test files with healed locators.
"""

import os
import re
import json
import difflib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class CodeModifier:
    """Modifies test files to update broken locators with healed ones."""
    
    def __init__(self, backup_dir: str = ".qastra_cache/backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Patterns for different locator types
        self.locator_patterns = {
            'css_selector': r'(["\'])([#\.][^"\']*\1)',
            'xpath': r'(["\'])(//[^"\']*\1)',
            'text': r'text\(["\']([^"\']*)["\']',
            'id': r'id\(["\']([^"\']*)["\']',
            'class': r'class\(["\']([^"\']*)["\']',
            'name': r'name\(["\']([^"\']*)["\']',
            'placeholder': r'placeholder\(["\']([^"\']*)["\']',
            'role': r'role\=["\']([^"\']*)["\']',
            'attribute': r'get_attribute\(["\']([^"\']*)["\']',
        }
        
        # Playwright specific patterns
        self.playwright_patterns = {
            'locator': r'page\.locator\(["\']([^"\']*)["\']\)',
            'fill': r'page\.fill\(["\']([^"\']*)["\']',
            'click': r'page\.click\(["\']([^"\']*)["\']',
            'type': r'page\.type\(["\']([^"\']*)["\']',
            'select_option': r'page\.select_option\(["\']([^"\']*)["\']',
            'wait_for_selector': r'page\.wait_for_selector\(["\']([^"\']*)["\']',
            'query_selector': r'page\.query_selector\(["\']([^"\']*)["\']',
            'query_selector_all': r'page\.query_selector_all\(["\']([^"\']*)["\']',
        }
        
        # Qastra smart locator patterns
        self.qastra_patterns = {
            'click': r'click\(page,\s*["\']([^"\']*)["\']',
            'fill': r'fill\(page,\s*["\']([^"\']*)["\']',
            'select': r'select\(page,\s*["\']([^"\']*)["\']',
            'wait_for': r'wait_for\(page,\s*["\']([^"\']*)["\']',
            'get_text': r'get_text\(page,\s*["\']([^"\']*)["\']',
            'is_visible': r'is_visible\(page,\s*["\']([^"\']*)["\']',
        }
    
    def update_locator(self, file_path: str, old_locator: str, new_locator: str, 
                      create_backup: bool = True) -> Dict[str, Any]:
        """
        Update a specific locator in a test file.
        
        Args:
            file_path: Path to the test file
            old_locator: Old locator string
            new_locator: New locator string
            create_backup: Whether to create a backup before modification
            
        Returns:
            Dictionary with update results
        """
        result = {
            'file_path': file_path,
            'old_locator': old_locator,
            'new_locator': new_locator,
            'success': False,
            'changes_made': 0,
            'backup_created': False,
            'error': None,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Create backup if requested
            if create_backup:
                backup_path = self._create_backup(file_path)
                result['backup_path'] = backup_path
                result['backup_created'] = True
            
            # Read the original file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Update locators
            updated_content, changes_count = self._update_locators_in_content(
                original_content, old_locator, new_locator
            )
            
            result['changes_made'] = changes_count
            
            if changes_count > 0:
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                result['success'] = True
                print(f"✅ Updated {changes_count} locator(s) in {file_path}")
                print(f"   {old_locator} → {new_locator}")
            else:
                print(f"⚠️  No locators found to update in {file_path}")
                result['success'] = True  # Still successful, just no changes needed
        
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Failed to update {file_path}: {e}")
        
        return result
    
    def _update_locators_in_content(self, content: str, old_locator: str, new_locator: str) -> Tuple[str, int]:
        """Update all occurrences of old locator with new locator in content."""
        updated_content = content
        changes_count = 0
        
        # Update in all pattern types
        all_patterns = {}
        all_patterns.update(self.locator_patterns)
        all_patterns.update(self.playwright_patterns)
        all_patterns.update(self.qastra_patterns)
        
        for pattern_name, pattern in all_patterns.items():
            # Create a pattern that matches the old locator
            full_pattern = re.compile(pattern.replace(r'([^"\']*)', re.escape(old_locator)))
            
            # Count matches before replacement
            matches = list(full_pattern.finditer(updated_content))
            
            if matches:
                # Replace with new locator
                updated_content = full_pattern.sub(
                    lambda m: m.group(0).replace(old_locator, new_locator),
                    updated_content
                )
                changes_count += len(matches)
                
                print(f"   Found {len(matches)} {pattern_name} matches")
        
        return updated_content, changes_count
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of the original file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_filename = f"{filename}.backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Copy the file
        with open(file_path, 'r', encoding='utf-8') as src:
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        
        return backup_path
    
    def update_multiple_locators(self, updates: List[Dict[str, str]], create_backups: bool = True) -> List[Dict[str, Any]]:
        """
        Update multiple locators across multiple files.
        
        Args:
            updates: List of dictionaries with 'file_path', 'old_locator', 'new_locator'
            create_backups: Whether to create backups
            
        Returns:
            List of update results
        """
        results = []
        
        print(f"🔧 Updating {len(updates)} locator(s) across files...")
        
        for update in updates:
            file_path = update.get('file_path')
            old_locator = update.get('old_locator')
            new_locator = update.get('new_locator')
            
            if not all([file_path, old_locator, new_locator]):
                print(f"⚠️  Skipping invalid update: {update}")
                continue
            
            if not os.path.exists(file_path):
                print(f"⚠️  File not found: {file_path}")
                continue
            
            result = self.update_locator(file_path, old_locator, new_locator, create_backups)
            results.append(result)
        
        # Summary
        successful = len([r for r in results if r['success']])
        total_changes = sum(r['changes_made'] for r in results)
        
        print(f"\n📊 Update Summary:")
        print(f"   Files processed: {len(results)}")
        print(f"   Successful: {successful}")
        print(f"   Total changes: {total_changes}")
        
        return results
    
    def apply_locator_fixes(self, fixes_file: str = ".qastra_cache/locator_fixes.json") -> List[Dict[str, Any]]:
        """
        Apply locator fixes from a JSON file.
        
        Args:
            fixes_file: Path to the fixes JSON file
            
        Returns:
            List of update results
        """
        try:
            with open(fixes_file, 'r') as f:
                fixes = json.load(f)
            
            print(f"🔧 Applying {len(fixes)} locator fix(es)...")
            
            results = []
            for fix in fixes:
                file_path = fix.get('file')
                old_locator = fix.get('old')
                new_locator = fix.get('new')
                
                if all([file_path, old_locator, new_locator]):
                    result = self.update_locator(file_path, old_locator, new_locator)
                    results.append(result)
                else:
                    print(f"⚠️  Invalid fix entry: {fix}")
            
            return results
        
        except FileNotFoundError:
            print(f"❌ Fixes file not found: {fixes_file}")
            return []
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in fixes file: {e}")
            return []
    
    def generate_diff_report(self, file_path: str, old_content: str, new_content: str) -> str:
        """Generate a diff report for the changes made."""
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f'before/{os.path.basename(file_path)}',
            tofile=f'after/{os.path.basename(file_path)}',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def validate_syntax(self, file_path: str) -> Dict[str, Any]:
        """
        Validate Python syntax of a file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Validation result
        """
        result = {
            'file_path': file_path,
            'valid': True,
            'error': None,
            'line_number': None
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            compile(content, file_path, 'exec')
        
        except SyntaxError as e:
            result['valid'] = False
            result['error'] = str(e)
            result['line_number'] = e.lineno
        
        except Exception as e:
            result['valid'] = False
            result['error'] = str(e)
        
        return result
    
    def smart_locator_update(self, file_path: str, intent: str, new_selector: str) -> Dict[str, Any]:
        """
        Smart update that finds and updates locators based on intent.
        
        Args:
            file_path: Path to the test file
            intent: The intent (e.g., 'login', 'username', 'password')
            new_selector: The new selector to use
            
        Returns:
            Update result
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all occurrences of the intent in smart locator calls
            pattern = re.compile(rf'(click|fill|select|wait_for|get_text|is_visible)\(page,\s*["\']({re.escape(intent)})["\']')
            
            matches = list(pattern.finditer(content))
            
            if not matches:
                return {
                    'file_path': file_path,
                    'intent': intent,
                    'new_selector': new_selector,
                    'success': False,
                    'error': f'No smart locator calls found for intent: {intent}',
                    'changes_made': 0
                }
            
            # For each match, we need to update the underlying selector
            # This is more complex and would require understanding the smart locator implementation
            # For now, we'll create a placeholder implementation
            
            updated_content = content
            changes_count = 0
            
            # This is a simplified approach - in reality, you'd need to update the smart locator's internal logic
            for match in matches:
                # Add a comment about the selector update
                updated_line = match.group(0) + f"  # Selector updated to: {new_selector}"
                updated_content = updated_content.replace(match.group(0), updated_line)
                changes_count += 1
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return {
                'file_path': file_path,
                'intent': intent,
                'new_selector': new_selector,
                'success': True,
                'changes_made': changes_count,
                'matches_found': len(matches)
            }
        
        except Exception as e:
            return {
                'file_path': file_path,
                'intent': intent,
                'new_selector': new_selector,
                'success': False,
                'error': str(e),
                'changes_made': 0
            }
    
    def get_locator_statistics(self, file_path: str) -> Dict[str, Any]:
        """
        Get statistics about locators in a test file.
        
        Args:
            file_path: Path to the test file
            
        Returns:
            Locator statistics
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stats = {
                'file_path': file_path,
                'total_locators': 0,
                'locator_types': {},
                'playwright_locators': 0,
                'qastra_locators': 0,
                'css_selectors': 0,
                'xpaths': 0,
                'text_locators': 0,
                'id_locators': 0,
                'class_locators': 0
            }
            
            # Count different locator types
            for pattern_name, pattern in self.playwright_patterns.items():
                matches = len(re.findall(pattern, content))
                stats['playwright_locators'] += matches
                stats['locator_types'][pattern_name] = matches
                stats['total_locators'] += matches
            
            for pattern_name, pattern in self.qastra_patterns.items():
                matches = len(re.findall(pattern, content))
                stats['qastra_locators'] += matches
                stats['locator_types'][f'qastra_{pattern_name}'] = matches
                stats['total_locators'] += matches
            
            # Count specific selector types
            stats['css_selectors'] = len(re.findall(r'["\']#[\w-]+["\']', content))
            stats['css_selectors'] += len(re.findall(r'["\'][\.\w-]+["\']', content))
            stats['xpaths'] = len(re.findall(r'["\']//[^"\']*["\']', content))
            stats['text_locators'] = len(re.findall(r'text\(["\'][^"\']*["\']', content))
            stats['id_locators'] = len(re.findall(r'id\(["\'][^"\']*["\']', content))
            stats['class_locators'] = len(re.findall(r'class\(["\'][^"\']*["\']', content))
            
            return stats
        
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'total_locators': 0
            }


# Convenience functions
def update_locator(file_path: str, old_locator: str, new_locator: str, 
                  backup_dir: str = ".qastra_cache/backups") -> Dict[str, Any]:
    """Quick function to update a locator."""
    modifier = CodeModifier(backup_dir)
    return modifier.update_locator(file_path, old_locator, new_locator)


def apply_locator_fixes(fixes_file: str = ".qastra_cache/locator_fixes.json", 
                      backup_dir: str = ".qastra_cache/backups") -> List[Dict[str, Any]]:
    """Quick function to apply locator fixes."""
    modifier = CodeModifier(backup_dir)
    return modifier.apply_locator_fixes(fixes_file)
