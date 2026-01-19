#!/usr/bin/env python3
"""
Anthropic Admin API Key Manager
Demonstrates integration of Anthropic Admin API for managing API keys
"""

import sys
import io
import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class AnthropicAPIKeyManager:
    """Manager for Anthropic Admin API operations"""

    BASE_URL = "https://api.anthropic.com/v1/organizations"

    def __init__(self, admin_api_key: str):
        """
        Initialize the API Key Manager.

        Args:
            admin_api_key: Admin-level API key for organization management
        """
        self.admin_api_key = admin_api_key
        self.headers = {
            "X-Api-Key": admin_api_key,
            "Content-Type": "application/json"
        }

    def retrieve_api_key(self, api_key_id: str) -> Optional[Dict]:
        """
        Retrieve information about a specific API key.

        Args:
            api_key_id: ID of the API key to retrieve

        Returns:
            Dictionary with API key information, or None on error
        """
        url = f"{self.BASE_URL}/api_keys/{api_key_id}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                print(f"[ERROR] Invalid admin API key - check your credentials")
            elif response.status_code == 404:
                print(f"[ERROR] API key not found: {api_key_id}")
            else:
                print(f"[ERROR] HTTP {response.status_code}: {response.text}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return None

    def list_api_keys(self, limit: int = 20) -> Optional[List[Dict]]:
        """
        List all API keys in the organization.

        Args:
            limit: Maximum number of keys to retrieve

        Returns:
            List of API key dictionaries, or None on error
        """
        url = f"{self.BASE_URL}/api_keys"
        params = {"limit": limit}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])

        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Failed to list API keys: {response.status_code}")
            print(f"[ERROR] {response.text}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            return None

    def display_key_info(self, key_info: Dict) -> None:
        """
        Display API key information in a formatted way.

        Args:
            key_info: Dictionary containing API key information
        """
        print("\n" + "="*70)
        print("API KEY INFORMATION")
        print("="*70)
        print(f"ID:           {key_info['id']}")
        print(f"Name:         {key_info['name']}")
        print(f"Status:       {key_info['status'].upper()}")
        print(f"Type:         {key_info['type']}")
        print(f"Key Hint:     {key_info['partial_key_hint']}")

        # Parse and format the creation date
        created_at = key_info['created_at']
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            formatted_date = created_at

        print(f"Created:      {formatted_date}")
        print(f"Created By:   {key_info['created_by']['type']} (ID: {key_info['created_by']['id']})")

        workspace_id = key_info.get('workspace_id')
        print(f"Workspace:    {workspace_id if workspace_id else 'Default (Organization)'}")
        print("="*70 + "\n")

    def display_keys_summary(self, keys: List[Dict]) -> None:
        """
        Display a summary table of multiple API keys.

        Args:
            keys: List of API key dictionaries
        """
        print("\n" + "="*100)
        print("API KEYS SUMMARY")
        print("="*100)
        print(f"{'Name':<30} {'Status':<10} {'Key Hint':<25} {'Created':<20}")
        print("-"*100)

        for key in keys:
            name = key['name'][:28] + '..' if len(key['name']) > 30 else key['name']
            status = key['status'].upper()
            hint = key['partial_key_hint']

            # Format creation date
            try:
                dt = datetime.fromisoformat(key['created_at'].replace('Z', '+00:00'))
                created = dt.strftime("%Y-%m-%d %H:%M")
            except:
                created = key['created_at'][:16]

            print(f"{name:<30} {status:<10} {hint:<25} {created:<20}")

        print("="*100)
        print(f"Total Keys: {len(keys)}")
        print(f"Active: {sum(1 for k in keys if k['status'] == 'active')}")
        print(f"Inactive: {sum(1 for k in keys if k['status'] == 'inactive')}")
        print(f"Archived: {sum(1 for k in keys if k['status'] == 'archived')}")
        print("="*100 + "\n")


def interactive_menu():
    """Interactive menu for API key management"""

    print("="*70)
    print("ANTHROPIC API KEY MANAGER")
    print("="*70)
    print("\nThis tool helps you manage Anthropic API keys using the Admin API.")
    print("You need an Admin API Key to use this tool.\n")

    # Get admin API key
    admin_key = os.getenv("ANTHROPIC_ADMIN_API_KEY")

    if not admin_key:
        print("[INFO] ANTHROPIC_ADMIN_API_KEY not found in environment")
        admin_key = input("Enter your Admin API Key: ").strip()

        if not admin_key:
            print("[ERROR] Admin API key is required")
            return
    else:
        print("[INFO] Using Admin API Key from environment variable")

    # Initialize manager
    manager = AnthropicAPIKeyManager(admin_key)

    while True:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("  1. Retrieve specific API key by ID")
        print("  2. List all API keys")
        print("  3. Exit")
        print("="*70)

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            # Retrieve specific key
            key_id = input("\nEnter API Key ID: ").strip()
            if key_id:
                print(f"\n[INFO] Retrieving API key: {key_id}")
                key_info = manager.retrieve_api_key(key_id)
                if key_info:
                    manager.display_key_info(key_info)

                    # Save to file option
                    save = input("Save to JSON file? (y/n): ").strip().lower()
                    if save == 'y':
                        filename = f"api_key_{key_id}.json"
                        with open(filename, 'w') as f:
                            json.dump(key_info, f, indent=2)
                        print(f"[SUCCESS] Saved to {filename}")

        elif choice == "2":
            # List all keys
            limit = input("\nHow many keys to retrieve? (default: 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20

            print(f"\n[INFO] Retrieving up to {limit} API keys...")
            keys = manager.list_api_keys(limit)

            if keys:
                manager.display_keys_summary(keys)

                # Save to file option
                save = input("Save to JSON file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = "api_keys_list.json"
                    with open(filename, 'w') as f:
                        json.dump(keys, f, indent=2)
                    print(f"[SUCCESS] Saved to {filename}")

        elif choice == "3":
            print("\n[INFO] Exiting API Key Manager")
            break

        else:
            print("\n[ERROR] Invalid choice. Please select 1, 2, or 3.")


def demo_usage():
    """Demonstrate programmatic usage"""

    print("\n" + "="*70)
    print("DEMO: Programmatic Usage")
    print("="*70 + "\n")

    # Example code
    example = '''
# Example 1: Retrieve specific API key
from anthropic_api_key_manager import AnthropicAPIKeyManager

admin_key = "sk-ant-admin-xxxxxxxxxxxxx"
manager = AnthropicAPIKeyManager(admin_key)

# Get info about a specific key
key_info = manager.retrieve_api_key("apikey_abc123xyz")
if key_info:
    print(f"Key Status: {key_info['status']}")
    print(f"Created: {key_info['created_at']}")

# Example 2: List all active keys
keys = manager.list_api_keys(limit=50)
active_keys = [k for k in keys if k['status'] == 'active']
print(f"Active keys: {len(active_keys)}")

# Example 3: Find keys by name
def find_keys_by_name(manager, name_pattern):
    keys = manager.list_api_keys(limit=100)
    return [k for k in keys if name_pattern.lower() in k['name'].lower()]

prod_keys = find_keys_by_name(manager, "production")
print(f"Production keys: {prod_keys}")
'''

    print(example)
    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_usage()
    else:
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")
