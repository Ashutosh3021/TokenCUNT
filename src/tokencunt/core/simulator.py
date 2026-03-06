"""Cost simulator module for estimating LLM API costs."""

from typing import Optional
from enum import Enum
from pydantic import BaseModel


class ModelTier(Enum):
    """Model pricing tiers."""

    PREMIUM = "premium"  # GPT-4, Claude-3, etc.
    STANDARD = "standard"  # GPT-3.5, Claude-instant
    BUDGET = "budget"  # MiniMax, Llama, etc.


# Model pricing constants (USD per 1,000 tokens)
MODEL_PRICING = {
    # Premium models
    "gpt-4": {"input": 0.03, "output": 0.06, "tier": ModelTier.PREMIUM},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03, "tier": ModelTier.PREMIUM},
    "gpt-4o": {"input": 0.005, "output": 0.015, "tier": ModelTier.PREMIUM},
    "gpt-4o-mini": {"input": 0.0015, "output": 0.006, "tier": ModelTier.PREMIUM},
    "claude-3-opus": {"input": 0.015, "output": 0.075, "tier": ModelTier.PREMIUM},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015, "tier": ModelTier.PREMIUM},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015, "tier": ModelTier.PREMIUM},
    # Standard models
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002, "tier": ModelTier.STANDARD},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004, "tier": ModelTier.STANDARD},
    "claude-instant": {"input": 0.0008, "output": 0.00124, "tier": ModelTier.STANDARD},
    # Budget models
    "minimax": {"input": 0.001, "output": 0.001, "tier": ModelTier.BUDGET},
    "minimax-text-01": {"input": 0.001, "output": 0.001, "tier": ModelTier.BUDGET},
    "llama-3": {"input": 0.0002, "output": 0.0002, "tier": ModelTier.BUDGET},
    "llama-3-70b": {"input": 0.0008, "output": 0.0008, "tier": ModelTier.BUDGET},
    "mistral": {"input": 0.00024, "output": 0.00024, "tier": ModelTier.BUDGET},
    "gemini-flash": {"input": 0.00035, "output": 0.00035, "tier": ModelTier.BUDGET},
}


# Pre-defined scenarios
SCENARIOS = {
    "dev": {
        "name": "Developer",
        "description": "Light daily usage for individual developers",
        "requests_per_day": 50,
        "avg_tokens_per_request": 500,
    },
    "startup": {
        "name": "Startup",
        "description": "Moderate usage for small teams",
        "requests_per_day": 500,
        "avg_tokens_per_request": 1000,
    },
    "enterprise": {
        "name": "Enterprise",
        "description": "Heavy usage for large organizations",
        "requests_per_day": 5000,
        "avg_tokens_per_request": 2000,
    },
    "custom": {
        "name": "Custom",
        "description": "User-defined usage pattern",
        "requests_per_day": 0,  # Must be provided
        "avg_tokens_per_request": 0,  # Must be provided
    },
}


class CostSimulator:
    """Simulates API costs based on traffic patterns."""

    # Default model if none specified
    DEFAULT_MODEL = "gpt-4"

    # Days in month for calculation
    DAYS_PER_MONTH = 30

    def __init__(self, model: str = None):
        """
        Initialize cost simulator.

        Args:
            model: Model name to use for calculations (default: gpt-4)
        """
        self.model = model or self.DEFAULT_MODEL
        self._last_calculation: Optional[dict] = None

    def get_model_pricing(self, model: str = None) -> dict:
        """
        Get pricing for a model.

        Args:
            model: Model name (uses self.model if not provided)

        Returns:
            Pricing dictionary with input/output costs

        Raises:
            ValueError: If model is not recognized
        """
        model = model or self.model
        if model not in MODEL_PRICING:
            raise ValueError(
                f"Unknown model: {model}. "
                f"Available models: {', '.join(MODEL_PRICING.keys())}"
            )
        return MODEL_PRICING[model]

    def simulate_traffic(
        self,
        requests_per_day: int,
        avg_tokens_per_request: int,
        model: str = None,
        input_output_ratio: float = 0.7,
    ) -> dict:
        """
        Calculate monthly cost based on traffic patterns.

        Args:
            requests_per_day: Number of API requests per day
            avg_tokens_per_request: Average tokens per request (combined input+output)
            model: Model to use (uses instance default if not provided)
            input_output_ratio: Ratio of input tokens (default: 70% input, 30% output)

        Returns:
            Dictionary with cost breakdown:
            {
                "model": str,
                "requests_per_day": int,
                "avg_tokens_per_request": int,
                "monthly_requests": int,
                "monthly_input_tokens": int,
                "monthly_output_tokens": int,
                "monthly_total_tokens": int,
                "cost_per_1k_input": float,
                "cost_per_1k_output": float,
                "monthly_input_cost": float,
                "monthly_output_cost": float,
                "monthly_total_cost": float,
            }
        """
        model = model or self.model

        # Get pricing
        pricing = self.get_model_pricing(model)

        # Calculate monthly totals
        monthly_requests = requests_per_day * self.DAYS_PER_MONTH
        total_tokens = avg_tokens_per_request * monthly_requests

        # Split input/output based on ratio
        input_tokens = int(total_tokens * input_output_ratio)
        output_tokens = total_tokens - input_tokens

        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Store for later retrieval
        self._last_calculation = {
            "model": model,
            "scenario": "Custom Traffic",
            "requests_per_day": requests_per_day,
            "avg_tokens_per_request": avg_tokens_per_request,
            "monthly_requests": monthly_requests,
            "monthly_input_tokens": input_tokens,
            "monthly_output_tokens": output_tokens,
            "monthly_total_tokens": total_tokens,
            "cost_per_1k_input": pricing["input"],
            "cost_per_1k_output": pricing["output"],
            "monthly_input_cost": round(input_cost, 4),
            "monthly_output_cost": round(output_cost, 4),
            "monthly_total_cost": round(total_cost, 2),
            "tier": pricing["tier"].value,
        }

        return self._last_calculation

    def simulate_scenario(
        self,
        scenario_name: str,
        params: dict = None,
        model: str = None,
    ) -> dict:
        """
        Simulate a pre-defined scenario.

        Args:
            scenario_name: Name of scenario (dev, startup, enterprise, custom)
            params: Override parameters for custom scenarios
            model: Model to use

        Returns:
            Cost calculation dictionary from simulate_traffic

        Raises:
            ValueError: If scenario not found or custom without params
        """
        if scenario_name not in SCENARIOS:
            raise ValueError(
                f"Unknown scenario: {scenario_name}. "
                f"Available: {', '.join(SCENARIOS.keys())}"
            )

        scenario = SCENARIOS[scenario_name]

        # Use provided params or scenario defaults
        if scenario_name == "custom":
            if not params:
                raise ValueError(
                    "Custom scenario requires params dict with 'requests_per_day' and 'avg_tokens_per_request'"
                )
            requests_per_day = params.get("requests_per_day", 0)
            avg_tokens_per_request = params.get("avg_tokens_per_request", 0)
            scenario_name = "Custom Traffic"
        else:
            requests_per_day = scenario["requests_per_day"]
            avg_tokens_per_request = scenario["avg_tokens_per_request"]
            scenario_name = scenario["name"]

        # Run simulation
        result = self.simulate_traffic(
            requests_per_day=requests_per_day,
            avg_tokens_per_request=avg_tokens_per_request,
            model=model,
        )

        # Override scenario name in result
        result["scenario"] = scenario_name

        return result

    def simulate_user_scenario(
        self,
        users: int,
        messages_per_user_per_day: int,
        tokens_per_message: int,
        model: str = None,
    ) -> dict:
        """
        Calculate cost based on user activity scenarios.

        Args:
            users: Number of active users
            messages_per_user_per_day: Average messages each user sends per day
            tokens_per_message: Average tokens (input+output) per message
            model: Model to use

        Returns:
            Cost calculation dictionary from simulate_traffic
        """
        # Calculate total daily requests
        requests_per_day = users * messages_per_user_per_day

        # Run traffic simulation
        result = self.simulate_traffic(
            requests_per_day=requests_per_day,
            avg_tokens_per_request=tokens_per_message,
            model=model,
        )

        # Override scenario name
        result["scenario"] = f"User Scenario ({users} users)"
        result["users"] = users
        result["messages_per_user_per_day"] = messages_per_user_per_day

        return result

    def get_cost_breakdown(self) -> dict:
        """
        Get cost breakdown for all models/tiers.

        Returns:
            Dictionary with costs by tier and individual models
        """
        breakdown = {}

        for tier in ModelTier:
            tier_models = {
                name: pricing
                for name, pricing in MODEL_PRICING.items()
                if pricing["tier"] == tier
            }

            # Calculate cost for 1000 requests with 1000 tokens each
            sample_cost = self.simulate_traffic(
                requests_per_day=1000,
                avg_tokens_per_request=1000,
                model=list(tier_models.keys())[0] if tier_models else None,
            )

            breakdown[tier.value] = {
                "models": list(tier_models.keys()),
                "sample_monthly_cost": sample_cost["monthly_total_cost"],
            }

        return breakdown

    def list_models(self) -> list[str]:
        """Get list of all available models."""
        return list(MODEL_PRICING.keys())

    def list_scenarios(self) -> dict:
        """Get list of all available scenarios."""
        return SCENARIOS.copy()
