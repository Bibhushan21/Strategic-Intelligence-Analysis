from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_config import Base
from datetime import datetime
from typing import Dict, Any, Optional

class AnalysisSession(Base):
    """
    Main analysis session table.
    Stores each strategic intelligence analysis request.
    """
    __tablename__ = 'analysis_sessions'
    
    id = Column(Integer, primary_key=True, index=True)
    strategic_question = Column(Text, nullable=False)
    time_frame = Column(String(50))
    region = Column(String(100))
    additional_instructions = Column(Text)
    status = Column(String(50), default='processing')  # processing, completed, failed
    total_processing_time = Column(Float)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    agent_results = relationship("AgentResult", back_populates="session", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'strategic_question': self.strategic_question,
            'time_frame': self.time_frame,
            'region': self.region,
            'additional_instructions': self.additional_instructions,
            'status': self.status,
            'total_processing_time': self.total_processing_time,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AgentResult(Base):
    """
    Individual agent results table.
    Stores the output from each agent in an analysis session.
    """
    __tablename__ = 'agent_results'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_sessions.id'), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(100))  # Type/category of agent
    raw_response = Column(Text)  # Raw LLM response
    formatted_output = Column(Text)  # Markdown formatted output
    structured_data = Column(JSON)  # Parsed structured data
    processing_time = Column(Float)  # Processing time in seconds
    status = Column(String(50), default='processing')  # processing, completed, failed, timeout
    error_message = Column(Text)  # Error details if failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    session = relationship("AnalysisSession", back_populates="agent_results")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'raw_response': self.raw_response,
            'formatted_output': self.formatted_output,
            'structured_data': self.structured_data,
            'processing_time': self.processing_time,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AnalysisTemplate(Base):
    """
    Analysis templates table.
    Store commonly used analysis configurations for quick reuse.
    """
    __tablename__ = 'analysis_templates'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    strategic_question_template = Column(Text)
    default_time_frame = Column(String(50))
    default_region = Column(String(100))
    default_instructions = Column(Text)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'strategic_question_template': self.strategic_question_template,
            'default_time_frame': self.default_time_frame,
            'default_region': self.default_region,
            'default_instructions': self.default_instructions,
            'usage_count': self.usage_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemLog(Base):
    """
    System logs table.
    Track system performance, errors, and usage statistics.
    """
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('analysis_sessions.id'), nullable=True)
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    component = Column(String(100))  # orchestrator, agent_name, database, etc.
    message = Column(Text, nullable=False)
    details = Column(JSON)  # Additional structured details
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'log_level': self.log_level,
            'component': self.component,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class AgentPerformance(Base):
    """
    Agent performance metrics table.
    Track performance statistics for each agent.
    """
    __tablename__ = 'agent_performance'
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_executions = Column(Integer, default=0)
    successful_executions = Column(Integer, default=0)
    failed_executions = Column(Integer, default=0)
    timeout_executions = Column(Integer, default=0)
    average_processing_time = Column(Float)  # in seconds
    min_processing_time = Column(Float)
    max_processing_time = Column(Float)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'agent_name': self.agent_name,
            'date': self.date.isoformat() if self.date else None,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'failed_executions': self.failed_executions,
            'timeout_executions': self.timeout_executions,
            'average_processing_time': self.average_processing_time,
            'min_processing_time': self.min_processing_time,
            'max_processing_time': self.max_processing_time
        } 