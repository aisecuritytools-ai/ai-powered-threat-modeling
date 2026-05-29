<p align="center">
  <img src="https://img.shields.io/badge/🛡️_AI_Powered-Threat_Modeling-0066FF?style=for-the-badge&labelColor=000000" alt="AI Threat Modeling"/>
</p>

<p align="center">
  <strong>Automated STRIDE threat analysis for system architectures — powered by LLMs</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Bedrock-Claude_4-FF9900?style=flat-square&logo=amazonaws&logoColor=white" alt="Bedrock"/>
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=flat-square&logo=openai&logoColor=white" alt="OpenAI"/>
  <img src="https://img.shields.io/badge/Ollama-Local_Free-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
</p>

<p align="center">
  <a href="docs/getting-started.md">Getting Started</a> •
  <a href="docs/stride-methodology.md">STRIDE Methodology</a> •
  <a href="examples/output/">Example Output</a> •
  <a href="#-enterprise-edition">Enterprise</a>
</p>

---

> 💡 **Free & open-source.** For the enterprise edition with 16+ advanced features, contact **ai.security.tools@gmail.com**

---

## What is AITM?

Describe your system architecture (or upload a diagram), and AITM automatically:

1. **Identifies assets** — components, services, databases, external dependencies
2. **Maps data flows** — communication paths, protocols, encryption status
3. **Discovers threats** — using STRIDE methodology with CWE mapping
4. **Scores risks** — 5-level matrix (Critical → Minimal)
5. **Recommends mitigations** — specific, actionable fixes for each threat

All in one command. No manual spreadsheets. No security expertise required.

---

## ⚡ Quick Start

```bash
# Install
git clone https://github.com/aisecuritytools-ai/ai-powered-threat-modeling.git
cd ai-powered-threat-modeling
pip install -e .

# Run (choose your provider)
aitm analyze --provider ollama -d "A REST API with PostgreSQL behind nginx"
aitm analyze --provider openai -d "Microservices on Kubernetes with Redis cache"
aitm analyze --provider bedrock --image architecture.png -d "Our payment platform"
```

**No cloud account needed?** Use Ollama — runs 100% locally, completely free:
```bash
brew install ollama && ollama pull llama3.1
aitm analyze --provider ollama --description-file examples/sample-description.txt
```

---

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🔍 **STRIDE Analysis** | Systematic threat identification across all 6 categories |
| 🖼️ **Diagram Analysis** | Upload PNG/JPEG architecture diagrams — AI reads them |
| 📊 **Risk Scoring** | 5-level matrix: Critical, High, Medium, Low, Minimal |
| 🔗 **CWE Mapping** | Every threat linked to Common Weakness Enumeration |
| 🧠 **Multi-Provider** | Amazon Bedrock, OpenAI, or Ollama (free/local) |
| 💭 **Reasoning Modes** | Configurable thinking depth for complex architectures |
| 📄 **Export** | Markdown and JSON reports |
| 🏗️ **Extensible** | Core engine ready for API, frontend, or Lambda wrapper |

---

## 📋 Usage

```
aitm analyze [OPTIONS]

Options:
  -i, --image PATH              Architecture diagram (PNG/JPEG)
  -d, --description TEXT        System description
  -f, --description-file PATH   File with system description
  -p, --provider [bedrock|openai|ollama]  AI provider (default: bedrock)
  -m, --model TEXT              Model ID (auto-detected if not set)
  -o, --output PATH             Output file path
  --format [markdown|json]      Output format (default: markdown)
  -r, --reasoning [0-3]         Reasoning depth (0=off, 3=deep)
```

---

## 📊 Example Output

<details>
<summary><strong>Click to see terminal output</strong></summary>

```
┌─────────────────────────────────────────────┐
│  AI-Powered Threat Modeling                 │
│  Provider: bedrock | Model: claude-sonnet-4 │
└─────────────────────────────────────────────┘

✓ Found 18 threats
  Assets: 11 | Flows: 14

  STRIDE breakdown:
    Tampering: 5
    Spoofing: 4
    Information Disclosure: 4
    Elevation of Privilege: 3
    Denial of Service: 1
    Repudiation: 1

✓ Report saved to: threat-model.md
```

</details>

<details>
<summary><strong>Click to see sample threat (from Markdown report)</strong></summary>

> ### 🔴 [1] SQL Injection in Order Service Database Queries
>
> - **STRIDE:** Tampering
> - **Target:** Order Service
> - **Impact:** High | **Likelihood:** High
> - **CWE:** CWE-89
>
> If the Order Service constructs SQL queries using string concatenation with user-supplied input, an attacker could extract all customer data, modify orders, or drop tables.
>
> **Mitigations:**
> - Use parameterized queries (prepared statements) for all database operations
> - Implement input validation with strict type checking and length limits
> - Deploy a WAF rule to detect and block SQL injection patterns
> - Enable PostgreSQL audit logging to detect anomalous query patterns

</details>

📁 Full example reports: [`examples/output/`](examples/output/)

---

## 🏗️ Architecture

```
src/aitm/
├── cli.py              # CLI interface (Typer + Rich)
├── core/
│   ├── config.py       # Provider configuration
│   ├── models.py       # Shared data contract (Pydantic)
│   ├── llm.py          # LLM abstraction layer
│   └── engine.py       # Stateless threat modeling workflow
└── export/
    ├── json_export.py
    └── markdown_export.py
```

**Design principles:**
- Engine is **stateless** — wrap it with any interface (CLI today, API tomorrow)
- Models are the **shared contract** — same Pydantic schemas for CLI, API, and frontend
- Provider is **abstracted** — add new LLMs without touching analysis logic

---

## ⚙️ Supported Models

| Provider | Model | Cost | Quality | Setup |
|----------|-------|------|---------|-------|
| **Ollama** | llama3.1 | Free | Good | `brew install ollama` |
| **OpenAI** | gpt-4o | ~$0.01/run | Excellent | API key |
| **Bedrock** | Claude Sonnet 4 | ~$0.01/run | Excellent | AWS account |

---

## 📚 Documentation

| Doc | Description |
|-----|-------------|
| [Getting Started](docs/getting-started.md) | Step-by-step setup and first run |
| [Architecture](docs/architecture.md) | System design and extension guide |
| [STRIDE Methodology](docs/stride-methodology.md) | How STRIDE analysis works |
| [Example Output](examples/output/) | Sample reports you can browse |
| [Contributing](CONTRIBUTING.md) | How to contribute |

---

## 🗺️ Roadmap

- [x] CLI with Markdown/JSON export
- [x] Multi-provider (Bedrock + OpenAI + Ollama)
- [x] Architecture diagram analysis (vision)
- [x] Configurable reasoning depth
- [ ] PDF export
- [ ] Agentic loop with gap analysis
- [ ] CVE enrichment via web search
- [ ] REST API (FastAPI)
- [ ] React frontend
- [ ] Terraform infrastructure

---

## 💼 Enterprise Edition

The open-source version is a **fully functional** threat modeling engine. The Enterprise Edition adds production-grade capabilities for security teams:

| | Open Source | Enterprise |
|---|:---:|:---:|
| STRIDE threat analysis | ✅ | ✅ |
| Multi-provider AI | ✅ | ✅ |
| Diagram analysis | ✅ | ✅ |
| Risk scoring | ✅ | ✅ |
| Markdown/JSON export | ✅ | ✅ |
| Custom security standards (40+) | — | ✅ |
| Baseline security questions | — | ✅ |
| Organization risk matrix | — | ✅ |
| ISO27001 controls mapping | — | ✅ |
| Approved tool recommendations | — | ✅ |
| Web search (CVE/OWASP/NIST) | — | ✅ |
| SME comparison (PDF upload) | — | ✅ |
| Multi-file upload | — | ✅ |
| User activity tracking | — | ✅ |
| Collaboration & sharing | — | ✅ |
| Custom export templates | — | ✅ |
| SSO integration (OIDC/SAML) | — | ✅ |
| Full web UI + AI assistant | — | ✅ |
| AWS infrastructure (Terraform) | — | ✅ |
| CI/CD pipeline integration | — | ✅ |
| Knowledge base | — | ✅ |
| Priority support & SLA | — | ✅ |

<p align="center">
  <br/>
  📧 <strong>ai.security.tools@gmail.com</strong><br/>
  Custom deployment • On-premise • Volume licensing • Integration support
</p>

---

<p align="center">
  <sub>MIT License • Built for security engineers, by security engineers</sub>
</p>
