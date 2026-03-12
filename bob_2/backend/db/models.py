import json
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text, JSON

class Base(DeclarativeBase):
    pass

class Turn(Base):
    __tablename__ = "turns"

    id: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[str]
    user_query: Mapped[str] = mapped_column(Text)
    reflection: Mapped[str] = mapped_column(Text)
    response: Mapped[str] = mapped_column(Text)
    state: Mapped[dict] = mapped_column(JSON, default=dict)
    keywords: Mapped[list] = mapped_column(JSON, default=list)
    memories_used: Mapped[int] = mapped_column(default=0)
    memory_ids_used: Mapped[list] = mapped_column(JSON, default=list)
    prompt_version: Mapped[str] = mapped_column(Text, default="1.0")
    is_consolidated: Mapped[bool] = mapped_column(default=False)
    consolidated_at: Mapped[str] = mapped_column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "user_query": self.user_query,
            "reflection": self.reflection,
            "response": self.response,
            "state": self.state,
            "keywords": self.keywords,
            "memories_used": self.memories_used,
            "memory_ids_used": self.memory_ids_used,
            "prompt_version": self.prompt_version,
            "is_consolidated": self.is_consolidated,
            "consolidated_at": self.consolidated_at
        }
