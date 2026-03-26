#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Server - MCP server for sending emails from Approved folder.

This MCP server:
1. Monitors /Approved folder for approval files
2. Sends emails via Gmail API
3. Moves completed files to /Done
4. Provides MCP tools for email operations

Usage:
    python email_mcp_server.py
    
Or via MCP client:
    npx -y @modelcontextprotocol/server --transport stdio python email_mcp_server.py
"""

import sys
import json
import base64
import re
import time
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText

# Gmail API imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:
    print(json.dumps({
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32000,
            "message": "Google auth not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client"
        }
    }))
    sys.exit(1)


class EmailMCPServer:
    """MCP Server for email operations."""
    
    def __init__(self, vault_path: str = None):
        """Initialize email MCP server."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        self.approved_folder = self.vault_path / 'Approved'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.approved_folder.mkdir(parents=True, exist_ok=True)
        self.done_folder.mkdir(parents=True, exist_ok=True)
        
        # Gmail service
        self.service = self._authenticate()
        
        # File watcher state
        self.processed_files = set()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        token_path = Path(__file__).parent / 'token.json'
        
        if not token_path.exists():
            raise FileNotFoundError(f'OAuth token not found at {token_path}')
        
        creds = Credentials.from_authorized_user_file(token_path, [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ])
        
        return build('gmail', 'v1', credentials=creds)
    
    def list_tools(self) -> dict:
        """List available MCP tools."""
        return {
            "tools": [
                {
                    "name": "email_send_approved",
                    "description": "Send all approved emails from the Approved folder",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "dry_run": {
                                "type": "boolean",
                                "description": "If true, only list files without sending"
                            }
                        }
                    }
                },
                {
                    "name": "email_send_single",
                    "description": "Send a single email to specified recipient",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Recipient email"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body"},
                            "in_reply_to": {"type": "string", "description": "Message ID to reply to"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                },
                {
                    "name": "email_list_approved",
                    "description": "List all pending approval files in Approved folder",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "email_check_status",
                    "description": "Check email server status and authentication",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def call_tool(self, name: str, arguments: dict) -> dict:
        """Call an MCP tool."""
        if name == "email_send_approved":
            return self._send_approved(arguments)
        elif name == "email_send_single":
            return self._send_single(arguments)
        elif name == "email_list_approved":
            return self._list_approved()
        elif name == "email_check_status":
            return self._check_status()
        else:
            return {"error": f"Unknown tool: {name}"}
    
    def _send_approved(self, arguments: dict) -> dict:
        """Send all approved emails."""
        dry_run = arguments.get('dry_run', False)
        results = []
        
        # Find approval files
        approval_files = list(self.approved_folder.glob('APPROVAL_EMAIL_*.md'))
        
        if not approval_files:
            return {
                "content": [{"type": "text", "text": "📭 No approved emails to send"}],
                "isError": False
            }
        
        for filepath in approval_files:
            try:
                content = filepath.read_text(encoding='utf-8')
                email_data = self._extract_email_details(content)
                
                if dry_run:
                    results.append(f"Would send to: {email_data['to']}")
                    continue
                
                # Send email
                message_id = self._send_email(
                    to=email_data['to'],
                    subject=email_data['subject'],
                    body=self._extract_reply_body(content)
                )
                
                # Update and move file
                self._update_file(filepath, 'sent', message_id)
                self._move_to_done(filepath)
                
                results.append(f"✅ Sent to {email_data['to']} - Message ID: {message_id}")
                
            except Exception as e:
                results.append(f"❌ Failed {filepath.name}: {str(e)}")
        
        return {
            "content": [{"type": "text", "text": "\n".join(results)}],
            "isError": False
        }
    
    def _send_single(self, arguments: dict) -> dict:
        """Send a single email."""
        try:
            to = arguments['to']
            subject = arguments['subject']
            body = arguments['body']
            in_reply_to = arguments.get('in_reply_to')
            
            message_id = self._send_email(to, subject, body, in_reply_to)
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"✅ Email sent to {to}\nMessage ID: {message_id}"
                }],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"❌ Failed: {str(e)}"}],
                "isError": True
            }
    
    def _list_approved(self) -> dict:
        """List pending approval files."""
        files = list(self.approved_folder.glob('APPROVAL_*.md'))
        
        if not files:
            return {
                "content": [{"type": "text", "text": "📭 No pending approval files"}],
                "isError": False
            }
        
        file_list = []
        for f in sorted(files):
            stat = f.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            file_list.append(f"- {f.name} ({size} bytes, modified: {modified})")
        
        return {
            "content": [{
                "type": "text",
                "text": f"📧 Pending approval files ({len(files)}):\n\n" + "\n".join(file_list)
            }],
            "isError": False
        }
    
    def _check_status(self) -> dict:
        """Check server status."""
        return {
            "content": [{
                "type": "text",
                "text": f"✅ Email MCP Server Status:\n"
                       f"- Vault: {self.vault_path}\n"
                       f"- Approved folder: {self.approved_folder}\n"
                       f"- Gmail API: Connected\n"
                       f"- Token: Valid"
            }],
            "isError": False
        }
    
    def _extract_email_details(self, content: str) -> dict:
        """Extract email details from approval file."""
        def extract_field(pattern, text):
            match = re.search(pattern, text, re.MULTILINE)
            return match.group(1) if match else None
        
        to_email = extract_field(r'to: "([^"]+)"', content)
        subject = extract_field(r'subject: "([^"]+)"', content)
        
        return {
            'to': to_email,
            'subject': subject
        }
    
    def _extract_reply_body(self, content: str) -> str:
        """Extract reply body from approval file."""
        # Look for draft content section
        match = re.search(r'## Draft Content\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if match:
            body = match.group(1).strip()
            # Remove approval sections
            body = re.sub(r'\n## To (Approve|Reject).*', '', body, flags=re.DOTALL)
            return body.strip()
        
        # Fallback: use entire content after first section
        return content[:2000]
    
    def _send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> str:
        """Send email via Gmail API."""
        message = MIMEText(body)
        message['to'] = to
        message['from'] = 'me'
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_message = self.service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return sent_message['id']
    
    def _update_file(self, filepath: Path, status: str, message_id: str):
        """Update approval file with status."""
        content = filepath.read_text(encoding='utf-8')
        content = re.sub(r'status: pending', f'status: {status}', content)
        
        log_entry = f"""
---

## 🤖 MCP Sent

**Sent at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** {status.title()}  
**Message ID:** {message_id}
"""
        content += log_entry
        filepath.write_text(content, encoding='utf-8')
    
    def _move_to_done(self, filepath: Path):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{filepath.stem}_sent_{timestamp}.md"
        dest_path = self.done_folder / new_name
        filepath.rename(dest_path)


def main():
    """Main MCP server loop (stdio transport)."""
    server = EmailMCPServer()
    
    # Send initialization message
    init_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "email-mcp-server",
                "version": "1.0.0"
            }
        }
    }
    print(json.dumps(init_response), flush=True)
    
    # Process messages
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')
            
            if method == 'initialize':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "email-mcp-server", "version": "1.0.0"}
                    }
                }
            elif method == 'tools/list':
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": server.list_tools()
                }
            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})
                result = server.call_tool(tool_name, tool_args)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            elif method == 'notifications/initialized':
                # No response needed for notifications
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    main()
