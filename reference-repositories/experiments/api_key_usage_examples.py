#!/usr/bin/env python3
"""
Advanced Examples: Integrating Anthropic Admin API into Agentic Workflows
"""

import sys
import io
import os
from anthropic_api_key_manager import AnthropicAPIKeyManager
from datetime import datetime, timedelta
import json

# Force UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class APIKeyAnalyzer:
    """Advanced analytics for API key management"""

    def __init__(self, manager: AnthropicAPIKeyManager):
        self.manager = manager

    def audit_keys(self) -> dict:
        """
        Perform a comprehensive audit of all API keys.

        Returns:
            Dictionary with audit results
        """
        print("\n[INFO] Starting API key audit...")
        keys = self.manager.list_api_keys(limit=100)

        if not keys:
            return {"error": "Failed to retrieve keys"}

        audit_results = {
            "total_keys": len(keys),
            "by_status": {
                "active": [],
                "inactive": [],
                "archived": []
            },
            "by_workspace": {},
            "by_creator": {},
            "recent_keys": [],  # Created in last 30 days
            "old_keys": []      # Created more than 180 days ago
        }

        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        six_months_ago = now - timedelta(days=180)

        for key in keys:
            status = key['status']
            audit_results['by_status'][status].append(key)

            # Group by workspace
            workspace = key.get('workspace_id', 'default')
            if workspace not in audit_results['by_workspace']:
                audit_results['by_workspace'][workspace] = []
            audit_results['by_workspace'][workspace].append(key)

            # Group by creator
            creator_id = key['created_by']['id']
            if creator_id not in audit_results['by_creator']:
                audit_results['by_creator'][creator_id] = []
            audit_results['by_creator'][creator_id].append(key)

            # Check age
            try:
                created_dt = datetime.fromisoformat(key['created_at'].replace('Z', '+00:00'))
                created_dt = created_dt.replace(tzinfo=None)  # Remove timezone for comparison

                if created_dt > thirty_days_ago:
                    audit_results['recent_keys'].append(key)
                elif created_dt < six_months_ago:
                    audit_results['old_keys'].append(key)
            except:
                pass

        return audit_results

    def display_audit_report(self, audit_results: dict) -> None:
        """Display formatted audit report"""

        print("\n" + "="*80)
        print("API KEY AUDIT REPORT")
        print("="*80)

        # Summary
        print(f"\nTotal API Keys: {audit_results['total_keys']}")
        print("\nStatus Breakdown:")
        for status, keys in audit_results['by_status'].items():
            print(f"  {status.capitalize():<12}: {len(keys)}")

        # Workspace distribution
        print("\nWorkspace Distribution:")
        for workspace, keys in audit_results['by_workspace'].items():
            ws_name = workspace if workspace != 'default' else 'Default (Organization)'
            print(f"  {ws_name:<30}: {len(keys)} keys")

        # Creator distribution
        print("\nTop Key Creators:")
        creators_sorted = sorted(
            audit_results['by_creator'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]
        for creator_id, keys in creators_sorted:
            print(f"  {creator_id:<30}: {len(keys)} keys")

        # Age analysis
        print("\nAge Analysis:")
        print(f"  Recent (< 30 days):     {len(audit_results['recent_keys'])}")
        print(f"  Old (> 180 days):       {len(audit_results['old_keys'])}")

        # Recommendations
        print("\n" + "-"*80)
        print("RECOMMENDATIONS:")

        if len(audit_results['by_status']['inactive']) > 0:
            print(f"  [!] {len(audit_results['by_status']['inactive'])} inactive keys - consider archiving")

        if len(audit_results['old_keys']) > 5:
            print(f"  [!] {len(audit_results['old_keys'])} keys older than 6 months - review and rotate")

        if audit_results['total_keys'] > 50:
            print(f"  [!] {audit_results['total_keys']} total keys - consider consolidation")

        print("="*80 + "\n")

    def find_keys_by_criteria(self, **criteria) -> list:
        """
        Find API keys matching specific criteria.

        Args:
            **criteria: Keyword arguments for filtering
                - status: 'active', 'inactive', 'archived'
                - name_contains: substring to match in name
                - workspace_id: specific workspace
                - creator_id: specific creator

        Returns:
            List of matching API keys
        """
        keys = self.manager.list_api_keys(limit=100)
        if not keys:
            return []

        results = keys

        if 'status' in criteria:
            results = [k for k in results if k['status'] == criteria['status']]

        if 'name_contains' in criteria:
            pattern = criteria['name_contains'].lower()
            results = [k for k in results if pattern in k['name'].lower()]

        if 'workspace_id' in criteria:
            results = [k for k in results if k.get('workspace_id') == criteria['workspace_id']]

        if 'creator_id' in criteria:
            results = [k for k in results if k['created_by']['id'] == criteria['creator_id']]

        return results

    def export_audit_to_json(self, audit_results: dict, filename: str = "api_key_audit.json") -> None:
        """Export audit results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(audit_results, f, indent=2)
        print(f"[SUCCESS] Audit exported to {filename}")


def example_1_retrieve_single_key():
    """Example 1: Retrieve and display a single API key"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Retrieve Single API Key")
    print("="*80)

    admin_key = os.getenv("ANTHROPIC_ADMIN_API_KEY")
    if not admin_key:
        print("[ERROR] Set ANTHROPIC_ADMIN_API_KEY environment variable")
        return

    manager = AnthropicAPIKeyManager(admin_key)

    # Get API key ID from user or environment
    key_id = os.getenv("ANTHROPIC_API_KEY_ID") or input("Enter API Key ID: ").strip()

    if key_id:
        key_info = manager.retrieve_api_key(key_id)
        if key_info:
            manager.display_key_info(key_info)

            # Additional analysis
            print("[ANALYSIS]")
            print(f"  - Key is {key_info['status']}")
            print(f"  - Type: {key_info['type']}")
            print(f"  - Belongs to workspace: {key_info.get('workspace_id', 'Default')}")


def example_2_list_and_filter():
    """Example 2: List all keys and filter by status"""
    print("\n" + "="*80)
    print("EXAMPLE 2: List and Filter API Keys")
    print("="*80)

    admin_key = os.getenv("ANTHROPIC_ADMIN_API_KEY")
    if not admin_key:
        print("[ERROR] Set ANTHROPIC_ADMIN_API_KEY environment variable")
        return

    manager = AnthropicAPIKeyManager(admin_key)
    analyzer = APIKeyAnalyzer(manager)

    # Find all active keys
    print("\n[INFO] Finding all active keys...")
    active_keys = analyzer.find_keys_by_criteria(status='active')
    print(f"[RESULT] Found {len(active_keys)} active keys")

    if active_keys:
        manager.display_keys_summary(active_keys)

    # Find keys with 'prod' in the name
    print("\n[INFO] Finding keys with 'prod' in name...")
    prod_keys = analyzer.find_keys_by_criteria(name_contains='prod')
    print(f"[RESULT] Found {len(prod_keys)} production keys")

    if prod_keys:
        for key in prod_keys:
            print(f"  - {key['name']} ({key['status']})")


def example_3_full_audit():
    """Example 3: Perform comprehensive audit"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Comprehensive API Key Audit")
    print("="*80)

    admin_key = os.getenv("ANTHROPIC_ADMIN_API_KEY")
    if not admin_key:
        print("[ERROR] Set ANTHROPIC_ADMIN_API_KEY environment variable")
        return

    manager = AnthropicAPIKeyManager(admin_key)
    analyzer = APIKeyAnalyzer(manager)

    # Run audit
    audit_results = analyzer.audit_keys()

    if "error" not in audit_results:
        # Display report
        analyzer.display_audit_report(audit_results)

        # Export to file
        analyzer.export_audit_to_json(audit_results)


def example_4_integrate_with_research_assistant():
    """Example 4: Integration pattern for research assistant"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Research Assistant Integration Pattern")
    print("="*80)

    print("""
This example shows how to integrate API key management into your research assistant:

1. Add API Key Tool to Research Assistant:
   - Create a new tool function 'check_api_quota'
   - Use AnthropicAPIKeyManager to retrieve key info
   - Display usage statistics and limits

2. Automatic Key Rotation:
   - Monitor key age and usage
   - Alert when keys are approaching expiration
   - Suggest creating new keys for rotation

3. Cost Tracking:
   - Log API usage per key
   - Track costs across different workspaces
   - Generate monthly reports

4. Security Monitoring:
   - Audit key access patterns
   - Detect unused keys (archive candidates)
   - Alert on suspicious activity

Example Integration Code:
""")

    example_code = '''
# In your research_assistant.py

from anthropic_api_key_manager import AnthropicAPIKeyManager

def tool_check_api_quota():
    """Tool to check current API key quota and status"""
    admin_key = os.getenv("ANTHROPIC_ADMIN_API_KEY")
    current_key_id = os.getenv("ANTHROPIC_API_KEY_ID")

    manager = AnthropicAPIKeyManager(admin_key)
    key_info = manager.retrieve_api_key(current_key_id)

    if key_info:
        status = key_info['status']
        name = key_info['name']
        created = key_info['created_at']

        return f"""
API Key Status:
  Name: {name}
  Status: {status}
  Created: {created}

Recommendation: {"Key is active and healthy" if status == "active" else "Key needs attention"}
"""
    return "Could not retrieve API key information"

# Add to your tool registry
TOOLS = {
    "arxiv": tool_search_arxiv,
    "github": tool_search_github,
    "api_quota": tool_check_api_quota,  # NEW TOOL
    # ... other tools
}
'''

    print(example_code)
    print("\n" + "="*80 + "\n")


def interactive_examples_menu():
    """Interactive menu to run examples"""
    print("\n" + "="*80)
    print("API KEY MANAGEMENT - ADVANCED EXAMPLES")
    print("="*80)
    print("\nChoose an example to run:")
    print("  1. Retrieve single API key")
    print("  2. List and filter API keys")
    print("  3. Comprehensive audit")
    print("  4. Research assistant integration pattern")
    print("  5. Run all examples")
    print("  6. Exit")
    print("="*80)

    while True:
        choice = input("\nSelect example (1-6): ").strip()

        if choice == "1":
            example_1_retrieve_single_key()
        elif choice == "2":
            example_2_list_and_filter()
        elif choice == "3":
            example_3_full_audit()
        elif choice == "4":
            example_4_integrate_with_research_assistant()
        elif choice == "5":
            example_1_retrieve_single_key()
            example_2_list_and_filter()
            example_3_full_audit()
            example_4_integrate_with_research_assistant()
        elif choice == "6":
            print("\n[INFO] Exiting examples")
            break
        else:
            print("[ERROR] Invalid choice")

        if choice != "6":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        interactive_examples_menu()
    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
