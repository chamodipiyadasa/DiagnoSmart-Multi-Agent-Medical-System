# Contribution Guide for 4 Members

Use this guide to show clear individual contribution evidence in Git history.

## Member 1 - Symptom Analyzer
Own these files:
- agents/symptom_analyzer.py
- tools/symptom_parser.py
- tests/test_analyzer.py

Suggested commit:
- feat(analyzer): add symptom analyzer agent, parser tool, and tests

## Member 2 - Medical Research
Own these files:
- agents/medical_research.py
- tools/disease_lookup.py
- tests/test_research.py
- data/diseases.json

Suggested commit:
- feat(research): add medical research agent, disease lookup tool, and tests

## Member 3 - Diagnosis Generator
Own these files:
- agents/diagnosis_generator.py
- tools/advice_generator.py
- tests/test_generator.py

Suggested commit:
- feat(generator): add diagnosis generator agent, advice tool, and tests

## Member 4 - Risk Validator
Own these files:
- agents/risk_validator.py
- tools/risk_assessment.py
- tests/test_validator.py

Suggested commit:
- feat(validator): add risk validator agent, assessment tool, and tests

## Shared Integration Commit (any one member)
Shared files:
- orchestration/workflow.py
- state/global_state.py
- utils/logger.py
- config.py
- main.py
- requirements.txt
- README.md

Suggested commit:
- feat(core): add langgraph orchestration, global state, logging, and app entrypoint

## Report Evidence
For each member include:
- Agent developed
- Tool implemented
- Test file authored
- At least one challenge and fix
- Git commit hash and screenshot
