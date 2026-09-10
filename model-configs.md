# W&B model configurations

Checked 2026-09-09. The live notebook and `notebook.py` use `MODEL_CONFIGS` as the single source for the 10-model selector. `inference_options(..., task="direct" | "agent")` resolves mode and task overrides. Both inference paths use it; agent traces record the resolved settings.

These are author-recommended starting points, not empirically optimized gridworld settings. The original Gemma greedy off-mode override has been replaced by Google's current recommendation. Prompt wording, world generation, seed, and sandbox execution are unchanged by this configuration update.

## Sampling

Values are temperature / top_p. Unless a difference is listed, the same values apply with reasoning on and off.

| Model | Direct planning | Code agent | Additional settings / source |
| --- | --- | --- | --- |
| Gemma 4 31B | 1.0 / 0.95 | Same | top_k=64 in both modes. [Google guidance](https://huggingface.co/google/gemma-4-31B-it#best-practices) |
| DeepSeek V4 Flash 0731 | 1.0 / 1.0 | 1.0 / 0.95 | [DeepSeek guidance](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731#how-to-run-locally) |
| DeepSeek V4 Pro 0813 | 1.0 / 1.0 | 1.0 / 0.95 | [DeepSeek guidance](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813#how-to-run-locally) |
| Granite 4.2 8B | 1.0 / 0.95 | Same | IBM explicitly recommends these settings across tasks and modes. [IBM guidance](https://huggingface.co/ibm-granite/granite-4.2-8b#generation-parameters) |
| MiniMax M3 | 1.0 / 0.95 | Same | [MiniMax guidance](https://huggingface.co/MiniMaxAI/MiniMax-M3#inference-parameters) |
| Nemotron 3.5 Lightning | 1.0 / 0.95 | Same | Agent template: force_nonempty_content=True. [NVIDIA guidance](https://huggingface.co/nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4#api-client) |
| Nemotron 3 Ultra | 1.0 / 0.95 | Same | Agent template: force_nonempty_content=True. [NVIDIA guidance](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16) |
| Qwen3.8 27B | On: 1.0 / 0.95; off: 0.7 / 0.80 | Same | presence_penalty=0 on, 1.5 off. [Qwen guidance](https://huggingface.co/Qwen/Qwen3.8-27B#best-practices) |
| Qwen3.6 35B A3B | On: 1.0 / 0.95; off: 0.7 / 0.80 | On: 0.6 / 0.95; off: 0.7 / 0.80 | presence_penalty=1.5 except agent on=0. Both Qwens: top_k=20, min_p=0, repetition_penalty=1. [Qwen guidance](https://huggingface.co/Qwen/Qwen3.6-35B-A3B#best-practices) |
| GLM 5.2 | 1.0 / 0.95 | 1.0 / 1.0 | Based on Z.ai's reasoning and SWE evaluation settings, not a universal recommendation; no separate off-mode setting was found. [Z.ai model card](https://huggingface.co/zai-org/GLM-5.2) |

## Reasoning and limits

The boolean switch is translated to `chat_template_kwargs.enable_thinking` for nine models, following [W&B's reasoning documentation](https://docs.wandb.ai/inference/response-settings/reasoning). MiniMax uses `chat_template_kwargs.thinking_mode="enabled"/"disabled"`, matching its [official template](https://huggingface.co/MiniMaxAI/MiniMax-M3/blob/main/chat_template.jinja). Both this explicit mapping and W&B's previous boolean mapping worked in a small on/off test.

Output limits remain the notebook's demo budgets, separate from sampling recommendations. They are smaller than some authors' evaluation budgets. A truncated result should not be counted as a completed failed solution or, by itself, as evidence of repetitive generation. Hosted sampling seeds do not guarantee identical results.

W&B accepted all tested request parameters. Acceptance and observed reasoning output do not establish that every backend honors every optional sampling parameter; top_k/min_p/repetition_penalty were not independently measured.

## Validation and remaining behavior

- Verified all 40 combinations of 10 models, two reasoning modes, and two request paths against a captured request transport. No configuration dictionaries were mutated by request construction.
- All 20 short streamed arithmetic requests completed correctly. Reasoning fields were empty with reasoning off and nonempty with reasoning on.
- Eight small tool-call checks covered MiniMax, both Nemotrons, and Qwen3.6 in both modes. Seven initially returned valid tool arguments. Ultra's reasoning-on response was incomplete at the 384-token test budget; it returned valid arguments with a 2,048-token budget (393 output tokens used). No sandbox code was executed.
- Actual puzzle, reasoning off, seed 3407, cap 2,048: DeepSeek Flash returned a finite JSON list; MiniMax finished with explanation plus an action list. These responses were not scored by Wanderland in this configuration check.
- Lightning still generated a long repeated action list and hit the 2,048-token cap. It remains selectable. The research-backed profile does not establish that this failure is a model defect, nor does it claim to fix it.
- The notebook UI was checked: exactly 10 choices, including restored MiniMax and Lightning, and an “Active model settings” disclosure next to the inference controls.

Deprecated models and models without a supported on/off comparison were not restored. MiniMax and Lightning were the two removed for the repetitive/off-mode failures; Ultra and DeepSeek Flash were already available.

