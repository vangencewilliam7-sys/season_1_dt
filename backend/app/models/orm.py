import enum
import uuid
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class SkillType(enum.Enum):
    Basic = "Basic"
    Functional = "Functional"

# -----------------------------------------------------------------------------
# Layer 1: Hubs
# -----------------------------------------------------------------------------
class Hub(Base):
    __tablename__ = "hubs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    domains = relationship("Domain", back_populates="hub", cascade="all, delete-orphan", lazy="selectin")

# -----------------------------------------------------------------------------
# Layer 2: Domains
# -----------------------------------------------------------------------------
class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hub_id = Column(UUID(as_uuid=True), ForeignKey("hubs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    hub = relationship("Hub", back_populates="domains")
    roles = relationship("Role", back_populates="domain", cascade="all, delete-orphan", lazy="selectin")

# -----------------------------------------------------------------------------
# Layer 3: Roles
# -----------------------------------------------------------------------------
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    domain = relationship("Domain", back_populates="roles")
    workflows = relationship("Workflow", back_populates="role", cascade="all, delete-orphan", lazy="selectin")

# -----------------------------------------------------------------------------
# Layer 4: Workflows
# -----------------------------------------------------------------------------
class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    role = relationship("Role", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow", cascade="all, delete-orphan", lazy="selectin")
    skills = relationship("WorkflowSkill", back_populates="workflow", cascade="all, delete-orphan", lazy="selectin")

# -----------------------------------------------------------------------------
# Layer 5: Tasks
# -----------------------------------------------------------------------------
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workflow = relationship("Workflow", back_populates="tasks")

# -----------------------------------------------------------------------------
# Skills Engine Node
# -----------------------------------------------------------------------------
class SkillDefinition(Base):
    __tablename__ = "skill_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name = Column(String, nullable=False, unique=True)
    skill_type = Column(Enum(SkillType), nullable=False)
    is_active = Column(Boolean, default=True)
    requires_human_approval = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workflow_links = relationship("WorkflowSkill", back_populates="skill", cascade="all, delete-orphan")

class WorkflowSkill(Base):
    __tablename__ = "workflow_skills"
    
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skill_definitions.id", ondelete="CASCADE"), primary_key=True)
    functional_context_description = Column(Text)
    
    workflow = relationship("Workflow", back_populates="skills")
    skill = relationship("SkillDefinition", back_populates="workflow_links")

# -----------------------------------------------------------------------------
# Orchestration Tracking Tables
# -----------------------------------------------------------------------------
class StateLedger(Base):
    __tablename__ = "state_ledger"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    expert_id = Column(UUID(as_uuid=True), nullable=False)
    current_state = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    workflow = relationship("Workflow")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"))
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skill_definitions.id", ondelete="SET NULL"))
    expert_id = Column(UUID(as_uuid=True), nullable=False)
    raw_payload = Column(JSON)
    status = Column(String)
    error_trace = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workflow = relationship("Workflow")
    task = relationship("Task")
    skill = relationship("SkillDefinition")
