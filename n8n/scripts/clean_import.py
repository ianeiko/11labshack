import json
import os
import subprocess
import glob
import sys
import uuid
import requests

def main():
    workflows_dir = "../workflows"
    temp_dir = "../temp_clean_workflows"

    # Ensure we are in the scripts directory or adjust paths
    if not os.path.exists(workflows_dir):
        # Fallback if running from root
        workflows_dir = "workflows"
        temp_dir = "temp_clean_workflows"

    if not os.path.exists(workflows_dir):
        print(f"Error: Workflows directory '{workflows_dir}' not found.")
        sys.exit(1)

    # Check for API configuration
    api_url = os.getenv("N8N_API_URL", "http://localhost:5678/api/v1").rstrip('/')
    if not api_url.endswith("/api/v1"):
        api_url += "/api/v1"

    api_key = os.getenv("N8N_API_KEY")
    if api_key:
        api_key = api_key.strip()
    use_api = False

    if api_key:
        use_api = True
        print(f"N8N_API_KEY found. Importing via API to {api_url}")
    else:
        print("N8N_API_KEY not set. Falling back to local Docker CLI import.")
        os.makedirs(temp_dir, exist_ok=True)

    print(f"Processing workflows from {workflows_dir}...")

    # Get all JSON files (recursively)
    workflow_files = glob.glob(os.path.join(workflows_dir, "**", "*.json"), recursive=True)

    if not workflow_files:
        print("No workflow files found.")
        return

    processed_count = 0

    for file_path in workflow_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # 1. Remove Top-Level ID
            # Keeping these can cause conflicts if the server has existing workflows with same IDs
            if "id" in data:
                print(f"  Stripping ID {data['id']} from {os.path.basename(file_path)}")
                del data["id"]

            # Generate new versionId to avoid DB constraints
            data["versionId"] = str(uuid.uuid4())

            # 2. Set active to false
            data["active"] = False

            # Regenerate webhookId for nodes
            if "nodes" in data and isinstance(data["nodes"], list):
                for node in data["nodes"]:
                    if "webhookId" in node:
                        new_id = str(uuid.uuid4())
                        print(f"    Regenerating webhookId for node {node.get('name', 'Unknown')}: {new_id}")
                        node["webhookId"] = new_id

            if use_api:
                # Import via API
                try:
                    headers = {
                        "X-N8N-API-KEY": api_key,
                        "Content-Type": "application/json"
                    }
                    response = requests.post(f"{api_url}/workflows", json=data, headers=headers)
                    response.raise_for_status()
                    new_wf = response.json()
                    print(f"  Successfully imported {os.path.basename(file_path)} (API ID: {new_wf.get('id')})")
                    processed_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"  Failed to import {os.path.basename(file_path)} via API")
                    if hasattr(e, 'response') and e.response is not None:
                         print(f"  Response: {e.response.text}")
                    else:
                         print(f"  Error: {e}")

            else:
                # Import via Docker CLI
                filename = os.path.basename(file_path)
                temp_filename = f"_import_{filename}"
                host_temp_path = os.path.join(workflows_dir, temp_filename)
                container_temp_path = f"/workflows/{temp_filename}"

                with open(host_temp_path, 'w') as f:
                    json.dump(data, f, indent=2)

                # Import using n8n CLI pointing to the mounted file
                cmd = ["docker", "compose", "exec", "-T", "n8n", "n8n", "import:workflow", f"--input={container_temp_path}"]

                # Run import command
                result = subprocess.run(
                    cmd,
                    capture_output=True
                )

                # Clean up temp file immediately
                if os.path.exists(host_temp_path):
                    os.remove(host_temp_path)

                if result.returncode == 0:
                    print(f"  Successfully imported {filename} (CLI)")
                    processed_count += 1
                else:
                    print(f"  Failed to import {filename}")
                    print(f"  Stdout: {result.stdout.decode('utf-8')}")
                    print(f"  Stderr: {result.stderr.decode('utf-8')}")

        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            if not use_api:
                # Ensure cleanup for CLI method
                temp_filename = f"_import_{os.path.basename(file_path)}"
                host_temp_path = os.path.join(workflows_dir, temp_filename)
                if os.path.exists(host_temp_path):
                    os.remove(host_temp_path)

    print(f"\nCompleted. Imported {processed_count} workflows.")

if __name__ == "__main__":
    main()
