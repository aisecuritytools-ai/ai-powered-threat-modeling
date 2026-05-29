# Example Output

These files show what AITM produces when analyzing the [sample e-commerce architecture](../sample-description.txt).

## Files

| File | Format | Description |
|------|--------|-------------|
| `threat-model.md` | Markdown | Full threat model report with risk-sorted threats |
| `threat-model.json` | JSON | Structured output for programmatic consumption |

## How these were generated

```bash
# Markdown output
aitm analyze \
  --description-file ../sample-description.txt \
  --output threat-model.md \
  --format markdown

# JSON output
aitm analyze \
  --description-file ../sample-description.txt \
  --output threat-model.json \
  --format json
```

## What to expect

- **11 assets** identified from the architecture description
- **14 data flows** mapped between components
- **18 threats** across all STRIDE categories
- Each threat includes risk level, CWE ID, attack vector, and 2-4 mitigations
- Threats sorted by risk: Critical → High → Medium → Low → Minimal
