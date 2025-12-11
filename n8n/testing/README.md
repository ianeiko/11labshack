# N8N Workflow Testing

This directory contains Python tests for verifying the N8N workflows. These tests simulate external API calls to the N8N webhooks.

## ⚠️ Prerequisites

1.  **N8N Running**: Your N8N instance must be running (e.g., at `http://localhost:5678`).
2.  **Workflows Active**: **CRITICAL!** The workflows you are testing must be **Active** in N8N. If they are not active, the webhook URLs will fail with a 404 (unless you are using the Test URL, but these tests typically target the Production URL).
    *   *Tip:* If testing locally during development, ensure your `.env` or test scripts point to the correct webhook URL format (Production vs Test). Currently, scripts default to `http://localhost:5678/webhook/...` which usually requires the workflow to be Active.

## 📦 Setup

Install the required Python packages:

```bash
pip install pytest requests
```

## 🚀 Running Tests

### Run All Tests
To run the entire test suite:

```bash
pytest n8n/testing/
```

### Run a Single Test
To test a specific workflow (e.g., creating agents):

```bash
pytest n8n/testing/test_1.0_create_agents.py
```

## 📂 Test Data
These tests use mock data located in `n8n/workflows/tests/mock_data/`. This ensures consistent payloads for requests.
