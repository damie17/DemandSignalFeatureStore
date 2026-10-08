# Demand Signal Feature Store

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/damie17/DemandSignalFeatureStore.git
cd DemandSignalFeatureStore

# 2. Install Jupyter kernel
pip install ipykernel

# 3. Create .env file with your API key
cp .env.example .env
# Edit .env and replace "your-openrouter-api-key" with your actual key

# 4. Open in VS Code
code .
```

Open `notebooks/main.ipynb` and click **Run All**. The first cell installs all dependencies automatically.

## Notes

- LLM extraction is enabled by default (`USE_LLM = True` in Section 2 of the notebook)
- Set `USE_LLM = False` to run without an API key (uses ground-truth fallback)
- All data is synthetic and generated at runtime
