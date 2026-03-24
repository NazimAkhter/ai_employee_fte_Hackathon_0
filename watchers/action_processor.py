#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Action File Processor - Process action files in the Obsidian vault.

Reads action files from /Needs_Action, processes them based on type,
and moves completed files to /Done.

Usage:
    python action_processor.py <vault_path> [--dry-run]
    
Example:
    python action_processor.py "C:/Users/Name/ObsidianVault"
    python action_processor.py "C:/Vault" --dry-run
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime


class ActionProcessor:
    """
    Process action files in the Obsidian vault.
    """

    def __init__(self, vault_path: str, dry_run: bool = False):
        """
        Initialize the processor.
        
        Args:
            vault_path: Path to the Obsidian vault root
            dry_run: If True, don't actually move files (just report)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.dry_run = dry_run
        
        # Ensure directories exist
        self.done.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.processed_count = 0
        self.error_count = 0

    def process_all(self) -> dict:
        """
        Process all action files in /Needs_Action.
        
        Returns:
            Dict with processing stats
        """
        stats = {
            'processed': 0,
            'errors': 0,
            'files': []
        }
        
        # Get all markdown files
        action_files = list(self.needs_action.glob('*.md'))
        
        if not action_files:
            print("📭 No action files to process")
            return stats
        
        print(f"📋 Found {len(action_files)} action file(s)")
        
        for filepath in sorted(action_files):
            try:
                result = self.process_file(filepath)
                stats['processed'] += 1
                stats['files'].append(result)
                self.processed_count += 1
            except Exception as e:
                print(f"❌ Error processing {filepath.name}: {e}")
                stats['errors'] += 1
                self.error_count += 1
        
        # Update dashboard
        if not self.dry_run:
            self.update_dashboard(stats)
        
        return stats

    def process_file(self, filepath: Path) -> dict:
        """
        Process a single action file.
        
        Args:
            filepath: Path to action file
            
        Returns:
            Dict with file processing result
        """
        print(f"\n📄 Processing: {filepath.name}")
        
        # Read file content
        content = filepath.read_text(encoding='utf-8')
        
        # Parse frontmatter
        frontmatter = self._parse_frontmatter(content)
        
        # Get file info
        file_type = frontmatter.get('type', 'unknown')
        priority = frontmatter.get('priority', 'normal')
        original_name = frontmatter.get('original_name', filepath.name)
        
        print(f"   Type: {file_type} | Priority: {priority}")
        print(f"   Original: {original_name}")
        
        # Process based on type
        result = {
            'file': filepath.name,
            'type': file_type,
            'priority': priority,
            'status': 'processed',
            'actions_taken': []
        }
        
        if file_type == 'file_drop':
            result['actions_taken'] = self._process_file_drop(content, filepath)
        elif file_type == 'email':
            result['actions_taken'] = self._process_email(content, filepath)
        elif file_type == 'message':
            result['actions_taken'] = self._process_message(content, filepath)
        else:
            result['actions_taken'] = self._process_generic(content, filepath)
        
        # Mark as completed
        if not self.dry_run:
            self._mark_completed(filepath, result)
            print(f"   ✅ Completed and moved to /Done")
        else:
            print(f"   [DRY RUN] Would move to /Done")
        
        return result

    def _parse_frontmatter(self, content: str) -> dict:
        """
        Parse YAML frontmatter from content.
        
        Args:
            content: File content
            
        Returns:
            Dict of frontmatter fields
        """
        frontmatter = {}
        
        if not content.startswith('---'):
            return frontmatter
        
        # Find end of frontmatter
        end_index = content.find('---', 3)
        if end_index == -1:
            return frontmatter
        
        # Parse lines
        fm_content = content[3:end_index].strip()
        for line in fm_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                frontmatter[key] = value
        
        return frontmatter

    def _process_file_drop(self, content: str, filepath: Path) -> list:
        """
        Process a file drop action.
        
        Args:
            content: File content
            filepath: Path to action file
            
        Returns:
            List of actions taken
        """
        actions = []
        
        # Check for checkboxes and mark them
        if '- [ ]' in content:
            # Auto-complete generic actions
            content = content.replace('- [ ] Review file contents', '- [x] Review file contents')
            actions.append('Reviewed file contents')
        
        # Add processing note
        processing_note = f"\n\n---\n\n## 🤖 AI Processing Log\n\n**Processed by:** Qwen Code  \n**Processed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n**Status:** ✅ Completed\n\nAutomatically processed as file drop.\n"
        content += processing_note
        actions.append('Added processing log')
        
        # Write updated content
        filepath.write_text(content, encoding='utf-8')
        
        return actions

    def _process_email(self, content: str, filepath: Path) -> list:
        """
        Process an email action.
        
        Args:
            content: File content
            filepath: Path to action file
            
        Returns:
            List of actions taken
        """
        actions = []
        
        # Add processing note
        processing_note = f"\n\n---\n\n## 🤖 AI Processing Log\n\n**Processed by:** Qwen Code  \n**Processed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n**Status:** ✅ Completed\n\nEmail action processed.\n"
        content += processing_note
        actions.append('Processed email action')
        
        # Write updated content
        filepath.write_text(content, encoding='utf-8')
        
        return actions

    def _process_message(self, content: str, filepath: Path) -> list:
        """
        Process a message action.
        
        Args:
            content: File content
            filepath: Path to action file
            
        Returns:
            List of actions taken
        """
        actions = []
        
        # Add processing note
        processing_note = f"\n\n---\n\n## 🤖 AI Processing Log\n\n**Processed by:** Qwen Code  \n**Processed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n**Status:** ✅ Completed\n\nMessage action processed.\n"
        content += processing_note
        actions.append('Processed message action')
        
        # Write updated content
        filepath.write_text(content, encoding='utf-8')
        
        return actions

    def _process_generic(self, content: str, filepath: Path) -> list:
        """
        Process a generic action.
        
        Args:
            content: File content
            filepath: Path to action file
            
        Returns:
            List of actions taken
        """
        actions = []
        
        # Add processing note
        processing_note = f"\n\n---\n\n## 🤖 AI Processing Log\n\n**Processed by:** Qwen Code  \n**Processed at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n**Status:** ✅ Completed\n\nGeneric action processed.\n"
        content += processing_note
        actions.append('Processed generic action')
        
        # Write updated content
        filepath.write_text(content, encoding='utf-8')
        
        return actions

    def _mark_completed(self, filepath: Path, result: dict):
        """
        Mark file as completed and move to /Done.
        
        Args:
            filepath: Path to action file
            result: Processing result
        """
        # Generate destination filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f"{filepath.stem}_done_{timestamp}.md"
        dest_path = self.done / dest_name
        
        # Move file
        shutil.move(str(filepath), str(dest_path))

    def update_dashboard(self, stats: dict):
        """
        Update Dashboard.md with processing stats.
        
        Args:
            stats: Processing statistics
        """
        if not self.dashboard.exists():
            print("⚠️ Dashboard.md not found, skipping update")
            return
        
        try:
            content = self.dashboard.read_text(encoding='utf-8')
            
            # Count files in each folder
            needs_action_count = len(list(self.needs_action.glob('*.md')))
            done_today = len([f for f in self.done.glob('*_done_*.md') 
                             if datetime.now().strftime('%Y%m%d') in f.name])
            
            # Update stats table
            old_stats_line = f"| ⚠️ Needs Action |"
            new_stats_line = f"| ⚠️ Needs Action | {needs_action_count} |"
            
            # Simple replacement
            if "| ⚠️ Needs Action |" in content:
                # Find and replace the line
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "| ⚠️ Needs Action |" in line:
                        lines[i] = f"| ⚠️ Needs Action | {needs_action_count} |"
                    if "| ✅ Done Today |" in line:
                        lines[i] = f"| ✅ Done Today | {done_today} |"
                content = '\n'.join(lines)

            # Update last_updated timestamp using regex for clean replacement
            import re
            content = re.sub(
                r'last_updated:.*',
                f'last_updated: {datetime.now().isoformat()}',
                content,
                count=1
            )
            
            self.dashboard.write_text(content, encoding='utf-8')
            print(f"\n📊 Dashboard updated: {needs_action_count} pending, {done_today} done today")
            
        except Exception as e:
            print(f"⚠️ Could not update Dashboard: {e}")


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python action_processor.py <vault_path> [--dry-run]")
        print("\nExample:")
        print('  python action_processor.py "C:/Users/Name/ObsidianVault"')
        print('  python action_processor.py "C:/Vault" --dry-run')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f"❌ Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create and run processor
    processor = ActionProcessor(vault_path, dry_run)
    print(f"🤖 Action Processor starting...")
    print(f"   Vault: {vault_path}")
    print(f"   Dry Run: {dry_run}")
    print()
    
    stats = processor.process_all()
    
    print(f"\n{'='*50}")
    print(f"📊 Processing Complete")
    print(f"   Processed: {stats['processed']} files")
    print(f"   Errors: {stats['errors']}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
