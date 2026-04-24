# DiagnoSmart System Overview (For Report)

```mermaid
flowchart LR
  U[User] -->|symptom text| CLI[CLI Entrypoint\n`diagnosmart/main.py`]

  CLI --> INIT[init_llm()\nChatOllama (optional)]
  INIT -->|llm or None| WG[LangGraph Workflow\nStateGraph(GlobalState)]

  subgraph STATE[Shared Global State (GlobalState)]
    S0[user_input]
    S1[symptoms + duration + severity]
    S2[conditions]
    S3[advice]
    S4[risk_level]
  end

  WG --> A1[Agent 1: Symptom Analyzer\n`run_symptom_analyzer`]
  A1 -->|updates| S1
  A1 --> T1[Tool: Symptom Parser\n`extract_symptoms`]

  WG --> A2[Agent 2: Medical Research\n`run_medical_research`]
  A2 -->|updates| S2
  A2 --> T2[Tool: Disease Lookup\n`find_conditions`]
  T2 --> D1[(Local Data\n`data/diseases.json`)]

  WG --> A3[Agent 3: Diagnosis Generator\n`run_diagnosis_generator`]
  A3 -->|updates| S3
  A3 --> T3[Tool: Advice Generator\n`generate_advice`]

  WG --> A4[Agent 4: Risk Validator\n`run_risk_validator`]
  A4 -->|updates| S4
  A4 --> T4[Tool: Risk Assessment\n`assess_risk`]

  A1 --> A2 --> A3 --> A4

  A4 --> OUT[Final Output JSON\nsymptoms, conditions, advice, risk_level]

  subgraph OBS[Observability / Logging]
    L[log_event(...)] --> F[(JSON Log File\n`diagnosmart/diagnosmart.log`)]
    L --> C[Console Timeline\nSTART/TOOL/DONE/ERROR]
  end

  A1 --> L
  T1 --> L
  A2 --> L
  T2 --> L
  A3 --> L
  T3 --> L
  A4 --> L
  T4 --> L

  INIT -. if Ollama down .->|tool-only mode| WG
```

```mermaid
sequenceDiagram
  participant User
  participant CLI as main.py
  participant LLM as Ollama (optional)
  participant SA as SymptomAnalyzer
  participant MR as MedicalResearch
  participant DG as DiagnosisGenerator
  participant RV as RiskValidator
  participant LOG as Logger (file+console)

  User->>CLI: Enter symptom description
  CLI->>LLM: init_llm()
  alt Ollama reachable
    Note over SA, RV: Each agent may call LLM to validate/justify\nand logs agent_reasoning
  else Ollama unreachable
    Note over SA, RV: Agents continue in tool-only mode\nand log agent_error for LLM calls
  end

  CLI->>SA: Invoke node 1
  SA->>LOG: agent_start + tool_output + agent_output
  SA->>MR: Pass GlobalState

  MR->>LOG: agent_start + tool_output + agent_output
  MR->>DG: Pass GlobalState

  DG->>LOG: agent_start + tool_output + agent_output
  DG->>RV: Pass GlobalState

  RV->>LOG: agent_start + tool_output + agent_output
  RV-->>CLI: Final GlobalState
  CLI-->>User: Print final JSON result
```

Notes:
- The reference implementation lives under `diagnosmart/`.
- A functionally equivalent demo entrypoint exists at `member_handoffs/shared_integration/main.py`.
