#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Monitors LinkedIn for notifications, messages, and engagement.

Uses Playwright browser automation to check LinkedIn for:
- New connection requests
- Messages
- Post engagement (likes, comments)
- Job alerts

When activity is detected, creates action files in the Obsidian vault.

Usage:
    python linkedin_watcher.py <vault_path> [session_path] [check_interval]
    
Example:
    python linkedin_watcher.py "C:/Users/Name/ObsidianVault" "C:/Users/Name/linkedin_session" 300
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import base class
from base_watcher import BaseWatcher

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for notifications, messages, and engagement.
    """

    LINKEDIN_URL = 'https://www.linkedin.com'
    LINKEDIN_MESSAGES_URL = 'https://www.linkedin.com/messaging'
    LINKEDIN_NOTIFICATIONS_URL = 'https://www.linkedin.com/notifications'

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        """
        Initialize the LinkedIn watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to store browser session (default: vault/.linkedin_session)
            check_interval: Seconds between checks (default: 300 = 5 min)
        """
        super().__init__(vault_path, check_interval)
        
        # Set session path
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path / '.linkedin_session'
        
        # Ensure session path exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords for priority detection
        self.priority_keywords = ['urgent', 'asap', 'interview', 'job', 'opportunity',
                                   'hiring', 'position', 'role', 'meeting']
        
        # Track processed items
        self.processed_notifications = set()
        self.processed_messages = set()
        
        # Load processed items from cache
        self._load_cache()
        
        # Browser context
        self.browser_context = None
        self.page = None

    def _load_cache(self):
        """Load processed items from cache file."""
        cache_file = Path(__file__).parent / 'linkedin_processed_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.processed_notifications = set(data.get('notifications', []))
                    self.processed_messages = set(data.get('messages', []))
                self.logger.info(f'Loaded LinkedIn cache: {len(self.processed_notifications)} notifications, {len(self.processed_messages)} messages')
            except Exception as e:
                self.logger.warning(f'Could not load LinkedIn cache: {e}')

    def _save_cache(self):
        """Save processed items to cache file."""
        cache_file = Path(__file__).parent / 'linkedin_processed_cache.json'
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'notifications': list(self.processed_notifications),
                    'messages': list(self.processed_messages)
                }, f)
        except Exception as e:
            self.logger.warning(f'Could not save LinkedIn cache: {e}')

    def _init_browser(self):
        """Initialize browser with persistent session."""
        try:
            playwright = sync_playwright().start()
            # Use headless=False for first run so user can log in
            self.browser_context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,  # Visible browser for login
                ignore_default_args=['--enable-automation'],
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox'
                ]
            )
            self.page = self.browser_context.pages[0] if self.browser_context.pages else self.browser_context.new_page()
            
            # Handle popup windows (for Google OAuth)
            def handle_popup(popup):
                self.logger.info('Popup window detected')
                # Keep popup open for user to interact
                pass
            
            self.browser_context.on('page', handle_popup)
            
            self.logger.info('Browser initialized (visible mode for login)')
            return True
        except Exception as e:
            self.logger.error(f'Could not initialize browser: {e}')
            return False

    def _close_browser(self):
        """Close browser."""
        try:
            if self.browser_context:
                self.browser_context.close()
                self.browser_context = None
                self.page = None
                self.logger.debug('Browser closed')
        except Exception as e:
            self.logger.warning(f'Error closing browser: {e}')

    def _is_logged_in(self) -> bool:
        """
        Check if logged into LinkedIn.

        Returns:
            True if logged in
        """
        try:
            # Multiple selectors to check for login
            selectors = [
                '[data-control-name="nav_digitallip_navbar"]',
                '.nav-item__profile-image',
                '#mynav',
                'a[href*="/mynetwork"]',
                'a[href*="/messaging"]'
            ]
            
            for selector in selectors:
                try:
                    self.page.wait_for_selector(selector, timeout=3000)
                    self.logger.debug(f'Found logged-in indicator: {selector}')
                    return True
                except:
                    continue
            
            # Also check URL - if we're on login page, not logged in
            current_url = self.page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                self.logger.debug(f'On login/checkpoint page: {current_url}')
                return False
            
            # If we have a reasonable LinkedIn URL, assume logged in
            if 'linkedin.com' in current_url and 'login' not in current_url:
                self.logger.debug(f'On LinkedIn page: {current_url}')
                return True
                
            return False
        except Exception as e:
            self.logger.debug(f'Error checking login status: {e}')
            return False

    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new notifications and messages.

        Returns:
            List of new activity items
        """
        activity = []

        try:
            # Initialize browser if needed
            if not self.page:
                if not self._init_browser():
                    return activity

            # Navigate to LinkedIn
            self.logger.info('Navigating to LinkedIn...')
            
            try:
                self.page.goto(self.LINKEDIN_URL, wait_until='networkidle', timeout=60000)
            except Exception as e:
                self.logger.warning(f'Navigation error (may be popup): {e}')
                # Wait longer for any popup to resolve
                self.page.wait_for_timeout(10000)

            # Wait for page to fully load (300 seconds = 5 minutes)
            self.logger.info('Waiting for page to fully load (300 seconds)...')
            self.page.wait_for_timeout(300000)

            # Check if logged in
            if not self._is_logged_in():
                self.logger.warning('Not logged into LinkedIn. Please log in manually.')
                self.logger.info('Waiting 120 minutes for manual login...')
                
                # Wait for user to log in manually (120 minutes = 7200 seconds)
                login_timeout = 1440  # 1440 x 5 seconds = 7200 seconds = 120 minutes
                logged_in = False
                
                for i in range(login_timeout):
                    self.page.wait_for_timeout(5000)
                    if self._is_logged_in():
                        self.logger.info('Login detected!')
                        logged_in = True
                        break
                    # Show progress every 30 seconds
                    if (i + 1) % 6 == 0:
                        elapsed = (i + 1) * 5
                        minutes = elapsed // 60
                        self.logger.info(f'Waiting for login... ({minutes} minutes elapsed)')
                
                # Check again after waiting
                if not logged_in:
                    # Create action file for login required
                    activity.append({
                        'type': 'login_required',
                        'message': 'LinkedIn login required. Please log in and keep browser open.'
                    })
                    return activity

            # Check notifications
            notifications = self._check_notifications()
            activity.extend(notifications)
            
            # Check messages
            messages = self._check_messages()
            activity.extend(messages)
            
            return activity
            
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
            self._close_browser()
            return activity

    def _check_notifications(self) -> list:
        """
        Check for new notifications.
        
        Returns:
            List of new notifications
        """
        notifications = []
        
        try:
            # Navigate to notifications
            self.page.goto(self.LINKEDIN_NOTIFICATIONS_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)
            
            # Try to find notification elements
            notification_elements = self.page.query_selector_all('div.notification-item')
            
            if not notification_elements:
                # Try alternative selector
                notification_elements = self.page.query_selector_all('li.update-card')
            
            self.logger.info(f'Found {len(notification_elements)} notifications')
            
            for elem in notification_elements[:10]:  # Limit to 10
                try:
                    # Extract notification data
                    text = elem.inner_text()
                    notification_id = elem.get_attribute('data-id') or str(hash(text))
                    
                    if notification_id not in self.processed_notifications:
                        # Extract type
                        notif_type = 'general'
                        if 'connection' in text.lower():
                            notif_type = 'connection'
                        elif 'message' in text.lower():
                            notif_type = 'message'
                        elif 'job' in text.lower() or 'hiring' in text.lower():
                            notif_type = 'job'
                        elif 'like' in text.lower() or 'comment' in text.lower():
                            notif_type = 'engagement'
                        
                        notifications.append({
                            'type': 'notification',
                            'notification_type': notif_type,
                            'id': notification_id,
                            'text': text[:500],
                            'timestamp': datetime.now().isoformat()
                        })
                        self.processed_notifications.add(notification_id)
                except Exception as e:
                    self.logger.debug(f'Could not parse notification: {e}')
            
        except Exception as e:
            self.logger.debug(f'Could not check notifications: {e}')
        
        return notifications

    def _check_messages(self) -> list:
        """
        Check for new messages.
        
        Returns:
            List of new messages
        """
        messages = []
        
        try:
            # Navigate to messages
            self.page.goto(self.LINKEDIN_MESSAGES_URL, wait_until='networkidle', timeout=30000)
            self.page.wait_for_timeout(3000)
            
            # Find conversation elements
            conversations = self.page.query_selector_all('div.conversation-list-item')
            
            if not conversations:
                conversations = self.page.query_selector_all('li.artdeco-list__item')
            
            self.logger.info(f'Found {len(conversations)} conversations')
            
            for conv in conversations[:5]:  # Limit to 5
                try:
                    text = conv.inner_text()
                    message_id = conv.get_attribute('data-id') or str(hash(text))
                    
                    # Check for unread indicator
                    is_unread = 'unread' in text.lower() or conv.get_attribute('aria-label') == 'unread'
                    
                    if is_unread and message_id not in self.processed_messages:
                        # Extract sender and preview
                        lines = text.split('\n')
                        sender = lines[0] if lines else 'Unknown'
                        preview = lines[1] if len(lines) > 1 else ''
                        
                        # Detect priority
                        priority = 'normal'
                        if any(kw in text.lower() for kw in self.priority_keywords):
                            priority = 'high'
                        
                        messages.append({
                            'type': 'message',
                            'id': message_id,
                            'sender': sender,
                            'preview': preview[:200],
                            'priority': priority,
                            'timestamp': datetime.now().isoformat()
                        })
                        self.processed_messages.add(message_id)
                        
                except Exception as e:
                    self.logger.debug(f'Could not parse message: {e}')
            
        except Exception as e:
            self.logger.debug(f'Could not check messages: {e}')
        
        return messages

    def create_action_file(self, item: dict) -> Path:
        """
        Create a markdown action file for the LinkedIn activity.
        
        Args:
            item: Activity item dict
            
        Returns:
            Path to created action file
        """
        if item['type'] == 'login_required':
            return self._create_login_action_file(item)
        elif item['type'] == 'notification':
            return self._create_notification_action_file(item)
        elif item['type'] == 'message':
            return self._create_message_action_file(item)
        else:
            return self._create_generic_action_file(item)

    def _create_login_action_file(self, item: dict) -> Path:
        """Create action file for login required."""
        content = f'''---
type: linkedin_login_required
created: {datetime.now().isoformat()}
priority: "high"
status: pending
---

# 🔐 LinkedIn Login Required

**Message:** {item['message']}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## ⚠️ Action Required

The LinkedIn Watcher needs you to log in to LinkedIn first.

## Steps

1. **Open LinkedIn** in your browser
2. **Log in** with your credentials
3. **Complete any 2FA** if prompted
4. **Run the watcher again**

---

## 🔗 Links

- [LinkedIn Login](https://www.linkedin.com/login)

---

*Action file created by LinkedIn Watcher*
'''
        filepath = self.get_unique_filename('LINKEDIN_LOGIN')
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def _create_notification_action_file(self, item: dict) -> Path:
        """Create action file for notification."""
        priority_emoji = '🔴' if item['notification_type'] in ['job', 'message'] else '🟡'
        
        content = f'''---
type: linkedin_notification
notification_type: "{item['notification_type']}"
linkedin_id: "{item['id']}"
created: {datetime.now().isoformat()}
priority: "{item['notification_type']}"
status: pending
---

# 🔔 LinkedIn Notification

**Type:** {item['notification_type'].title()}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Priority:** {priority_emoji} {item['notification_type'].title()}

---

## 📋 Notification Content

{item['text']}

---

## ✅ Suggested Actions

{self._notification_suggestions(item['notification_type'])}

---

## 🔗 Links

- [View on LinkedIn](https://www.linkedin.com/notifications)

---

*Action file created by LinkedIn Watcher*
'''
        filepath = self.get_unique_filename(f'LINKEDIN_{item["notification_type"].upper()}')
        filepath.write_text(content, encoding='utf-8')
        self._save_cache()
        return filepath

    def _create_message_action_file(self, item: dict) -> Path:
        """Create action file for message."""
        priority_emoji = '🔴' if item['priority'] == 'high' else '🟢'
        
        content = f'''---
type: linkedin_message
from: "{item['sender']}"
linkedin_id: "{item['id']}"
created: {datetime.now().isoformat()}
priority: "{item['priority']}"
status: pending
---

# 💬 LinkedIn Message

**From:** {item['sender']}  
**Preview:** {item['preview']}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Priority:** {priority_emoji} {item['priority'].title()}

---

## 📋 Message Preview

{item['preview']}

---

## ✅ Suggested Actions

{self._message_suggestions(item)}

---

## 🔗 Links

- [View on LinkedIn Messages](https://www.linkedin.com/messaging)

---

*Action file created by LinkedIn Watcher*
'''
        safe_sender = item['sender'].replace(' ', '_')[:20]
        filepath = self.get_unique_filename(f'LINKEDIN_MSG_{safe_sender}')
        filepath.write_text(content, encoding='utf-8')
        self._save_cache()
        return filepath

    def _create_generic_action_file(self, item: dict) -> Path:
        """Create generic action file."""
        content = f'''---
type: linkedin_activity
created: {datetime.now().isoformat()}
status: pending
---

# 📱 LinkedIn Activity

**Type:** {item.get('type', 'unknown')}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## Details

{json.dumps(item, indent=2)}

---

## ✅ Suggested Actions

- [ ] Review LinkedIn activity
- [ ] Take appropriate action
- [ ] Update this file with actions taken

---

*Action file created by LinkedIn Watcher*
'''
        filepath = self.get_unique_filename('LINKEDIN_ACTIVITY')
        filepath.write_text(content, encoding='utf-8')
        return filepath

    def _notification_suggestions(self, notif_type: str) -> str:
        """Get suggested actions for notification type."""
        suggestions = {
            'connection': [
                '- [ ] Review connection request',
                '- [ ] Check sender profile',
                '- [ ] Accept or decline connection',
                '- [ ] Send welcome message if accepted'
            ],
            'message': [
                '- [ ] Read message',
                '- [ ] Draft response',
                '- [ ] Send reply via LinkedIn'
            ],
            'job': [
                '- [ ] Review job opportunity',
                '- [ ] Check if interested',
                '- [ ] Apply or respond'
            ],
            'engagement': [
                '- [ ] Review engagement',
                '- [ ] Consider responding to comment',
                '- [ ] Thank for engagement if appropriate'
            ],
            'general': [
                '- [ ] Review notification',
                '- [ ] Take action if needed'
            ]
        }
        return '\n'.join(suggestions.get(notif_type, suggestions['general']))

    def _message_suggestions(self, item: dict) -> str:
        """Get suggested actions for message."""
        suggestions = []
        text = f"{item['sender']} {item['preview']}".lower()
        
        if item['priority'] == 'high':
            suggestions.append('- [ ] **Respond urgently** (high priority)')
        
        if any(kw in text for kw in ['interview', 'job', 'hiring', 'position']):
            suggestions.append('- [ ] Review job opportunity')
            suggestions.append('- [ ] Check if interested')
            suggestions.append('- [ ] Respond with interest or decline')
        elif any(kw in text for kw in ['meeting', 'call', 'schedule']):
            suggestions.append('- [ ] Check calendar availability')
            suggestions.append('- [ ] Propose meeting time')
        elif any(kw in text for kw in ['invoice', 'payment', 'billing']):
            suggestions.append('- [ ] Review billing inquiry')
            suggestions.append('- [ ] Forward to accounting if needed')
        else:
            suggestions.append('- [ ] Read full message')
            suggestions.append('- [ ] Draft appropriate response')
            suggestions.append('- [ ] Send reply')
        
        return '\n'.join(suggestions)

    def run(self):
        """Main run loop with proper cleanup."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Session path: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    if items:
                        self.logger.info(f'Found {len(items)} new activity item(s)')
                        for item in items:
                            try:
                                filepath = self.create_action_file(item)
                                self.logger.info(f'Created action file: {filepath.name}')
                            except Exception as e:
                                self.logger.error(f'Error creating action file: {e}')
                    else:
                        self.logger.debug('No new activity')
                    
                    # Close browser after each check to save resources
                    self._close_browser()
                    
                except Exception as e:
                    self.logger.error(f'Error in check loop: {e}')
                    self._close_browser()
                
                self.page = None  # Reset page for next iteration
                self.browser_context = None
                self._save_cache()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
            self._close_browser()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}')
            self._close_browser()
            raise


def main():
    """Main entry point."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python linkedin_watcher.py <vault_path> [session_path] [check_interval]")
        print("\nExample:")
        print('  python linkedin_watcher.py "C:/Users/Name/ObsidianVault"')
        print('  python linkedin_watcher.py "C:/Vault" "C:/linkedin_session" 300')
        sys.exit(1)
    
    vault_path = sys.argv[1]
    session_path = sys.argv[2] if len(sys.argv) > 2 else None
    check_interval = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    
    # Validate vault path
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Check Playwright installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed.")
        print("Run: pip install playwright && playwright install")
        sys.exit(1)
    
    # Create and run watcher
    watcher = LinkedInWatcher(vault_path, session_path, check_interval)
    print(f"💼 LinkedIn Watcher starting...")
    print(f"   Vault: {vault_path}")
    print(f"   Session: {watcher.session_path}")
    print(f"   Check Interval: {check_interval}s")
    print(f"\nNote: First run will require manual LinkedIn login")
    print("Press Ctrl+C to stop\n")
    
    watcher.run()


if __name__ == '__main__':
    import time  # Import time for the run loop
    main()
