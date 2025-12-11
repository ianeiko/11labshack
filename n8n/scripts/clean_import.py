import json
import os
import subprocess
import glob
import sys
import uuid

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

    os.makedirs(temp_dir, exist_ok=True)

    print(f"Processing workflows from {workflows_dir}...")

    # Get all JSON files
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

            # 1. Remove Top-Level ID and versionId
            # Keeping these can cause conflicts if the server has existing workflows with same IDs
            if "id" in data:
                print(f"  Stripping ID {data['id']} from {os.path.basename(file_path)}")
                del data["id"]

            # Generate new versionId to avoid DB constraints
            data["versionId"] = str(uuid.uuid4())

            # 2. Set active to false
            # We don't want them running immediately upon import
            # 2. Set active to false
            # We don't want them running immediately upon import
            data["active"] = False

            # NEW: Regenerate webhookId for nodes
            # If multiple workflows have the same webhookId, n8n prevents activation
            # We used to delete it, but that might cause 'missing property' errors.
            # Regenerating ensures uniqueness and validity.
            if "nodes" in data and isinstance(data["nodes"], list):
                for node in data["nodes"]:
                    if "webhookId" in node:
                        new_id = str(uuid.uuid4())
                        print(f"    Regenerating webhookId for node {node.get('name', 'Unknown')}: {new_id}")
                        node["webhookId"] = new_id

            # 3. Save to temp file in the workflows directory (mounted)
            # This ensures n8n container can see it at /workflows/...
            filename = os.path.basename(file_path)
            temp_filename = f"_import_{filename}"
            host_temp_path = os.path.join(workflows_dir, temp_filename)
            container_temp_path = f"/workflows/{temp_filename}"

            with open(host_temp_path, 'w') as f:
                json.dump(data, f, indent=2)

            # 4. Import using n8n CLI pointing to the mounted file
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
                print(f"  Successfully imported {filename} (Cleaned)")
                processed_count += 1
            else:
                print(f"  Failed to import {filename}")
                print(f"  Stdout: {result.stdout.decode('utf-8')}")
                print(f"  Stderr: {result.stderr.decode('utf-8')}")

        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            # Ensure cleanup
            temp_filename = f"_import_{os.path.basename(file_path)}"
            host_temp_path = os.path.join(workflows_dir, temp_filename)
            if os.path.exists(host_temp_path):
                os.remove(host_temp_path)

    print(f"\nCompleted. Imported {processed_count} workflows.")

if __name__ == "__main__":
    main()
