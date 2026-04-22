# DiagnoSmart - AI-Based Multi-Agent System for Intelligent Medical Decision Support

DiagnoSmart is a local-first Multi-Agent System (MAS) for preliminary symptom analysis and medical decision support.

## Key Features
- Local execution only (no paid APIs)
- Ollama-powered local small language model support
- LangGraph orchestration with exactly 4 agents
- 4 custom Python tools (one per agent)
- Shared global state for context preservation
- Structured logging for observability
- Agent-level test coverage with edge cases

## Architecture
Sequential pipeline:
1. Symptom Analyzer Agent
2. Medical Research Agent
3. Diagnosis Generator Agent
4. Risk Validator Agent

## Project Structure

```
diagnosmart/
|-- main.py
|-- config.py
|-- requirements.txt
|-- README.md
|-- agents/
|   |-- symptom_analyzer.py
|   |-- medical_research.py
|   |-- diagnosis_generator.py
|   `-- risk_validator.py
|-- tools/
|   |-- symptom_parser.py
|   |-- disease_lookup.py
|   |-- advice_generator.py
|   `-- risk_assessment.py
|-- data/
|   `-- diseases.json
|-- state/
|   `-- global_state.py
|-- orchestration/
|   `-- workflow.py
|-- tests/
|   |-- test_analyzer.py
|   |-- test_research.py
|   |-- test_generator.py
|   `-- test_validator.py
`-- utils/
    `-- logger.py
```

## Setup
1. Install dependencies:
   - python -m venv .venv
   - source .venv/bin/activate
   - pip install -r requirements.txt

2. Install and run Ollama locally:
   - Install Ollama from https://ollama.com
   - Pull a model:
     - ollama pull llama3:8b
   - Keep Ollama service running

3. Run the app:
   - python main.py

4. Run tests:
   - pytest -q

## Example Input
I have fever, headache, and body ache for 2 days with moderate pain.

## Example Output Format
```
{
  "symptoms": ["fever", "headache", "body ache"],
  "conditions": ["Influenza (Flu)", "COVID-19"],
  "advice": "... This is not a medical diagnosis. Please consult a doctor.",
  "risk_level": "MEDIUM"
}
```

## Safety Note
This project provides educational and preliminary guidance only.
It is not a substitute for professional medical diagnosis.
