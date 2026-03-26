#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Post Automation - Posts content to LinkedIn automatically.

Uses the saved LinkedIn session to post content from action files.
Requires prior approval before posting (HITL workflow).

Usage:
    python linkedin_poster.py <vault_path> [post_file]

Example:
    python linkedin_poster.py "..\\AI_Employee_Vault" "LINKEDIN_POST_draft.md"
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Playwright imports
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install")
    sys.exit(1)


class LinkedInPoster:
    """
    Posts content to LinkedIn using saved session.
    """

    LINKEDIN_URL = 'https://www.linkedin.com'
    LINKEDIN_POST_URL = 'https://www.linkedin.com/feed/'

    def __init__(self, vault_path: str, session_path: str = None):
        """
        Initialize the LinkedIn poster.

        Args:
            vault_path: Path to the Obsidian vault root
            session_path: Path to LinkedIn browser session (default: vault/.linkedin_session)
        """
        self.vault_path = Path(vault_path)

        # Set session path
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = self.vault_path / '.linkedin_session'

        # Browser context
        self.browser_context = None
        self.page = None

        # Setup logging
        import logging
        self.logger = logging.getLogger('LinkedInPoster')
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def _init_browser(self):
        """Initialize browser with saved session."""
        try:
            self.logger.info('Starting Playwright...')
            playwright = sync_playwright().start()
            self.logger.info(f'Session path: {self.session_path}')
            self.logger.info('Launching browser with persistent context...')
            
            # Try to launch with retry
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    self.browser_context = playwright.chromium.launch_persistent_context(
                        user_data_dir=str(self.session_path),
                        headless=False,  # Visible for verification
                        ignore_default_args=['--enable-automation'],
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-gpu'
                        ]
                    )
                    
                    self.page = self.browser_context.pages[0] if self.browser_context.pages else self.browser_context.new_page()
                    self.logger.info('Browser initialized successfully')
                    return True
                except Exception as e:
                    self.logger.warning(f'Attempt {attempt + 1} failed: {e}')
                    if attempt == max_retries - 1:
                        # Last attempt - create fresh context
                        self.logger.info('Creating fresh browser context...')
                        self.browser_context = playwright.chromium.launch_persistent_context(
                            user_data_dir=str(self.session_path),
                            headless=False,
                            ignore_default_args=['--enable-automation'],
                            args=[
                                '--disable-blink-features=AutomationControlled',
                                '--disable-dev-shm-usage',
                                '--no-sandbox'
                            ]
                        )
                        self.page = self.browser_context.pages[0] if self.browser_context.pages else self.browser_context.new_page()
                        self.logger.info('Fresh browser context created')
                        return True
                    # Wait before retry
                    import time
                    time.sleep(2)
                    
        except Exception as e:
            self.logger.error(f'Could not initialize browser: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _close_browser(self):
        """Close browser."""
        try:
            if self.browser_context:
                self.browser_context.close()
                self.browser_context = None
                self.page = None
                self.logger.info('Browser closed')
        except Exception as e:
            self.logger.warning(f'Error closing browser: {e}')

    def _is_logged_in(self) -> bool:
        """Check if logged into LinkedIn."""
        try:
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
                    return True
                except:
                    continue
            
            current_url = self.page.url
            if 'login' in current_url or 'checkpoint' in current_url:
                return False
            
            if 'linkedin.com' in current_url and 'login' not in current_url:
                return True
                
            return False
        except Exception as e:
            self.logger.debug(f'Error checking login status: {e}')
            return False

    def post_content(self, content: str, description: str = '') -> bool:
        """
        Post content to LinkedIn.

        Args:
            content: The post content (text with hashtags)
            description: Optional description for logging

        Returns:
            True if post successful
        """
        try:
            # Initialize browser first
            self.logger.info('Initializing browser...')
            if not self._init_browser():
                self.logger.error('Failed to initialize browser')
                return False
            
            if not self.page:
                self.logger.error('Page object is None after browser initialization')
                return False
            
            # Navigate to LinkedIn homepage first (simpler than feed)
            self.logger.info('Navigating to LinkedIn homepage...')
            try:
                self.page.goto(self.LINKEDIN_URL, wait_until='domcontentloaded', timeout=30000)
                self.page.wait_for_timeout(5000)
            except Exception as e:
                self.logger.warning(f'Navigation timeout, continuing anyway: {e}')
                self.page.wait_for_timeout(10000)

            # Check if logged in
            if not self._is_logged_in():
                self.logger.error('Not logged into LinkedIn!')
                self.logger.error(f'Current URL: {self.page.url}')
                return False

            self.logger.info('Logged in successfully')
            
            # Navigate to feed page
            self.logger.info('Navigating to feed page...')
            try:
                self.page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=30000)
                self.page.wait_for_timeout(8000)
            except Exception as e:
                self.logger.warning(f'Feed navigation timeout, continuing: {e}')
                self.page.wait_for_timeout(5000)

            # Find and click the post creation box
            self.logger.info('Finding post creation box...')

            # Try multiple selectors for the post box
            post_box_selectors = [
                '[data-control-name="update-social-text"]',
                '.share-box-feed-entry__trigger',
                '[aria-label="Start a post"]',
                'button[aria-label*="post"]',
                '.ipynb-convert-trigger'
            ]

            post_box = None
            for selector in post_box_selectors:
                try:
                    post_box = self.page.query_selector(selector)
                    if post_box:
                        self.logger.info(f'Found post box with selector: {selector}')
                        break
                except Exception as e:
                    self.logger.debug(f'Selector {selector} failed: {e}')
                    continue

            if not post_box:
                self.logger.info('Post box not found, trying direct URL...')
                # Try direct create post URL
                self.page.goto('https://www.linkedin.com/feed/?createContent=true', wait_until='domcontentloaded', timeout=30000)
                self.page.wait_for_timeout(5000)

            # Click the post box to open editor
            if post_box:
                try:
                    post_box.click()
                    self.page.wait_for_timeout(3000)
                    self.logger.info('Post box clicked')
                except Exception as e:
                    self.logger.warning(f'Click failed: {e}')

            # Find the text editor
            self.logger.info('Finding text editor...')
            editor_selectors = [
                'div[contenteditable="true"]',
                '.editor-composer__content',
                '[aria-label="What do you want to talk about?"]',
                '[placeholder*="post"]',
                '[placeholder*="What"]'
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    editor = self.page.query_selector(selector)
                    if editor:
                        self.logger.info(f'Found editor with selector: {selector}')
                        break
                except Exception as e:
                    self.logger.debug(f'Editor selector {selector} failed: {e}')
                    continue
            
            if not editor:
                self.logger.error('Could not find text editor!')
                # Take screenshot for debugging
                screenshot_path = self.vault_path / 'linkedin_no_editor.png'
                self.page.screenshot(path=str(screenshot_path))
                self.logger.info(f'Screenshot saved: {screenshot_path}')
                return False
            
            # Type the content
            self.logger.info('Typing post content...')
            
            # Clear any existing content first
            try:
                self.page.keyboard.press('Control+A')
                self.page.keyboard.press('Delete')
                self.page.wait_for_timeout(500)
            except:
                pass
            
            # Type content in chunks
            chunks = content.split('\n\n')
            for chunk in chunks:
                if chunk.strip():
                    try:
                        editor.type(chunk.strip())
                        self.page.wait_for_timeout(300)
                        editor.type('\n\n')
                        self.page.wait_for_timeout(300)
                    except Exception as e:
                        self.logger.warning(f'Typing error: {e}')
            
            self.page.wait_for_timeout(2000)
            
            # Take a screenshot before posting
            screenshot_path = self.vault_path / 'linkedin_post_preview.png'
            try:
                self.page.screenshot(path=str(screenshot_path))
                self.logger.info(f'Preview screenshot saved: {screenshot_path}')
            except Exception as e:
                self.logger.warning(f'Could not take preview screenshot: {e}')
            
            # Find and click the Post button
            self.logger.info('Finding Post button...')
            
            # Wait for dialog to fully load
            self.page.wait_for_timeout(2000)
            
            # Look for Post button in the dialog (more specific selectors)
            post_button_selectors = [
                'button[aria-label="Post"]',
                'button.ml3',
                '.share-actions__primary-action',
                'button:has-text("Post")',
                '.update-v2 button:text("Post")',
                '[class*="share-actions"] button:text("Post")'
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = self.page.query_selector(selector)
                    if post_button:
                        self.logger.info(f'Found Post button with selector: {selector}')
                        break
                except Exception as e:
                    self.logger.debug(f'Post button selector {selector} failed: {e}')
                    continue
            
            if not post_button:
                # Try finding by class within dialog
                try:
                    self.logger.info('Looking for Post button in dialog...')
                    # LinkedIn post dialog has specific structure
                    post_button = self.page.evaluate('''() => {
                        const dialogs = document.querySelectorAll('[role="dialog"]');
                        for (const dialog of dialogs) {
                            const buttons = dialog.querySelectorAll('button');
                            for (const btn of buttons) {
                                if (btn.textContent.trim() === 'Post') {
                                    btn.click();
                                    return 'clicked';
                                }
                            }
                        }
                        return 'not found';
                    }''')
                    self.logger.info(f'Dialog button search result: {post_button}')
                    if post_button == 'clicked':
                        self.page.wait_for_timeout(5000)
                        # Check if posted
                        page_content = self.page.content()
                        if any(indicator.lower() in page_content.lower() for indicator in ['Your post has been shared', 'Post published']):
                            self.logger.info('✅ Post published successfully via dialog!')
                            return True
                except Exception as e:
                    self.logger.warning(f'Dialog button search failed: {e}')
                
                # Last resort - use keyboard
                self.logger.info('Using keyboard shortcut...')
                self.page.keyboard.press('Tab')  # Move focus to Post button
                self.page.wait_for_timeout(500)
                self.page.keyboard.press('Enter')
                self.page.wait_for_timeout(5000)
            
            # Click Post button
            self.logger.info('Clicking Post button...')
            
            if post_button and post_button != 'clicked':
                try:
                    # Try normal click first
                    post_button.click(timeout=5000)
                    self.logger.info('Normal click succeeded')
                except Exception as e:
                    self.logger.warning(f'Normal click failed: {e}')
                    try:
                        # Try force click
                        post_button.click(force=True, timeout=5000)
                        self.logger.info('Force click succeeded')
                    except Exception as e2:
                        self.logger.warning(f'Force click failed: {e2}')
                        # Use JavaScript click as last resort
                        self.page.evaluate('(el) => el.click()', post_button)
                        self.logger.info('JavaScript click used')
            
            # Wait for post to submit
            self.logger.info('Waiting for post submission...')
            self.page.wait_for_timeout(8000)
            
            # Check if post was successful
            page_content = self.page.content()
            success_indicators = [
                'Your post has been shared',
                'Post published',
                'View post',
                'See engagement',
                'post published'
            ]
            
            posted = any(indicator.lower() in page_content.lower() for indicator in success_indicators)
            
            if posted:
                self.logger.info('✅ Post published successfully!')
                # Take final screenshot
                final_screenshot = self.vault_path / 'linkedin_post_published.png'
                try:
                    self.page.screenshot(path=str(final_screenshot))
                    self.logger.info(f'Published screenshot saved: {final_screenshot}')
                except Exception as e:
                    self.logger.warning(f'Could not take final screenshot: {e}')
                return True
            else:
                # Check if we're on feed page (post likely succeeded)
                if 'feed' in self.page.url:
                    self.logger.info('Still on feed page - post likely successful')
                    # Take screenshot anyway
                    final_screenshot = self.vault_path / 'linkedin_post_published.png'
                    try:
                        self.page.screenshot(path=str(final_screenshot))
                        self.logger.info(f'Screenshot saved: {final_screenshot}')
                    except:
                        pass
                    return True
                self.logger.warning('Post status unclear - check manually')
                return False
                
        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            import traceback
            self.logger.error(traceback.format_exc())
            return False
        finally:
            self._close_browser()

    def parse_post_file(self, filepath: Path) -> dict:
        """
        Parse a LinkedIn post action file.
        
        Args:
            filepath: Path to post file
            
        Returns:
            Dict with post details
        """
        content = filepath.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = {}
        match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if match:
            for line in match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip().strip('"')
        
        # Extract post content (between ## 📝 Post Content and next section)
        post_content = ''
        content_match = re.search(r'## 📝 Post Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if content_match:
            post_content = content_match.group(1).strip()
        
        return {
            'filepath': filepath,
            'topic': frontmatter.get('topic', 'LinkedIn Post'),
            'scheduled': frontmatter.get('scheduled', ''),
            'status': frontmatter.get('status', 'draft'),
            'content': post_content,
            'hashtags': frontmatter.get('hashtags', '')
        }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python linkedin_poster.py <vault_path> [post_file]")
        print("\nExample:")
        print('  python linkedin_poster.py "..\\AI_Employee_Vault" "LINKEDIN_POST_draft.md"')
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    post_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Find post file
    if post_file:
        post_path = vault_path / 'Needs_Action' / post_file
        if not post_path.exists():
            post_path = vault_path / 'Approved' / post_file
        if not post_path.exists():
            post_path = Path(post_file)
        if not post_path.exists():
            print(f"Error: Post file not found: {post_file}")
            sys.exit(1)
    else:
        # Find latest approved post
        approved_folder = vault_path / 'Approved'
        post_files = list(approved_folder.glob('LINKEDIN_POST_*.md'))
        if not post_files:
            print("No LinkedIn post files found in /Approved folder")
            sys.exit(1)
        post_path = sorted(post_files)[-1]  # Get most recent
    
    print(f"📱 LinkedIn Post Automation")
    print(f"   Vault: {vault_path}")
    print(f"   Post File: {post_path}")
    print()
    
    # Initialize poster
    poster = LinkedInPoster(str(vault_path))
    
    # Parse post file
    post_data = poster.parse_post_file(post_path)
    print(f"📝 Post Details:")
    print(f"   Topic: {post_data['topic']}")
    print(f"   Status: {post_data['status']}")
    print(f"   Content Length: {len(post_data['content'])} chars")
    print()
    
    # Check if approved
    if post_data['status'] != 'approved':
        print("⚠️ Warning: Post is not approved!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Post to LinkedIn
    print("🚀 Posting to LinkedIn...")
    success = poster.post_content(post_data['content'], post_data['topic'])
    
    if success:
        print("\n✅ Post published successfully!")
        
        # Update the post file
        update_post_file(post_path, 'published')
    else:
        print("\n❌ Failed to post to LinkedIn")
        update_post_file(post_path, 'failed')


def update_post_file(filepath: Path, status: str):
    """Update post file with status."""
    content = filepath.read_text(encoding='utf-8')
    
    # Update status in frontmatter
    content = re.sub(
        r'status:.*',
        f'status: {status}',
        content
    )
    
    # Add processing log
    log_entry = f'''
---

## 🤖 Processing Log

**Posted by:** LinkedIn Poster  
**Posted at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status.title()}
'''
    
    content += log_entry
    filepath.write_text(content, encoding='utf-8')
    print(f"📝 Post file updated: {filepath}")


if __name__ == '__main__':
    main()
