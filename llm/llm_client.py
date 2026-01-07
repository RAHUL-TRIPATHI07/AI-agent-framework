import time
from typing import Generator, List, Any
from abc import ABC, abstractmethod

try:
    from optimum.intel import OVModelForCausalLM
    from transformers import AutoTokenizer, pipeline
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

from llm.llm_client_base import LLMClient, LLMRequest, LLMResponse, LLMProvider

class OpenVINOClient(LLMClient):
    """
    Intel-optimized LLM Client using OpenVINO.
    Fulfills the 'Intel Tech' requirement for local ML optimization.
    """
    def __init__(self, model_id: str, device: str = "CPU"):
        self.model_id = model_id
        self.device = device.upper() 
        
        if not OPENVINO_AVAILABLE:
            raise ImportError("Please install optimum[openvino] to use OpenVINOClient.")

        print(f"Loading {model_id} onto {self.device} via OpenVINO...")
        

        self.model = OVModelForCausalLM.from_pretrained(
            model_id, 
            export=True, 
            device=self.device,
            compile=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Execute inference optimized for Intel hardware."""
        start_time = time.time()
        
       
        prompt = self._format_messages(request.messages)
        
        
        output = self.pipeline(
            prompt, 
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True
        )
        
        generated_text = output[0]['generated_text'][len(prompt):]
        latency = (time.time() - start_time) * 1000
        
        return LLMResponse(
            content=generated_text,
            provider="intel_openvino",
            model=self.model_id,
            tokens_used=len(generated_text.split()), 
            finish_reason="stop",
            latency_ms=latency,
            metadata={"device": self.device, "optimized": True}
        )

    def stream_complete(self, request: LLMRequest) -> Generator[str, None, None]:
        """Streaming implementation for local OpenVINO inference."""
        
        response = self.complete(request)
        for word in response.content.split():
            yield word + " "
            time.sleep(0.01)

    def _format_messages(self, messages: List[Any]) -> str:
        """Converts ChatML or Message objects to a raw prompt string."""
        formatted = ""
        for msg in messages:
            formatted += f"\n<|{msg.role}|>\n{msg.content}\n"
        formatted += "\n<|assistant|>\n"
        return formatted

    def get_provider(self) -> LLMProvider:
        return LLMProvider.LOCAL
