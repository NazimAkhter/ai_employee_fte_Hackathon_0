#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

When files are added to the watched folder, creates corresponding
action files in the Obsidian vault's /Needs_Action folder.

Usage:
    python filesystem_watcher.py <vault_path> [watch_folder] [check_interval]
    
Example:
    python filesystem_watcher.py "C:/Users/Name/ObsidianVault" "C:/Users/Name/DropFolder" 30
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

# Import base class
from base_watcher import BaseWatcher


class FilesystemWatcher(BaseWatcher):
    """
    Watches a folder for new files and creates action items in Obsidian.
    """

    def __init__(self, vault_path: str, watch_folder: str = None, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            watch_folder: Path to folder to watch (default: vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Set watch folder
        if watch_folder:
            self.watch_folder = Path(watch_folder)
        else:
            self.watch_folder = self.inbox
        
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by path + modified time
        self.processed_files = {}
        
        # Keywords for priority detection
        self.priority_keywords = ['urgent', 'asap', 'invoice', 'payment', 'receipt', 'contract']

    def check_for_updates(self) -> list:
        """
        Check for new files in the watch folder.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            for filepath in self.watch_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    # Get file signature (path + modified time)
                    try:
                        mtime = filepath.stat().st_mtime
                        file_sig = f"{filepath}:{mtime}"
                        
                        if file_sig not in self.processed_files:
                            new_files.append(filepath)
                    except (OSError, IOError) as e:
                        self.logger.warning(f'Could not stat file {filepath}: {e}')
        except Exception as e:
            self.logger.error(f'Error scanning watch folder: {e}')
        
        return new_files

    def create_action_file(self, filepath: Path) -> Path:
        """
        Create a markdown action file for the dropped file.
        
        Args:
            filepath: Path to the dropped file
            
        Returns:
            Path to created action file
        """
        # Get file info
        try:
            stat = filepath.stat()
            file_size = stat.st_size
            file_mtime = datetime.fromtimestamp(stat.st_mtime)
        except (OSError, IOError) as e:
            self.logger.error(f'Could not get file info: {e}')
            file_size = 0
            file_mtime = datetime.now()
        
        # Detect priority based on filename
        filename_lower = filepath.name.lower()
        priority = 'high' if any(kw in filename_lower for kw in self.priority_keywords) else 'normal'
        
        # Detect file type
        extension = filepath.suffix.lower()
        file_type_map = {
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.xls': 'Excel Spreadsheet',
            '.xlsx': 'Excel Spreadsheet',
            '.csv': 'CSV Data',
            '.txt': 'Text File',
            '.md': 'Markdown File',
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.gif': 'Image',
        }
        file_type = file_type_map.get(extension, 'Unknown Type')
        
        # Generate action type suggestion based on filename
        action_suggestions = self._suggest_actions(filepath.name)

        # Create frontmatter manually for proper YAML format
        frontmatter = f'''---
type: file_drop
original_name: "{filepath.name}"
file_type: "{file_type}"
file_size: {file_size}
received: {file_mtime.isoformat()}
priority: "{priority}"
source_folder: "{self.watch_folder}"
status: pending
---'''
        
        # Create content
        content = f'''{frontmatter}

# 📄 File Dropped for Processing

**File:** `{filepath.name}`  
**Type:** {file_type}  
**Size:** {self._format_size(file_size)}  
**Received:** {file_mtime.strftime('%Y-%m-%d %H:%M')}  
**Priority:** {"🔴" if priority == 'high' else '🟢'} {priority.title()}

---

## 📋 Description

A new file has been dropped into the watch folder and requires processing.

---

## ✅ Suggested Actions

{action_suggestions}

---

## 📝 Notes

<!-- Add any notes about this file here -->

---

## 🔗 File Location

- **Original:** `{filepath}`
- **Watch Folder:** `{self.watch_folder}`

---

*Action file created by Filesystem Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''
        
        # Generate unique filename
        safe_name = filepath.stem.replace(' ', '_').replace('-', '_')[:30]
        action_filepath = self.get_unique_filename(f'FILE_{safe_name}')

        # Write action file with UTF-8 encoding
        action_filepath.write_text(content, encoding='utf-8')
        
        # Mark as processed
        mtime = filepath.stat().st_mtime
        self.processed_files[f"{filepath}:{mtime}"] = action_filepath
        
        self.logger.info(f'Created action file for: {filepath.name}')
        
        return action_filepath

    def _suggest_actions(self, filename: str) -> str:
        """
        Suggest actions based on filename patterns.
        
        Args:
            filename: Name of the file
            
        Returns:
            Markdown list of suggested actions
        """
        filename_lower = filename.lower()
        suggestions = []
        
        if any(kw in filename_lower for kw in ['invoice', 'bill', 'receipt']):
            suggestions.append('- [ ] Review and categorize for accounting')
            suggestions.append('- [ ] Extract amount and vendor information')
            suggestions.append('- [ ] Move to /Accounting after processing')
        elif any(kw in filename_lower for kw in ['contract', 'agreement']):
            suggestions.append('- [ ] Review contract terms')
            suggestions.append('- [ ] Flag important dates or deadlines')
            suggestions.append('- [ ] Store in appropriate project folder')
        elif any(kw in filename_lower for kw in ['report', 'summary']):
            suggestions.append('- [ ] Read and summarize key points')
            suggestions.append('- [ ] Extract action items')
            suggestions.append('- [ ] Update Dashboard with findings')
        elif any(kw in filename_lower for kw in ['urgent', 'asap']):
            suggestions.append('- [ ] Process immediately')
            suggestions.append('- [ ] Determine required response')
            suggestions.append('- [ ] Escalate if needed')
        else:
            suggestions.append('- [ ] Review file contents')
            suggestions.append('- [ ] Determine appropriate action')
            suggestions.append('- [ ] Process and move to /Done when complete')
        
        return '\n'.join(suggestions)

    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python filesystem_watcher.py <vault_path> [watch_folder] [check_interval]")
        print("\nExample:")
        print('  python filesystem_watcher.py "C:/Users/Name/ObsidianVault"')
        print('  python filesystem_watcher.py "C:/Vault" "C:/DropFolder" 30')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    watch_folder = sys.argv[2] if len(sys.argv) > 2 else None
    check_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create and run watcher
    watcher = FilesystemWatcher(vault_path, watch_folder, check_interval)
    print(f"🔍 Filesystem Watcher starting...")
    print(f"   Vault: {vault_path}")
    print(f"   Watch Folder: {watch_folder or 'vault/Inbox'}")
    print(f"   Check Interval: {check_interval}s")
    print(f"\nPress Ctrl+C to stop\n")
    
    watcher.run()


if __name__ == '__main__':
    main()
