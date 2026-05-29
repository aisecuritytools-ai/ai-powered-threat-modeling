# Getting Started

This guide walks you through installing and running your first threat model.

---

## Step 1: Install AITM

```bash
git clone https://github.com/aisecuritytools-ai/ai-powered-threat-modeling.git
cd ai-powered-threat-modeling
pip install -e .
```

Verify installation:

```bash
aitm version
# Output: aitm v0.1.0
```

---

## Step 2: Choose Your AI Provider

You need ONE of these three options:

### Option A: Ollama (Free, Local — Recommended for trying out)

No account needed. Runs entirely on your machine.

```bash
# Install Ollama
brew install ollama          # macOS
# or: curl -fsSL https://ollama.com/install.sh | sh   # Linux

# Start Ollama (runs in background)
ollama serve

# Pull a model (one-time download, ~4GB)
ollama pull llama3.1
```

**Requirements:** 8GB+ RAM (16GB recommended for best results)

### Option B: OpenAI (Best quality, needs API key)

1. Sign up at [openai.com](https://openai.com)
2. Go to API Keys → Create new key
3. Set the environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

**Cost:** ~$0.01-0.05 per threat model run

### Option C: Amazon Bedrock (Enterprise, needs AWS account)

1. Have an AWS account with Bedrock access
2. Enable Claude Sonnet 4 in your region ([instructions](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html))
3. Configure AWS credentials:

```bash
export AWS_PROFILE="your-profile"
export AWS_REGION="us-east-1"
```

**Cost:** ~$0.003-0.015 per run

---

## Step 3: Run Your First Threat Model

### Using a text description

```bash
aitm analyze \
  --provider ollama \
  --description "A web application with React frontend, Node.js REST API, and PostgreSQL database. Users authenticate via JWT tokens. The API is behind an nginx reverse proxy."
```

### Using a description file

```bash
aitm analyze \
  --provider ollama \
  --description-file examples/sample-description.txt
```

### Using an architecture diagram

```bash
aitm analyze \
  --provider openai \
  --image my-architecture.png \
  --description "Our cloud-native payment platform"
```

---

## Step 4: View Results

By default, AITM saves a `threat-model.md` file in your current directory.

```bash
# View in terminal
cat threat-model.md

# Or open in your editor
code threat-model.md
```

### Choose output format

```bash
# Markdown (default — human-readable)
aitm analyze --provider ollama -d "My system" --format markdown -o report.md

# JSON (machine-readable — for integrations)
aitm analyze --provider ollama -d "My system" --format json -o report.json
```

---

## Step 5: Customize the Analysis

### Change the model

```bash
# Use a larger Ollama model for better results
aitm analyze --provider ollama --model llama3.1:70b -d "My system"

# Use GPT-4o-mini for faster/cheaper OpenAI runs
aitm analyze --provider openai --model gpt-4o-mini -d "My system"
```

### Enable reasoning (deeper analysis)

```bash
# Level 1 = light reasoning, Level 3 = deep reasoning
aitm analyze --provider bedrock --reasoning 2 -d "My system"
```

Reasoning makes the AI "think longer" before answering. Higher levels produce more thorough analysis but take longer and cost more.

| Level | Depth | Speed | Best for |
|-------|-------|-------|----------|
| 0 | Standard | Fast | Quick scans |
| 1 | Light | Medium | Most use cases |
| 2 | Medium | Slower | Complex architectures |
| 3 | Deep | Slowest | Critical systems |

> **Note:** Reasoning is only supported by Bedrock (Claude) and OpenAI. Ollama ignores this setting.

---

## Tips for Better Results

### Write good descriptions

**Bad:**
```
A web app with a database
```

**Good:**
```
An e-commerce platform with:
- React SPA served via CloudFront
- REST API (Node.js) behind API Gateway with rate limiting
- PostgreSQL database storing user PII and payment references
- Redis cache for sessions (30-minute TTL)
- Authentication via Keycloak (OAuth2/OIDC)
- Payment processing via Stripe API (PCI DSS scope)
- All inter-service communication uses mTLS
```

The more detail you provide, the more specific and actionable the threats will be.

### Include trust boundaries

Mention where trust boundaries exist:
- "The API is public-facing"
- "The database is in a private subnet"
- "Stripe is an external third-party service"

### Mention sensitive data

Call out what's sensitive:
- "Stores PII (names, emails, addresses)"
- "Processes payment card data"
- "Contains healthcare records (HIPAA)"

### Use architecture diagrams

Diagrams help the AI understand component relationships that are hard to describe in text. Use PNG or JPEG format.

---

## Example Workflows

### Security review for a new feature

```bash
aitm analyze \
  --provider openai \
  --description "New feature: users can upload profile photos. Photos stored in S3, served via CloudFront. Upload goes through API Gateway → Lambda → S3. Max file size 5MB, JPEG/PNG only." \
  --output feature-review.md
```

### Full system threat model

```bash
aitm analyze \
  --provider bedrock \
  --image system-architecture.png \
  --description-file system-description.txt \
  --reasoning 2 \
  --output full-threat-model.md
```

### Quick check with local model

```bash
aitm analyze \
  --provider ollama \
  --description "Kubernetes cluster with 3 microservices, Istio service mesh, and external PostgreSQL" \
  --output quick-check.md
```

---

## Troubleshooting

### "Connection refused" with Ollama

Ollama server isn't running:
```bash
ollama serve
```

### "Model not found" with Ollama

Pull the model first:
```bash
ollama pull llama3.1
```

### "AccessDeniedException" with Bedrock

Enable the model in AWS Console:
1. Go to Amazon Bedrock → Model access
2. Request access to Claude Sonnet 4
3. Wait for approval (usually instant)

### "Invalid API key" with OpenAI

Check your key is set:
```bash
echo $OPENAI_API_KEY
```

### Output quality is poor (Ollama)

Try a larger model:
```bash
ollama pull llama3.1:70b
aitm analyze --provider ollama --model llama3.1:70b -d "..."
```

Or switch to OpenAI/Bedrock for production-quality results.

---

## Next Steps

- See [example output](../examples/output/) for what a full report looks like
- Read [STRIDE methodology](stride-methodology.md) to understand the threat categories
- Read [architecture docs](architecture.md) to understand how to extend AITM
