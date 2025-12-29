# LLM Evaluation

The framework supports "LLM-as-a-Judge" to evaluate responses using a secondary LLM. this allows for nuanced checking of tone, safety, and helpfulness beyond simple keyword matching.

## Usage

To use the LLM evaluator, pass `--evaluator llm` to the runner:

```bash
uv run python -m src.main \
  --config tests/llm_eval_suite.yaml \
  --evaluator llm
```

## Configuration

The `LLMEvaluator` uses a prompt template to instruct the judge. By default, it uses a safety-focused template that checks for harmful content.

### Custom Templates
*To be implemented: Allow loading custom templates from config files.*
