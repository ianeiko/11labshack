import os
import requests
import sys

def delete_all_workflows():
    # Configuration
    api_url = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1")
    api_key = os.getenv("N8N_API_KEY")

    if not api_key:
        print("Error: N8N_API_KEY environment variable is not set.")
        sys.exit(1)

    # Headers for authentication
    headers = {
        "X-N8N-API-KEY": api_key
    }

    try:
        # Fetch all workflows
        print("Fetching workflows...")
        response = requests.get(f"{api_url}/workflows", headers=headers)
        response.raise_for_status()
        workflows = response.json().get('data', [])

        if not workflows:
            print("No workflows found to delete.")
            return

        print(f"Found {len(workflows)} workflows. Deleting...")

        for workflow in workflows:
            wf_id = workflow.get('id')
            wf_name = workflow.get('name')

            print(f"Deleting workflow: {wf_name} ({wf_id})...", end="")

            delete_response = requests.delete(f"{api_url}/workflows/{wf_id}", headers=headers)
            if delete_response.status_code == 200:
                print(" Done.")
            else:
                print(f" Failed! Status: {delete_response.status_code} - {delete_response.text}")

        print("\nAll workflows verified cleared.")

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with n8n API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)

if __name__ == "__main__":
    confirm = input("Are you sure you want to DELETE ALL workflows? This cannot be undone. (y/N): ")
    if confirm.lower() == 'y':
        delete_all_workflows()
    else:
        print("Operation cancelled.")
