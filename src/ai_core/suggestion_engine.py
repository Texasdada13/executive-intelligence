"""Context-Aware Suggestion Engine for Executive Intelligence"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class SuggestionCategory(Enum):
    URGENT = "urgent"  # Immediate attention needed
    OPPORTUNITY = "opportunity"  # Growth/improvement opportunity
    FOLLOW_UP = "follow_up"  # Continue previous discussion
    GENERAL = "general"  # Standard prompts


@dataclass
class SuggestedPrompt:
    prompt_text: str
    relevance_score: float  # 0-100
    category: SuggestionCategory
    rationale: str  # Why this is suggested (for UI tooltip)
    topic_tags: List[str]  # For tracking discussed topics

    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt': self.prompt_text,
            'relevance': round(self.relevance_score, 1),
            'category': self.category.value,
            'rationale': self.rationale,
            'tags': self.topic_tags
        }


class ExecutiveSuggestionEngine:
    """Generates context-aware prompt suggestions for Executive Intelligence."""

    # Base prompts by mode (fallback when no context signals)
    BASE_PROMPTS = {
        'general': [
            ("What's the overall health of the business?", ["health", "overview"]),
            ("Where should I focus my attention this week?", ["priorities", "focus"]),
            ("What are the top risks to our business right now?", ["risks", "strategy"]),
        ],
        'strategic_planning': [
            ("How are we progressing on strategic goals?", ["goals", "progress"]),
            ("Which goals are at risk and why?", ["goals", "risk"]),
            ("Help me set priorities for next quarter", ["planning", "priorities"]),
        ],
        'financial_overview': [
            ("What's our financial health looking like?", ["financial", "health"]),
            ("How is our cash runway?", ["financial", "runway"]),
            ("Where can we improve profitability?", ["financial", "profitability"]),
        ],
        'operational_review': [
            ("How are operations performing?", ["operations", "performance"]),
            ("Where are the operational bottlenecks?", ["operations", "bottlenecks"]),
            ("What's our customer satisfaction trending?", ["operations", "customers"]),
        ],
        'people_culture': [
            ("How is employee engagement?", ["people", "engagement"]),
            ("What's our turnover looking like?", ["people", "turnover"]),
            ("Where should we invest in talent?", ["people", "talent"]),
        ],
        'csuite_dashboard': [
            ("Give me a C-Suite health dashboard", ["csuite", "dashboard"]),
            ("Which function needs the most attention?", ["csuite", "attention"]),
            ("How are the different departments performing?", ["csuite", "performance"]),
        ],
        'board_preparation': [
            ("Help me prepare for the board meeting", ["board", "preparation"]),
            ("What are the key points for the board?", ["board", "highlights"]),
            ("What questions should I anticipate from the board?", ["board", "questions"]),
        ],
        'risk_management': [
            ("What are our enterprise risks?", ["risk", "enterprise"]),
            ("How should we prioritize risk mitigation?", ["risk", "mitigation"]),
            ("What emerging risks should I know about?", ["risk", "emerging"]),
        ],
    }

    # Context-triggered prompts (signal -> prompt)
    CONTEXT_TRIGGERS = {
        # Strategic goal triggers
        'goals_at_risk': {
            'condition': lambda ctx: ctx.get('goals', {}).get('at_risk', 0) > 0,
            'prompt': "{at_risk} strategic goals are at risk. Should we discuss recovery plans?",
            'category': SuggestionCategory.URGENT,
            'relevance': 95,
            'tags': ['goals', 'risk', 'urgent']
        },
        'goals_behind': {
            'condition': lambda ctx: ctx.get('goals', {}).get('behind', 0) > 0,
            'prompt': "{behind} goals are behind schedule. Let's review resource allocation.",
            'category': SuggestionCategory.URGENT,
            'relevance': 92,
            'tags': ['goals', 'behind', 'resources']
        },
        'low_goal_progress': {
            'condition': lambda ctx: ctx.get('goals', {}).get('overall_progress', 100) < 50,
            'prompt': "Overall goal progress is {overall_progress}%. What's blocking execution?",
            'category': SuggestionCategory.URGENT,
            'relevance': 88,
            'tags': ['goals', 'progress', 'execution']
        },

        # Financial triggers
        'low_runway': {
            'condition': lambda ctx: ctx.get('financial', {}).get('runway_months', 999) < 6,
            'prompt': "Cash runway is {runway_months} months. Let's discuss funding strategy.",
            'category': SuggestionCategory.URGENT,
            'relevance': 98,
            'tags': ['financial', 'runway', 'funding']
        },
        'negative_growth': {
            'condition': lambda ctx: ctx.get('financial', {}).get('revenue_growth', 0) < 0,
            'prompt': "Revenue declined {revenue_growth}%. What's driving the decline?",
            'category': SuggestionCategory.URGENT,
            'relevance': 94,
            'tags': ['financial', 'revenue', 'growth']
        },
        'margin_pressure': {
            'condition': lambda ctx: ctx.get('financial', {}).get('gross_margin', 100) < 40,
            'prompt': "Gross margin is {gross_margin}%. How can we improve unit economics?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 82,
            'tags': ['financial', 'margin', 'profitability']
        },
        'high_burn': {
            'condition': lambda ctx: ctx.get('financial', {}).get('burn_rate', 0) > ctx.get('financial', {}).get('revenue', 1) * 0.5,
            'prompt': "Burn rate is high relative to revenue. Should we review cost structure?",
            'category': SuggestionCategory.URGENT,
            'relevance': 90,
            'tags': ['financial', 'burn', 'costs']
        },

        # Customer triggers
        'low_nps': {
            'condition': lambda ctx: ctx.get('customers', {}).get('nps', 100) < 30,
            'prompt': "NPS is {nps}. Let's discuss customer satisfaction issues.",
            'category': SuggestionCategory.URGENT,
            'relevance': 86,
            'tags': ['customers', 'nps', 'satisfaction']
        },
        'high_churn': {
            'condition': lambda ctx: ctx.get('customers', {}).get('churn_rate', 0) > 8,
            'prompt': "Customer churn is {churn_rate}%. What retention strategies should we consider?",
            'category': SuggestionCategory.URGENT,
            'relevance': 91,
            'tags': ['customers', 'churn', 'retention']
        },
        'customer_growth_stall': {
            'condition': lambda ctx: ctx.get('customers', {}).get('growth', 0) < 5,
            'prompt': "Customer growth is only {growth}%. How can we accelerate acquisition?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 78,
            'tags': ['customers', 'growth', 'acquisition']
        },

        # People triggers
        'low_engagement': {
            'condition': lambda ctx: ctx.get('people', {}).get('engagement', 100) < 60,
            'prompt': "Employee engagement is {engagement}%. This is a retention risk.",
            'category': SuggestionCategory.URGENT,
            'relevance': 87,
            'tags': ['people', 'engagement', 'retention']
        },
        'high_turnover': {
            'condition': lambda ctx: ctx.get('people', {}).get('turnover', 0) > 15,
            'prompt': "Voluntary turnover is {turnover}%. Let's discuss people strategy.",
            'category': SuggestionCategory.URGENT,
            'relevance': 85,
            'tags': ['people', 'turnover', 'talent']
        },

        # C-Suite health triggers
        'csuite_function_struggling': {
            'condition': lambda ctx: any(f.get('health_score', 100) < 50 for f in ctx.get('csuite', {}).values()),
            'prompt': "A C-Suite function is struggling (below 50%). Let's review.",
            'category': SuggestionCategory.URGENT,
            'relevance': 93,
            'tags': ['csuite', 'health', 'attention']
        },
        'overall_health_declining': {
            'condition': lambda ctx: ctx.get('overall_health', 100) < 60,
            'prompt': "Overall business health is {overall_health}. Where should we focus?",
            'category': SuggestionCategory.URGENT,
            'relevance': 96,
            'tags': ['health', 'business', 'priorities']
        },

        # Board/governance triggers
        'board_meeting_soon': {
            'condition': lambda ctx: ctx.get('board', {}).get('days_until_meeting', 999) < 14,
            'prompt': "Board meeting in {days_until_meeting} days. Ready to prepare materials?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 80,
            'tags': ['board', 'meeting', 'preparation']
        },

        # Risk triggers
        'critical_risk': {
            'condition': lambda ctx: any(r.get('severity') == 'critical' for r in ctx.get('risks', [])),
            'prompt': "There's a critical enterprise risk. Should we discuss mitigation?",
            'category': SuggestionCategory.URGENT,
            'relevance': 97,
            'tags': ['risk', 'critical', 'mitigation']
        },

        # Positive opportunity triggers
        'strong_momentum': {
            'condition': lambda ctx: ctx.get('financial', {}).get('revenue_growth', 0) > 30 and ctx.get('overall_health', 0) > 75,
            'prompt': "Strong momentum with {revenue_growth}% growth. Ready to scale?",
            'category': SuggestionCategory.OPPORTUNITY,
            'relevance': 75,
            'tags': ['growth', 'scaling', 'opportunity']
        },
    }

    def __init__(self):
        pass

    def get_suggestions(
        self,
        mode: str,
        context: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        discussed_topics: List[str] = None,
        dismissed_prompts: List[str] = None,
        max_suggestions: int = 4
    ) -> List[SuggestedPrompt]:
        """
        Generate context-aware suggestions.

        Args:
            mode: Current conversation mode
            context: Business context (goals, financial, customers, people, etc.)
            conversation_history: Previous messages
            discussed_topics: Topics already covered
            dismissed_prompts: Prompts user has dismissed
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of SuggestedPrompt objects sorted by relevance
        """
        discussed_topics = discussed_topics or []
        dismissed_prompts = dismissed_prompts or []

        suggestions = []

        # 1. Check context-triggered prompts first (highest priority)
        for trigger_name, trigger in self.CONTEXT_TRIGGERS.items():
            try:
                if trigger['condition'](context):
                    prompt_text = self._format_prompt(trigger['prompt'], context)

                    # Skip if already discussed or dismissed
                    if self._is_topic_discussed(trigger['tags'], discussed_topics):
                        continue
                    if prompt_text in dismissed_prompts:
                        continue

                    suggestions.append(SuggestedPrompt(
                        prompt_text=prompt_text,
                        relevance_score=trigger['relevance'],
                        category=trigger['category'],
                        rationale=f"Based on your current {trigger_name.replace('_', ' ')} data",
                        topic_tags=trigger['tags']
                    ))
            except Exception:
                continue  # Skip malformed triggers

        # 2. Add base prompts for the mode (fill remaining slots)
        base_prompts = self.BASE_PROMPTS.get(mode, self.BASE_PROMPTS['general'])
        for prompt_text, tags in base_prompts:
            if self._is_topic_discussed(tags, discussed_topics):
                continue
            if prompt_text in dismissed_prompts:
                continue

            # Lower relevance for base prompts
            relevance = 50 - (len(suggestions) * 5)  # Decreasing relevance

            suggestions.append(SuggestedPrompt(
                prompt_text=prompt_text,
                relevance_score=max(relevance, 20),
                category=SuggestionCategory.GENERAL,
                rationale=f"Common question for {mode.replace('_', ' ')}",
                topic_tags=tags
            ))

        # 3. Add follow-up suggestions based on conversation history
        if conversation_history:
            follow_ups = self._generate_follow_ups(conversation_history, discussed_topics)
            suggestions.extend(follow_ups)

        # Sort by relevance and return top N
        suggestions.sort(key=lambda x: x.relevance_score, reverse=True)
        return suggestions[:max_suggestions]

    def _format_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """Format prompt template with context values."""
        goals = context.get('goals', {})
        financial = context.get('financial', {})
        customers = context.get('customers', {})
        people = context.get('people', {})
        board = context.get('board', {})

        # Flatten context for formatting
        format_dict = {
            **goals,
            **financial,
            **customers,
            **people,
            **board,
            'overall_health': context.get('overall_health', 0),
        }

        try:
            return template.format(**format_dict)
        except KeyError:
            return template  # Return unformatted if values missing

    def _is_topic_discussed(self, tags: List[str], discussed: List[str]) -> bool:
        """Check if topic tags overlap with discussed topics."""
        return any(tag in discussed for tag in tags)

    def _generate_follow_ups(
        self,
        history: List[Dict[str, Any]],
        discussed: List[str]
    ) -> List[SuggestedPrompt]:
        """Generate follow-up suggestions based on conversation history."""
        follow_ups = []

        if not history:
            return follow_ups

        # Get last assistant message
        last_messages = [m for m in history[-4:] if m.get('role') == 'assistant']
        if not last_messages:
            return follow_ups

        last_response = last_messages[-1].get('content', '').lower()

        # Check for actionable topics mentioned
        follow_up_triggers = [
            {
                'keywords': ['recommend', 'suggest', 'should consider'],
                'prompt': "Can you elaborate on those strategic recommendations?",
                'tags': ['follow-up', 'recommendations']
            },
            {
                'keywords': ['goal', 'goals', 'objective'],
                'prompt': "What specific actions will get these goals back on track?",
                'tags': ['follow-up', 'goals']
            },
            {
                'keywords': ['revenue', 'financial', 'profit'],
                'prompt': "What's the financial impact of these changes?",
                'tags': ['follow-up', 'financial']
            },
            {
                'keywords': ['team', 'employee', 'people'],
                'prompt': "How do we execute on the people strategy?",
                'tags': ['follow-up', 'people']
            },
            {
                'keywords': ['risk', 'challenge', 'concern'],
                'prompt': "What's the mitigation plan for these risks?",
                'tags': ['follow-up', 'risks']
            },
            {
                'keywords': ['board', 'investor', 'stakeholder'],
                'prompt': "How should we position this for the board?",
                'tags': ['follow-up', 'board']
            },
        ]

        for trigger in follow_up_triggers:
            if any(kw in last_response for kw in trigger['keywords']):
                if not self._is_topic_discussed(trigger['tags'], discussed):
                    follow_ups.append(SuggestedPrompt(
                        prompt_text=trigger['prompt'],
                        relevance_score=70,
                        category=SuggestionCategory.FOLLOW_UP,
                        rationale="Follow up on our previous discussion",
                        topic_tags=trigger['tags']
                    ))

        return follow_ups[:2]  # Max 2 follow-ups

    def extract_topics(self, message: str) -> List[str]:
        """Extract topic tags from a message."""
        topics = []

        topic_keywords = {
            'goals': ['goal', 'objective', 'okr', 'target', 'milestone'],
            'financial': ['revenue', 'profit', 'margin', 'cash', 'runway', 'burn'],
            'customers': ['customer', 'nps', 'churn', 'retention', 'satisfaction'],
            'people': ['employee', 'team', 'engagement', 'turnover', 'talent'],
            'strategy': ['strategy', 'strategic', 'planning', 'vision', 'mission'],
            'board': ['board', 'investor', 'stakeholder', 'governance'],
            'risk': ['risk', 'challenge', 'threat', 'mitigation'],
            'growth': ['growth', 'scale', 'expand', 'acquisition'],
            'operations': ['operation', 'efficiency', 'process', 'productivity'],
        }

        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in message_lower for kw in keywords):
                topics.append(topic)

        return topics


# Factory function
def create_executive_suggestion_engine() -> ExecutiveSuggestionEngine:
    return ExecutiveSuggestionEngine()
