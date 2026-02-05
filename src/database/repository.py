"""Executive Intelligence - Repository Pattern"""
from typing import List, Optional, Dict
from datetime import datetime
from .models import db, Organization, StrategicGoal, KeyResult, ExecutiveMetrics, BoardReport, ChatSession, ChatMessage


class OrganizationRepository:
    @staticmethod
    def create(name: str, **kwargs) -> Organization:
        org = Organization(name=name, **kwargs)
        db.session.add(org)
        db.session.commit()
        return org

    @staticmethod
    def get_by_id(org_id: str) -> Optional[Organization]:
        return Organization.query.get(org_id)

    @staticmethod
    def get_all() -> List[Organization]:
        return Organization.query.order_by(Organization.name).all()

    @staticmethod
    def update(org_id: str, **kwargs) -> Optional[Organization]:
        org = Organization.query.get(org_id)
        if org:
            for key, value in kwargs.items():
                if hasattr(org, key):
                    setattr(org, key, value)
            db.session.commit()
        return org

    @staticmethod
    def delete(org_id: str) -> bool:
        org = Organization.query.get(org_id)
        if org:
            db.session.delete(org)
            db.session.commit()
            return True
        return False


class StrategicGoalRepository:
    @staticmethod
    def create(organization_id: str, title: str, **kwargs) -> StrategicGoal:
        goal = StrategicGoal(organization_id=organization_id, title=title, **kwargs)
        db.session.add(goal)
        db.session.commit()
        return goal

    @staticmethod
    def get_by_organization(org_id: str) -> List[StrategicGoal]:
        return StrategicGoal.query.filter_by(organization_id=org_id).order_by(StrategicGoal.priority).all()

    @staticmethod
    def update(goal_id: str, **kwargs) -> Optional[StrategicGoal]:
        goal = StrategicGoal.query.get(goal_id)
        if goal:
            for key, value in kwargs.items():
                if hasattr(goal, key):
                    setattr(goal, key, value)
            db.session.commit()
        return goal


class ExecutiveMetricsRepository:
    @staticmethod
    def create(organization_id: str, **kwargs) -> ExecutiveMetrics:
        metrics = ExecutiveMetrics(organization_id=organization_id, **kwargs)
        db.session.add(metrics)
        db.session.commit()
        return metrics

    @staticmethod
    def get_latest(org_id: str) -> Optional[ExecutiveMetrics]:
        return ExecutiveMetrics.query.filter_by(organization_id=org_id)\
            .order_by(ExecutiveMetrics.period_date.desc()).first()

    @staticmethod
    def get_history(org_id: str, limit: int = 12) -> List[ExecutiveMetrics]:
        return ExecutiveMetrics.query.filter_by(organization_id=org_id)\
            .order_by(ExecutiveMetrics.period_date.desc()).limit(limit).all()


class BoardReportRepository:
    @staticmethod
    def create(organization_id: str, **kwargs) -> BoardReport:
        report = BoardReport(organization_id=organization_id, **kwargs)
        db.session.add(report)
        db.session.commit()
        return report

    @staticmethod
    def get_latest(org_id: str) -> Optional[BoardReport]:
        return BoardReport.query.filter_by(organization_id=org_id)\
            .order_by(BoardReport.period_date.desc()).first()


class ChatRepository:
    @staticmethod
    def create_session(mode: str = 'general', organization_id: str = None,
                       title: str = None, context: Dict = None) -> ChatSession:
        session = ChatSession(mode=mode, organization_id=organization_id,
                              title=title or "Chat Session", context=context or {})
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_session(session_id: str) -> Optional[ChatSession]:
        return ChatSession.query.get(session_id)

    @staticmethod
    def get_sessions(organization_id: str = None, limit: int = 20) -> List[ChatSession]:
        query = ChatSession.query
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query.order_by(ChatSession.updated_at.desc()).limit(limit).all()

    @staticmethod
    def add_message(session_id: str, role: str, content: str) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content)
        db.session.add(message)
        session = ChatSession.query.get(session_id)
        if session:
            session.updated_at = datetime.utcnow()
        db.session.commit()
        return message

    @staticmethod
    def get_messages(session_id: str) -> List[ChatMessage]:
        return ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()

    @staticmethod
    def delete_session(session_id: str) -> bool:
        session = ChatSession.query.get(session_id)
        if session:
            ChatMessage.query.filter_by(session_id=session_id).delete()
            db.session.delete(session)
            db.session.commit()
            return True
        return False
