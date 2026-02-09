# NiFi Flow Summary

A tool to generate executive-friendly summaries of Apache NiFi flows using a local LLM.

## Installation
```bash
pip install -r requirements.txt
# Or (optional) install as package:
# pip install .
```

## Example usage

nifi-flow-summary --input /Users/me/flows/flow.json.gz \
                   --output /Users/me/flows/flow_report.md \
                   --config /Users/me/flows/config.yaml

# Sample run
python3.11 -m nifi_flow_summary.cli \
  --input flow.json.gz \
  --config config.yaml \
  --output report.md

# Sample reports
1. developer_report.md
2. report.md
