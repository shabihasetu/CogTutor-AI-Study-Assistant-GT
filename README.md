# CogTutor

CogTutor is a proof-of-concept AI study assistant for Georgia Tech CS 6795: Cognitive Science. It delays complete answers and guides learners through retrieval, feedback, self-explanation, reflection, and final explanation.

## Research question

How does an AI study assistant that integrates guided questioning, self-explanation prompts, and delayed answer disclosure influence retrieval practice, metacognitive reflection, and appropriate AI reliance among Georgia Tech graduate students?

## Cognitive science mapping

| System feature | Cognitive principle | Intended outcome |
|---|---|---|
| Guided question | Retrieval practice | Active recall |
| Incremental hint | Scaffolding | Support without replacing effort |
| Self-explanation prompt | Self-explanation | Deeper organization of knowledge |
| Reflection prompt | Metacognition | Monitoring understanding |
| Delayed final answer | Cognitive forcing/productive effort | Reduced passive AI reliance |

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the app:
```bash
streamlit run app.py
```



