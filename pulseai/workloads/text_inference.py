"""
PulseAI Text Inference Workload
--------------------------------

Reference AI workload used for hardware profiling.

Implements transformer-based text generation inference
with deterministic execution behavior.

Design Goals
------------
- Backend neutral (CPU/GPU)
- Stable benchmarking
- Token-count measurable work
- Minimal randomness
"""

from typing import List
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
)


class TextInferenceWorkload:
    """
    Transformer inference workload.

    Returns number of generated tokens as
    work-unit measurement.
    """

    MODEL_NAME = "distilgpt2"

    def __init__(
        self,
        prompts: List[str] | None = None,
        max_new_tokens: int = 50,
        device: str | None = None,
    ):

        self.prompts = prompts or [
            "Artificial intelligence will",
            "Future processors enable",
            "Efficient computing requires",
        ]

        self.max_new_tokens = max_new_tokens

        self.device = (
            device
            if device
            else ("cuda" if torch.cuda.is_available() else "cpu")
        )

        self._load_model()

    # ==========================================================
    # Model Initialization
    # ==========================================================

    def _load_model(self):
        """
        Load tokenizer + model once.
        """

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_NAME
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_NAME
        )

        self.model.to(self.device)
        self.model.eval()

        # Disable gradients for inference benchmarking
        torch.set_grad_enabled(False)

    # ==========================================================
    # Token Counting
    # ==========================================================

    def _count_generated_tokens(
        self,
        outputs,
        inputs,
    ) -> int:
        """
        Compute number of generated tokens.
        """

        total_tokens = 0

        for out, inp in zip(outputs, inputs["input_ids"]):
            generated = out.shape[-1] - inp.shape[-1]
            total_tokens += max(generated, 0)

        return total_tokens

    # ==========================================================
    # Execution
    # ==========================================================

    def __call__(self) -> int:
        """
        Execute inference workload.

        Returns
        -------
        int
            Total generated tokens.
        """

        inputs = self.tokenizer(
            self.prompts,
            return_tensors="pt",
            padding=True,
        ).to(self.device)

        with torch.inference_mode():

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,        # deterministic
                num_beams=1,
            )

        # GPU correctness
        if self.device == "cuda":
            torch.cuda.synchronize()

        tokens_generated = self._count_generated_tokens(
            outputs,
            inputs
        )

        return int(tokens_generated)

    # ==========================================================
    # Metadata
    # ==========================================================

    def info(self):
        """
        Workload metadata.
        """

        return {
            "type": "text_generation",
            "model": self.MODEL_NAME,
            "device": self.device,
            "max_new_tokens": self.max_new_tokens,
            "prompt_count": len(self.prompts),
        }