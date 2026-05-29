# Architecture

## Design Principles

1. **Stateless Engine** — The core `ThreatModelingEngine` takes inputs and returns results. No side effects, no database calls. This makes it trivial to wrap with any interface.

2. **Shared Data Contract** — `core/models.py` defines Pydantic models that are the single source of truth. CLI, API, and frontend all use the same models.

3. **Provider Abstraction** — `core/llm.py` hides provider differences. The engine doesn't know or care if it's talking to Bedrock or OpenAI.

4. **Separation of Concerns** — Analysis (engine) is separate from presentation (export). Add new formats without touching analysis logic.

## Component Diagram

```
┌────────────────────────────────────────────────────────┐
│                    Interfaces                           │
│  ┌─────────┐   ┌──────────┐   ┌────────────────────┐  │
│  │   CLI   │   │ REST API │   │  Lambda Handler    │  │
│  │ (typer) │   │ (future) │   │  (future)          │  │
│  └────┬────┘   └────┬─────┘   └─────────┬──────────┘  │
└───────┼──────────────┼───────────────────┼─────────────┘
        │              │                   │
        ▼              ▼                   ▼
┌────────────────────────────────────────────────────────┐
│                  Core Engine                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ThreatModelingEngine                            │  │
│  │  - identify_assets()                             │  │
│  │  - identify_data_flows()                         │  │
│  │  - identify_threats()                            │  │
│  └──────────────────────┬───────────────────────────┘  │
│                         │                              │
│  ┌──────────────────────▼───────────────────────────┐  │
│  │  LLM Abstraction (core/llm.py)                   │  │
│  │  - create_llm(config) → ChatModel                │  │
│  │  - invoke_structured(llm, messages, schema)      │  │
│  └──────────────────────┬───────────────────────────┘  │
└─────────────────────────┼──────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                                   ▼
┌───────────────┐                   ┌───────────────┐
│ Amazon Bedrock│                   │    OpenAI     │
│ (Claude)      │                   │  (GPT-4o)     │
└───────────────┘                   └───────────────┘
```

## Data Flow

```
Input (description + optional image)
    │
    ▼
┌─────────────────────┐
│ 1. Identify Assets  │ → AssetList (structured output)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 2. Identify Flows   │ → DataFlowList (structured output)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 3. Identify Threats │ → ThreatList (structured output)
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 4. Package Result   │ → ThreatModelResult
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ 5. Export           │ → Markdown / JSON / PDF
└─────────────────────┘
```

## Adding a REST API (future)

```python
# backend/api.py
from fastapi import FastAPI, UploadFile
from aitm.core.engine import ThreatModelingEngine
from aitm.core.config import AITMConfig
from aitm.core.models import ThreatModelResult

app = FastAPI()

@app.post("/analyze", response_model=ThreatModelResult)
async def analyze(description: str, image: UploadFile = None):
    config = AITMConfig()
    engine = ThreatModelingEngine(config)
    result = engine.run(description=description, image_path=image)
    return result
```

The engine doesn't change — you just add a new interface on top.
