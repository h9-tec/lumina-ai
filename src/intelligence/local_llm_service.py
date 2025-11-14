"""
Local LLM Service - Supports both Ollama and LLaMA.cpp with Azure GPT-4 fallback
"""
import os
from typing import Optional
from pathlib import Path


class LocalLLMService:
    """Local LLM service with multiple provider support"""

    def __init__(self, provider: str = "ollama", model_name: Optional[str] = None):
        """
        Initialize local LLM service

        Args:
            provider: "ollama", "llamacpp", or "azure" (fallback)
            model_name: Model to use (e.g., "llama3", "mistral", path to GGUF file)
        """
        self.provider = provider.lower()
        self.model_name = model_name or os.getenv('LOCAL_LLM_MODEL', 'llama3')
        self.llm = None

        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider"""

        if self.provider == "ollama":
            self._initialize_ollama()
        elif self.provider == "llamacpp":
            self._initialize_llamacpp()
        elif self.provider == "azure":
            self._initialize_azure()
        else:
            # Try Ollama first, then fallback
            try:
                self._initialize_ollama()
                self.provider = "ollama"
            except Exception as e:
                print(f"Ollama failed: {e}, falling back to Azure GPT-4")
                self._initialize_azure()
                self.provider = "azure"

    def _initialize_ollama(self):
        """Initialize Ollama LLM"""
        try:
            from langchain_community.llms import Ollama

            self.llm = Ollama(
                model=self.model_name,
                temperature=0.7,
            )
            print(f"✅ Initialized Ollama with model: {self.model_name}")

        except Exception as e:
            raise Exception(f"Failed to initialize Ollama: {e}")

    def _initialize_llamacpp(self):
        """Initialize LLaMA.cpp LLM"""
        try:
            from langchain_community.llms import LlamaCpp

            # Model path from env or use model_name as path
            model_path = os.getenv('LLAMACPP_MODEL_PATH', self.model_name)

            if not Path(model_path).exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            self.llm = LlamaCpp(
                model_path=model_path,
                temperature=0.7,
                max_tokens=2048,
                n_ctx=4096,
                verbose=False,
            )
            print(f"✅ Initialized LLaMA.cpp with model: {model_path}")

        except Exception as e:
            raise Exception(f"Failed to initialize LLaMA.cpp: {e}")

    def _initialize_azure(self):
        """Initialize Azure GPT-4 as fallback"""
        try:
            from langchain_openai import AzureChatOpenAI

            self.llm = AzureChatOpenAI(
                model="gpt-4-32k",
                api_version="2024-08-01-preview",
                api_key=os.getenv('OPENAI_API_KEY', "161a11270d03448fb67e707c12005909"),
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT',
                                       "https://prodnancyazure3277074411.openai.azure.com/"),
                temperature=0.7,
            )
            print(f"✅ Initialized Azure GPT-4 (fallback)")

        except Exception as e:
            raise Exception(f"Failed to initialize Azure GPT-4: {e}")

    def generate(self, prompt: str) -> str:
        """
        Generate text from prompt

        Args:
            prompt: Input prompt

        Returns:
            Generated text
        """
        if self.llm is None:
            raise Exception("LLM not initialized")

        try:
            if self.provider == "azure":
                # Azure uses chat format
                from langchain.schema import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            else:
                # Ollama and LLaMA.cpp use invoke directly
                response = self.llm.invoke(prompt)
                return response

        except Exception as e:
            print(f"❌ Error generating with {self.provider}: {e}")

            # Try fallback to Azure if not already using it
            if self.provider != "azure":
                print("Attempting fallback to Azure GPT-4...")
                try:
                    self._initialize_azure()
                    from langchain.schema import HumanMessage
                    response = self.llm.invoke([HumanMessage(content=prompt)])
                    return response.content
                except Exception as fallback_error:
                    raise Exception(f"Fallback also failed: {fallback_error}")
            else:
                raise e


# Test function
if __name__ == "__main__":
    print("Testing Local LLM Service...")

    # Test with Ollama
    try:
        llm_service = LocalLLMService(provider="ollama", model_name="llama3")
        response = llm_service.generate("Say hello in one sentence.")
        print(f"\nOllama Response: {response}")
    except Exception as e:
        print(f"Ollama test failed: {e}")

    print("\nTest complete!")
