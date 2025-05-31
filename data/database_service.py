from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from database_config import get_db_session, close_db_session
from models import (
    AnalysisSession, AgentResult, AnalysisTemplate, 
    SystemLog, AgentPerformance
)

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Service layer for database operations.
    Provides high-level CRUD operations for the Strategic Intelligence App.
    """
    
    @staticmethod
    def create_analysis_session(
        strategic_question: str,
        time_frame: Optional[str] = None,
        region: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ) -> Optional[int]:
        """
        Create a new analysis session.
        Returns the session ID if successful, None if failed.
        """
        session = get_db_session()
        try:
            analysis_session = AnalysisSession(
                strategic_question=strategic_question,
                time_frame=time_frame,
                region=region,
                additional_instructions=additional_instructions,
                status='processing'
            )
            session.add(analysis_session)
            session.commit()
            session.refresh(analysis_session)
            
            logger.info(f"Created analysis session {analysis_session.id}")
            return analysis_session.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create analysis session: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def update_session_status(
        session_id: int, 
        status: str, 
        total_processing_time: Optional[float] = None
    ) -> bool:
        """
        Update analysis session status and completion time.
        """
        session = get_db_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(
                AnalysisSession.id == session_id
            ).first()
            
            if not analysis_session:
                logger.warning(f"Analysis session {session_id} not found")
                return False
            
            analysis_session.status = status
            if status == 'completed':
                analysis_session.completed_at = datetime.utcnow()
            if total_processing_time:
                analysis_session.total_processing_time = total_processing_time
            
            session.commit()
            logger.info(f"Updated session {session_id} status to {status}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update session status: {str(e)}")
            return False
        finally:
            close_db_session(session)
    
    @staticmethod
    def save_agent_result(
        session_id: int,
        agent_name: str,
        agent_type: str,
        raw_response: str,
        formatted_output: str,
        structured_data: Optional[Dict] = None,
        processing_time: Optional[float] = None,
        status: str = 'completed'
    ) -> Optional[int]:
        """
        Save an agent's result to the database.
        Returns the result ID if successful, None if failed.
        """
        session = get_db_session()
        try:
            agent_result = AgentResult(
                session_id=session_id,
                agent_name=agent_name,
                agent_type=agent_type,
                raw_response=raw_response,
                formatted_output=formatted_output,
                structured_data=structured_data,
                processing_time=processing_time,
                status=status,
                completed_at=datetime.utcnow()
            )
            session.add(agent_result)
            session.commit()
            session.refresh(agent_result)
            
            logger.info(f"Saved result for agent {agent_name} in session {session_id}")
            return agent_result.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save agent result: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_analysis_session(session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get analysis session with all agent results.
        """
        session = get_db_session()
        try:
            analysis_session = session.query(AnalysisSession).filter(
                AnalysisSession.id == session_id
            ).first()
            
            if not analysis_session:
                return None
            
            # Get all agent results for this session
            agent_results = session.query(AgentResult).filter(
                AgentResult.session_id == session_id
            ).order_by(AgentResult.created_at).all()
            
            result = analysis_session.to_dict()
            result['agent_results'] = [agent_result.to_dict() for agent_result in agent_results]
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get analysis session: {str(e)}")
            return None
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent analysis sessions.
        """
        session = get_db_session()
        try:
            sessions = session.query(AnalysisSession).order_by(
                desc(AnalysisSession.created_at)
            ).limit(limit).all()
            
            return [s.to_dict() for s in sessions]
            
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def search_sessions(
        search_term: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search analysis sessions with filters.
        """
        session = get_db_session()
        try:
            query = session.query(AnalysisSession)
            
            # Apply filters
            if search_term:
                query = query.filter(
                    or_(
                        AnalysisSession.strategic_question.ilike(f"%{search_term}%"),
                        AnalysisSession.additional_instructions.ilike(f"%{search_term}%")
                    )
                )
            
            if status:
                query = query.filter(AnalysisSession.status == status)
            
            if date_from:
                query = query.filter(AnalysisSession.created_at >= date_from)
            
            if date_to:
                query = query.filter(AnalysisSession.created_at <= date_to)
            
            sessions = query.order_by(
                desc(AnalysisSession.created_at)
            ).limit(limit).all()
            
            return [s.to_dict() for s in sessions]
            
        except Exception as e:
            logger.error(f"Failed to search sessions: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def log_system_event(
        log_level: str,
        component: str,
        message: str,
        session_id: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> bool:
        """
        Log a system event.
        """
        session = get_db_session()
        try:
            log_entry = SystemLog(
                session_id=session_id,
                log_level=log_level,
                component=component,
                message=message,
                details=details
            )
            session.add(log_entry)
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to log system event: {str(e)}")
            return False
        finally:
            close_db_session(session)
    
    @staticmethod
    def get_agent_performance_stats(
        agent_name: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get agent performance statistics.
        """
        session = get_db_session()
        try:
            query = session.query(AgentResult)
            
            # Filter by date
            date_threshold = datetime.utcnow() - timedelta(days=days_back)
            query = query.filter(AgentResult.created_at >= date_threshold)
            
            if agent_name:
                query = query.filter(AgentResult.agent_name == agent_name)
            
            results = query.all()
            
            # Calculate statistics
            stats = {}
            for result in results:
                name = result.agent_name
                if name not in stats:
                    stats[name] = {
                        'agent_name': name,
                        'total_executions': 0,
                        'successful_executions': 0,
                        'failed_executions': 0,
                        'timeout_executions': 0,
                        'processing_times': []
                    }
                
                stats[name]['total_executions'] += 1
                if result.status == 'completed':
                    stats[name]['successful_executions'] += 1
                elif result.status == 'failed':
                    stats[name]['failed_executions'] += 1
                elif result.status == 'timeout':
                    stats[name]['timeout_executions'] += 1
                
                if result.processing_time:
                    stats[name]['processing_times'].append(result.processing_time)
            
            # Calculate averages
            for agent_stats in stats.values():
                times = agent_stats['processing_times']
                if times:
                    agent_stats['average_processing_time'] = sum(times) / len(times)
                    agent_stats['min_processing_time'] = min(times)
                    agent_stats['max_processing_time'] = max(times)
                else:
                    agent_stats['average_processing_time'] = None
                    agent_stats['min_processing_time'] = None
                    agent_stats['max_processing_time'] = None
                
                # Remove processing_times list from output
                del agent_stats['processing_times']
            
            return list(stats.values())
            
        except Exception as e:
            logger.error(f"Failed to get agent performance stats: {str(e)}")
            return []
        finally:
            close_db_session(session)
    
    @staticmethod
    def delete_old_sessions(days_old: int = 30) -> int:
        """
        Delete analysis sessions older than specified days.
        Returns number of deleted sessions.
        """
        session = get_db_session()
        try:
            date_threshold = datetime.utcnow() - timedelta(days=days_old)
            
            # Get sessions to delete
            old_sessions = session.query(AnalysisSession).filter(
                AnalysisSession.created_at < date_threshold
            ).all()
            
            count = len(old_sessions)
            
            # Delete sessions (cascades to agent_results)
            session.query(AnalysisSession).filter(
                AnalysisSession.created_at < date_threshold
            ).delete()
            
            session.commit()
            logger.info(f"Deleted {count} old analysis sessions")
            return count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to delete old sessions: {str(e)}")
            return 0
        finally:
            close_db_session(session) 