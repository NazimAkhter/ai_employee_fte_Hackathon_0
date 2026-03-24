#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all watcher scripts.

Watchers monitor various inputs (email, files, APIs) and create
actionable markdown files in the Obsidian vault's /Needs_Action folder.

Usage:
    Create a subclass implementing check_for_updates() and create_action_file()
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
        # Create logs directory
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        # Add file handler
        log_file = logs_dir / f'{self.__class__.__name__.lower()}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items (format depends on implementation)
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file for the item.
        
        Args:
            item: Item to create action file for
            
        Returns:
            Path to created file
        """
        pass

    def run(self):
        """
        Main run loop. Continuously checks for updates and creates action files.
        
        Press Ctrl+C to stop.
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new item(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new items')
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            raise

    def generate_frontmatter(self, item_type: str, **kwargs) -> str:
        """
        Generate YAML frontmatter for action files.
        
        Args:
            item_type: Type of item (email, file, message, etc.)
            **kwargs: Additional metadata fields
            
        Returns:
            YAML frontmatter string
        """
        lines = ['---', f'type: {item_type}', f'created: {datetime.now().isoformat()}', 'status: pending']
        
        for key, value in kwargs.items():
            lines.append(f'{key}: {value}')
        
        lines.append('---')
        return '\n'.join(lines)

    def get_unique_filename(self, prefix: str, extension: str = '.md') -> Path:
        """
        Generate a unique filename in the Needs_Action folder.
        
        Args:
            prefix: Filename prefix
            extension: File extension (default: .md)
            
        Returns:
            Path to unique filename
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{prefix}_{timestamp}{extension}'
        filepath = self.needs_action / filename
        
        # Ensure uniqueness
        counter = 0
        while filepath.exists():
            counter += 1
            filename = f'{prefix}_{timestamp}_{counter}{extension}'
            filepath = self.needs_action / filename
        
        return filepath


if __name__ == '__main__':
    print("BaseWatcher is an abstract class. Create a subclass to use.")
    print("\nExample subclass:")
    print("""
class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Return list of new items
        return []
    
    def create_action_file(self, item) -> Path:
        # Create markdown file and return path
        content = self.generate_frontmatter('my_type', source='example')
        content += '\\n\\n# Action Required\\n\\nProcess this item.'
        filepath = self.get_unique_filename('MYITEM')
        filepath.write_text(content)
        return filepath
""")
