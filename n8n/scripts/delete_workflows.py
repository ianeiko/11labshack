import os
import requests
import sys
import json

def delete_all_workflows():
    # Configuration
    api_url = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1").rstrip('/')
    if not api_url.endswith("/api/v1"):
        api_url += "/api/v1"

    api_key = os.getenv("N8N_API_KEY")
    if api_key:
        api_key = api_key.strip()

    if not api_key:
        print("Error: N8N_API_KEY environment variable is not set.")
        sys.exit(1)

    print(f"Using N8N API URL: {api_url}")

    # Headers for authentication
    headers = {
        "X-N8N-API-KEY": api_key
    }

    try:
        # Fetch all workflows
        print("Fetching workflows...")
        workflows_url = f"{api_url}/workflows"
        response = requests.get(workflows_url, headers=headers)

        try:
            response.raise_for_status()
            # Try to parse JSON
            response_json = response.json()
            workflows = response_json.get('data', [])
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error: Failed to parse JSON response from {workflows_url}")
            print(f"Status Code: {response.status_code}")
            print(f"Response Content (first 500 chars):\n{response.text[:500]}...")
            if response.status_code == 200 and "<html" in response.text.lower():
               print("\n[HINT] The response looks like HTML. You might be missing '/api/v1' in your N8N_API_URL.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response: {response.text}")
            sys.exit(1)

        if not workflows:
            print("No workflows found to delete.")
            return

        print(f"Found {len(workflows)} workflows. Deleting...")

        for workflow in workflows:
            wf_id = workflow.get('id')
            wf_name = workflow.get('name')

            print(f"Deleting workflow: {wf_name} ({wf_id})...", end="")

            try:
                delete_response = requests.delete(f"{api_url}/workflows/{wf_id}", headers=headers)
                delete_response.raise_for_status()
                print(" Done.")
            except requests.exceptions.RequestException as e:
                print(f" Failed! Status: {delete_response.status_code if 'delete_response' in locals() else 'Unknown'} - {e}")

        print("\nAll workflows verified cleared.")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with n8n API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    confirm = input("Are you sure you want to DELETE ALL workflows? This cannot be undone. (y/N): ")
    if confirm.lower() == 'y':
        delete_all_workflows()
    else:
        print("Operation cancelled.")
