# AI-Powered Threat Modeling (AITM)

> ⚠️ **This is a free demo version.** For the enterprise edition with advanced features, contact: **ai.security.tools@gmail.com**

**Automated STRIDE threat analysis for system architectures — powered by LLMs.**

Describe your system (or upload a diagram), and AITM identifies security threats, scores risks, and generates actionable mitigation recommendations.

---

## ✨ Features

- **STRIDE Analysis** — Systematic threat identification across all 6 categories
- **Architecture Diagram Support** — Analyze PNG/JPEG architecture diagrams with vision models
- **Risk Scoring** — 5-level risk matrix (Critical → Minimal) based on impact × likelihood
- **CWE Mapping** — Threats linked to Common Weakness Enumeration IDs
- **Multiple AI Providers** — Amazon Bedrock (Claude), OpenAI (GPT-4o), or Ollama (free, local)
- **Reasoning Modes** — Configurable thinking depth (off/low/medium/high)
- **Export Formats** — Markdown and JSON (PDF coming soon)
- **Extensible Architecture** — Core engine designed for CLI, API, or web frontend

---

## 🚀 Quick Start

### Install

```bash
git clone https://github.com/aisecuritytools-ai/ai-powered-threat-modeling.git
cd ai-powered-threat-modeling
pip install -e .
```

### Run with Amazon Bedrock

```bash
# Ensure AWS credentials are configured
export AWS_REGION=us-east-1

aitm analyze --description-file examples/sample-description.txt
```

### Run with OpenAI

```bash
export OPENAI_API_KEY=sk-...

aitm analyze \
  --provider openai \
  --description "A REST API with PostgreSQL database behind an nginx reverse proxy" \
  --output report.md
```

### Run with Ollama (free, local, no account needed)

```bash
# Install Ollama: https://ollama.com
brew install ollama        # macOS
# or: curl -fsSL https://ollama.com/install.sh | sh  # Linux

# Pull a model (one-time)
ollama pull llama3.1

# Run threat modeling — completely free, no API keys
aitm analyze \
  --provider ollama \
  --description "A REST API with PostgreSQL database behind an nginx reverse proxy" \
  --output report.md
```

### With Architecture Diagram

```bash
aitm analyze \
  --image architecture.png \
  --description "Our microservices platform" \
  --reasoning 2 \
  --format json \
  --output threats.json
```

---

## 📖 Usage

```
aitm analyze [OPTIONS]

Options:
  -i, --image PATH              Architecture diagram (PNG/JPEG)
  -d, --description TEXT        System description
  -f, --description-file PATH   File containing system description
  -p, --provider [bedrock|openai|ollama]  AI provider (default: bedrock)
  -m, --model TEXT              Model ID (auto-detected if not set)
  -o, --output PATH             Output file path
  --format [markdown|json]      Output format (default: markdown)
  -r, --reasoning [0-3]         Reasoning level (default: 0)
  --help                        Show help
```

---

## 📊 Example Output

```
┌─────────────────────────────────────────┐
│ AI-Powered Threat Modeling              │
│ Provider: bedrock | Model: claude-sonnet│
└─────────────────────────────────────────┘

✓ Found 18 threats
  Assets: 11 | Flows: 14

  STRIDE breakdown:
    Spoofing: 4
    Tampering: 3
    Information Disclosure: 4
    Denial of Service: 3
    Elevation of Privilege: 2
    Repudiation: 2

✓ Report saved to: threat-model.md
```

---

## 🏗️ Architecture (for contributors)

```
src/aitm/
├── cli.py              # CLI entry point (Typer)
├── core/
│   ├── config.py       # Configuration & provider settings
│   ├── models.py       # Pydantic data models (shared contract)
│   ├── llm.py          # LLM abstraction (Bedrock/OpenAI)
│   └── engine.py       # Threat modeling workflow
└── export/
    ├── json_export.py   # JSON output
    └── markdown_export.py  # Markdown report
```

**Key design decisions:**
- `core/models.py` defines the shared data contract — any future frontend/API uses the same models
- `core/engine.py` is stateless — takes inputs, returns `ThreatModelResult`
- `core/llm.py` abstracts the provider — add new providers without touching the engine
- Export is separate from analysis — add new formats without changing core logic

### Future extensions (designed for)

| Extension | How to add |
|-----------|-----------|
| **REST API** | Wrap `ThreatModelingEngine` with FastAPI routes |
| **React Frontend** | Call the API, render `ThreatModelResult` JSON |
| **AWS Lambda** | Use engine in Lambda handler, store results in DynamoDB |
| **Web Search** | Add a post-processing step that enriches threats with CVE data |
| **Attack Trees** | Add new export format that generates tree visualization |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_REGION` | For Bedrock | AWS region with Claude access |
| `AWS_PROFILE` | For Bedrock | AWS credentials profile |
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `OLLAMA_BASE_URL` | For Ollama (optional) | Ollama server URL (default: http://localhost:11434) |

### Supported Models

**Amazon Bedrock:**
- `us.anthropic.claude-sonnet-4-20250514-v1:0` (default)
- `anthropic.claude-3-5-sonnet-20241022-v2:0`
- Any Claude model with vision support

**OpenAI:**
- `gpt-4o` (default)
- `gpt-4o-mini`
- Any model supporting structured outputs

**Ollama (local, free):**
- `llama3.1` (default) — good balance of quality and speed
- `llama3.1:70b` — higher quality, needs 40GB+ RAM
- `mistral` — fast, lighter weight
- `qwen2.5` — good for structured output
- Any model available via `ollama list`

---

## 🧪 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check src/

# Run tests
pytest
```

---

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md) — Step-by-step setup and first run
- [Architecture & Design](docs/architecture.md) — How the system is structured and how to extend it
- [STRIDE Methodology](docs/stride-methodology.md) — How STRIDE is applied to threat analysis
- [Example Output](examples/output/) — See what the tool produces
- [Contributing](CONTRIBUTING.md) — How to contribute to the project

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 🗺️ Roadmap

- [x] CLI with Markdown/JSON export
- [x] Multi-provider support (Bedrock + OpenAI + Ollama)
- [x] Architecture diagram analysis
- [x] Configurable reasoning depth
- [ ] PDF export
- [ ] Iterative refinement (agentic loop with gap analysis)
- [ ] Web search for CVE enrichment
- [ ] REST API (FastAPI)
- [ ] React frontend
- [ ] AWS infrastructure (Terraform)
- [ ] Attack tree generation
- [ ] Collaboration features

---

## 💼 Enterprise Edition

This open-source version is a **fully functional demo** of the core threat modeling engine. For organizations needing production-grade security analysis, the **Enterprise Edition** includes:

### Advanced Features (Enterprise Only)

| Feature | Description |
|---------|-------------|
| **Custom Security Standards** | Load your organization's security policies (40+ standards) with intelligent LLM-based selection per architecture |
| **Baseline Security Questions** | Component-specific gap analysis questions (API, frontend, authentication, data storage) |
| **Organization Risk Matrix** | Custom 5-level risk scoring aligned to your risk appetite and compliance requirements |
| **Approved Tool Recommendations** | Mitigations reference your approved security tools with specific configurations (WAF rules, monitoring thresholds, scanner configs) |
| **ISO27001 Controls Mapping** | Automatic compliance mapping of each threat to relevant ISO27001 controls |
| **Web Search Integration** | Real-time CVE lookup and security best practices from OWASP, NIST, CWE using Google Gemini with caching |
| **SME Comparison** | Upload existing threat model PDFs from security experts — AI compares and flags rating discrepancies |
| **Multi-File Upload** | Analyze 2-3 architecture diagrams per submission for comprehensive coverage |
| **User Activity Tracking** | Full audit trail (who edited what, when) for compliance and accountability |
| **Collaboration** | Share threat models with team members, role-based access control, edit locking |
| **Custom Export Templates** | Configurable PDF/DOCX/Excel exports with section selection, column filtering, and risk-level filtering |
| **SSO Integration** | Enterprise single sign-on (OIDC/SAML) with your identity provider |
| **Full Web UI** | React-based dashboard with interactive threat catalog, attack tree visualization, and AI assistant |
| **AWS Infrastructure** | Production-ready Terraform deployment with encryption, DLQ, monitoring, and multi-environment support |
| **CI/CD Integration** | GitLab/GitHub pipeline templates for automated threat modeling in your SDLC |
| **Knowledge Base** | Attach organization documents (runbooks, policies, architecture guides) to enrich analysis |
| **Metadata Generation** | Scripts to generate and maintain your security knowledge base with LLM assistance |

### Contact

📧 **ai.security.tools@gmail.com**

- Custom deployment and integration support
- On-premise or private cloud options
- Volume licensing for teams
- Priority support and SLA
