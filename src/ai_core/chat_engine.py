"""Executive Intelligence - AI Chat Engine with CEO Conversation Modes"""
from enum import Enum
from typing import Dict, List, Optional, Generator, Any
from .claude_client import ClaudeClient
from .suggestion_engine import ExecutiveSuggestionEngine, SuggestedPrompt


class ConversationMode(Enum):
    GENERAL = "general"
    BUSINESS_HEALTH = "business_health"
    STRATEGIC_PLANNING = "strategic_planning"
    BOARD_PREP = "board_prep"
    DECISION_SUPPORT = "decision_support"
    CSUITE_REVIEW = "csuite_review"
    GROWTH_STRATEGY = "growth_strategy"
    RISK_OVERVIEW = "risk_overview"


MODE_DESCRIPTIONS = {
    ConversationMode.GENERAL: "General executive questions and guidance",
    ConversationMode.BUSINESS_HEALTH: "Overall business health and performance",
    ConversationMode.STRATEGIC_PLANNING: "Strategic planning and goal setting",
    ConversationMode.BOARD_PREP: "Board meeting preparation and reporting",
    ConversationMode.DECISION_SUPPORT: "Executive decision support",
    ConversationMode.CSUITE_REVIEW: "C-Suite performance review",
    ConversationMode.GROWTH_STRATEGY: "Growth strategy and planning",
    ConversationMode.RISK_OVERVIEW: "Enterprise risk overview",
}


SUGGESTED_PROMPTS = {
    ConversationMode.GENERAL: [
        "What should my top priorities be as CEO?",
        "How is the business performing overall?",
        "What are the biggest risks to our business?",
    ],
    ConversationMode.BUSINESS_HEALTH: [
        "Give me an overall business health assessment",
        "Which areas need the most attention?",
        "How do we compare to industry benchmarks?",
    ],
    ConversationMode.STRATEGIC_PLANNING: [
        "Help me develop our annual strategic plan",
        "Which strategic goals should we prioritize?",
        "Are we on track with our current strategy?",
    ],
    ConversationMode.BOARD_PREP: [
        "Help me prepare for the board meeting",
        "What should I highlight to the board?",
        "How do I communicate our challenges?",
    ],
    ConversationMode.DECISION_SUPPORT: [
        "Should we pursue this acquisition?",
        "How should we allocate next quarter's budget?",
        "What factors should I consider for this decision?",
    ],
    ConversationMode.CSUITE_REVIEW: [
        "How is each C-suite function performing?",
        "Where are the gaps in our leadership team?",
        "What cross-functional issues need attention?",
    ],
    ConversationMode.GROWTH_STRATEGY: [
        "What are our best growth opportunities?",
        "Should we expand into new markets?",
        "How do we accelerate growth sustainably?",
    ],
    ConversationMode.RISK_OVERVIEW: [
        "What are our top enterprise risks?",
        "How prepared are we for a downturn?",
        "What risks should the board be aware of?",
    ],
}


SYSTEM_PROMPTS = {
    ConversationMode.GENERAL: """You are a Fractional CEO - an experienced executive advisor providing strategic guidance to business leaders. You help with all aspects of running a successful organization.

Your expertise includes:
- Business strategy and vision
- Organizational leadership
- Board and investor relations
- Strategic decision making
- Cross-functional coordination
- Growth and scaling

Provide executive-level guidance that is strategic, actionable, and appropriate for the organization's stage and resources.""",

    ConversationMode.BUSINESS_HEALTH: """You are a Fractional CEO specializing in business health assessment. You help leaders understand how their business is performing across all dimensions.

For business health assessment, you focus on:
- Financial performance and trajectory
- Operational efficiency and quality
- Customer success and market position
- Team health and organizational culture
- Technology and innovation
- Risk and compliance posture

Provide balanced, data-informed assessments with clear priorities.""",

    ConversationMode.STRATEGIC_PLANNING: """You are a Fractional CEO specializing in strategic planning. You help organizations set direction and achieve their goals.

For strategic planning, you focus on:
- Vision and mission alignment
- OKR/goal framework development
- Resource allocation
- Market positioning
- Competitive strategy
- Execution planning

Help create ambitious but achievable strategic plans.""",

    ConversationMode.BOARD_PREP: """You are a Fractional CEO specializing in board relations. You help leaders communicate effectively with their boards.

For board preparation, you focus on:
- Board deck content and structure
- Key metrics presentation
- Narrative development
- Handling difficult questions
- Strategic asks from the board
- Building board confidence

Help prepare for productive board meetings.""",

    ConversationMode.DECISION_SUPPORT: """You are a Fractional CEO specializing in executive decision making. You help leaders make better decisions.

For decision support, you focus on:
- Decision framing and criteria
- Option analysis and trade-offs
- Risk assessment
- Stakeholder considerations
- Implementation implications
- Reversibility and timing

Provide structured decision support without making the decision for them.""",

    ConversationMode.CSUITE_REVIEW: """You are a Fractional CEO specializing in C-suite coordination. You help leaders assess and coordinate their executive teams.

For C-suite review, you focus on:
- Functional performance assessment
- Cross-functional coordination
- Leadership gaps and development
- Team dynamics and alignment
- Communication effectiveness

Provide honest assessments and actionable improvements.""",

    ConversationMode.GROWTH_STRATEGY: """You are a Fractional CEO specializing in growth strategy. You help organizations accelerate sustainable growth.

For growth strategy, you focus on:
- Growth opportunity identification
- Market expansion strategy
- Product/service expansion
- M&A and partnerships
- Scaling challenges
- Unit economics and efficiency

Balance growth ambition with operational sustainability.""",

    ConversationMode.RISK_OVERVIEW: """You are a Fractional CEO specializing in enterprise risk management. You help leaders understand and manage key risks.

For risk overview, you focus on:
- Strategic risk identification
- Operational risk assessment
- Financial risk management
- Market and competitive risks
- People and culture risks
- Technology and security risks

Provide clear risk visibility without creating panic.""",
}


class ChatEngine:
    def __init__(self, claude_client: ClaudeClient = None):
        self.client = claude_client or ClaudeClient()
        self.suggestion_engine = ExecutiveSuggestionEngine()

    def get_modes(self) -> Dict[str, str]:
        return {mode.value: desc for mode, desc in MODE_DESCRIPTIONS.items()}

    def get_suggested_prompts(self, mode: ConversationMode) -> List[str]:
        return SUGGESTED_PROMPTS.get(mode, SUGGESTED_PROMPTS[ConversationMode.GENERAL])

    def get_dynamic_suggestions(
        self,
        mode: str,
        context: Dict[str, Any] = None,
        conversation_history: List[Dict[str, Any]] = None,
        discussed_topics: List[str] = None,
        dismissed_prompts: List[str] = None,
        max_suggestions: int = 4
    ) -> List[Dict[str, Any]]:
        """Get context-aware dynamic suggestions."""
        suggestions = self.suggestion_engine.get_suggestions(
            mode=mode,
            context=context or {},
            conversation_history=conversation_history or [],
            discussed_topics=discussed_topics,
            dismissed_prompts=dismissed_prompts,
            max_suggestions=max_suggestions
        )
        return [s.to_dict() for s in suggestions]

    def extract_topics(self, message: str) -> List[str]:
        """Extract topic tags from a message."""
        return self.suggestion_engine.extract_topics(message)

    def chat(self, message: str, mode: ConversationMode = ConversationMode.GENERAL,
             history: List[Dict[str, str]] = None, context: Dict[str, Any] = None) -> str:
        system_prompt = self._build_system_prompt(mode, context)
        messages = self._build_messages(message, history)
        return self.client.chat(messages, system=system_prompt)

    def chat_stream(self, message: str, mode: ConversationMode = ConversationMode.GENERAL,
                    history: List[Dict[str, str]] = None,
                    context: Dict[str, Any] = None) -> Generator[str, None, None]:
        system_prompt = self._build_system_prompt(mode, context)
        messages = self._build_messages(message, history)
        return self.client.chat_stream(messages, system=system_prompt)

    def _build_system_prompt(self, mode: ConversationMode, context: Dict[str, Any] = None) -> str:
        base_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS[ConversationMode.GENERAL])
        if context:
            context_str = self._format_context(context)
            return f"{base_prompt}\n\n## Current Context\n{context_str}"
        return base_prompt

    def _build_messages(self, message: str, history: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
        messages = []
        if history:
            for msg in history[-10:]:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": message})
        return messages

    def _format_context(self, context: Dict[str, Any]) -> str:
        parts = []
        if "organization" in context:
            org = context["organization"]
            parts.append(f"**Organization**: {org.get('name', 'Unknown')}")
            if org.get('industry'):
                parts.append(f"**Industry**: {org['industry']}")
            if org.get('stage'):
                parts.append(f"**Stage**: {org['stage']}")

        if "health" in context:
            h = context["health"]
            parts.append(f"\n**Business Health**: {h.get('overall_score', 'N/A')} ({h.get('grade', 'N/A')})")

        if "csuite" in context:
            cs = context["csuite"]
            parts.append(f"\n**C-Suite Summary**:")
            for role, data in cs.items():
                parts.append(f"- {role}: {data.get('health_score', 'N/A')}")

        if "goals" in context:
            g = context["goals"]
            parts.append(f"\n**Strategic Goals**: {g.get('total', 0)} total")
            parts.append(f"- On Track: {g.get('on_track', 0)}, At Risk: {g.get('at_risk', 0)}")

        return "\n".join(parts) if parts else "No additional context available."
