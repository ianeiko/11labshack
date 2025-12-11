from pydantic import BaseModel, Field, UUID4
from typing import Optional, Literal
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    bio: str
    voice_id: str
    provider: Literal['grok', 'claude', 'gemini', 'openai']

class Agent(AgentBase):
    id: UUID4
    created_at: datetime

class TopicBase(BaseModel):
    title: str

class Topic(TopicBase):
    id: UUID4
    created_at: datetime

class ConversationBase(BaseModel):
    agent_1_id: UUID4
    agent_2_id: UUID4
    topic_id: UUID4
    status: Literal['scheduled', 'active', 'completed'] = 'scheduled'
    topic_title: str
    full_conversation: Optional[str] = None

class Conversation(ConversationBase):
    id: UUID4
    created_at: datetime

class TurnBase(BaseModel):
    conversation_id: UUID4
    turn_number: int
    agent_id: UUID4
    text: str
    audio_url: Optional[str] = None

class Turn(TurnBase):
    id: int
    created_at: datetime

class ConsensusReportBase(BaseModel):
    topic_id: UUID4
    narrative_text: str
    audio_url: Optional[str] = None

class ConsensusReport(ConsensusReportBase):
    id: UUID4
    created_at: datetime
