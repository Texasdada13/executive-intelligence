"""Executive Intelligence - Database Models"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


def generate_uuid():
    return str(uuid.uuid4())


class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100))
    size = db.Column(db.String(50))
    stage = db.Column(db.String(50))  # Startup, Growth, Mature
    fiscal_year_end = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    goals = db.relationship('StrategicGoal', backref='organization', lazy=True)
    metrics = db.relationship('ExecutiveMetrics', backref='organization', lazy=True)
    reports = db.relationship('BoardReport', backref='organization', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='organization', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'industry': self.industry,
            'size': self.size, 'stage': self.stage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class StrategicGoal(db.Model):
    __tablename__ = 'strategic_goals'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    owner = db.Column(db.String(100))
    priority = db.Column(db.Integer, default=1)
    status = db.Column(db.String(30), default='Not Started')
    start_date = db.Column(db.Date)
    target_date = db.Column(db.Date)
    progress = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    key_results = db.relationship('KeyResult', backref='goal', lazy=True)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'category': self.category, 'owner': self.owner, 'priority': self.priority,
            'status': self.status, 'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None
        }


class KeyResult(db.Model):
    __tablename__ = 'key_results'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    goal_id = db.Column(db.String(36), db.ForeignKey('strategic_goals.id'), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))

    def to_dict(self):
        progress = (self.current_value / self.target_value * 100) if self.target_value else 0
        return {
            'id': self.id, 'description': self.description,
            'target': self.target_value, 'current': self.current_value,
            'unit': self.unit, 'progress': round(progress, 1)
        }


class ExecutiveMetrics(db.Model):
    __tablename__ = 'executive_metrics'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    period = db.Column(db.String(20))
    period_date = db.Column(db.Date)

    # Financial
    revenue = db.Column(db.Float)
    revenue_growth = db.Column(db.Float)
    gross_margin = db.Column(db.Float)
    operating_margin = db.Column(db.Float)
    cash_position = db.Column(db.Float)
    burn_rate = db.Column(db.Float)

    # Customer
    customer_count = db.Column(db.Integer)
    customer_growth = db.Column(db.Float)
    nps = db.Column(db.Float)
    churn_rate = db.Column(db.Float)

    # People
    employee_count = db.Column(db.Integer)
    employee_engagement = db.Column(db.Float)
    voluntary_turnover = db.Column(db.Float)

    # Health scores
    overall_health = db.Column(db.Float)
    financial_health = db.Column(db.Float)
    operational_health = db.Column(db.Float)
    customer_health = db.Column(db.Float)
    people_health = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'period': self.period,
            'revenue': self.revenue, 'revenue_growth': self.revenue_growth,
            'customer_count': self.customer_count, 'nps': self.nps,
            'employee_count': self.employee_count,
            'overall_health': self.overall_health
        }


class BoardReport(db.Model):
    __tablename__ = 'board_reports'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False)
    period = db.Column(db.String(20))
    period_date = db.Column(db.Date)
    executive_summary = db.Column(db.Text)
    key_achievements = db.Column(db.JSON)
    challenges = db.Column(db.JSON)
    priorities = db.Column(db.JSON)
    board_asks = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'period': self.period,
            'period_date': self.period_date.isoformat() if self.period_date else None,
            'executive_summary': self.executive_summary,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=True)
    mode = db.Column(db.String(50), default='general')
    title = db.Column(db.String(200))
    context = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('ChatMessage', backref='session', lazy=True, order_by='ChatMessage.created_at')

    def to_dict(self):
        return {
            'id': self.id, 'mode': self.mode, 'title': self.title,
            'message_count': len(self.messages) if self.messages else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {'id': self.id, 'role': self.role, 'content': self.content,
                'created_at': self.created_at.isoformat() if self.created_at else None}
