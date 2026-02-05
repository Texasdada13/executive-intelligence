"""Executive Intelligence - Flask Web Application"""
import os
import sys
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_config
from src.database.models import db
from src.database.repository import OrganizationRepository, StrategicGoalRepository, ExecutiveMetricsRepository, BoardReportRepository, ChatRepository
from src.ai_core.chat_engine import ChatEngine, ConversationMode
from src.patterns.executive_scoring import create_business_health_engine
from src.patterns.benchmark_engine import create_executive_benchmarks


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    config = get_config()
    app.config.from_object(config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    try:
        chat_engine = ChatEngine()
    except Exception as e:
        print(f"Warning: Could not initialize ChatEngine: {e}")
        chat_engine = None

    health_engine = create_business_health_engine()
    benchmark_engine = create_executive_benchmarks()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        organizations = OrganizationRepository.get_all()
        return render_template('dashboard.html', organizations=organizations)

    @app.route('/organization/<org_id>')
    def organization_detail(org_id):
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return render_template('404.html'), 404
        goals = StrategicGoalRepository.get_by_organization(org_id)
        metrics = ExecutiveMetricsRepository.get_latest(org_id)
        return render_template('organization.html', organization=org, goals=goals, metrics=metrics)

    @app.route('/chat')
    def chat_page():
        modes = {mode.value: desc for mode, desc in [
            (ConversationMode.GENERAL, "General executive guidance"),
            (ConversationMode.BUSINESS_HEALTH, "Business health assessment"),
            (ConversationMode.STRATEGIC_PLANNING, "Strategic planning"),
            (ConversationMode.BOARD_PREP, "Board preparation"),
            (ConversationMode.DECISION_SUPPORT, "Decision support"),
            (ConversationMode.CSUITE_REVIEW, "C-Suite review"),
            (ConversationMode.GROWTH_STRATEGY, "Growth strategy"),
            (ConversationMode.RISK_OVERVIEW, "Risk overview"),
        ]}
        return render_template('chat.html', modes=modes)

    @app.route('/api/organizations', methods=['GET', 'POST'])
    def api_organizations():
        if request.method == 'POST':
            data = request.json
            org = OrganizationRepository.create(name=data.get('name'), **{k: v for k, v in data.items() if k != 'name'})
            return jsonify(org.to_dict()), 201
        return jsonify([org.to_dict() for org in OrganizationRepository.get_all()])

    @app.route('/api/organizations/<org_id>', methods=['GET', 'PUT', 'DELETE'])
    def api_organization(org_id):
        if request.method == 'DELETE':
            return jsonify({'success': OrganizationRepository.delete(org_id)})
        if request.method == 'PUT':
            org = OrganizationRepository.update(org_id, **request.json)
            return jsonify(org.to_dict()) if org else ('Not found', 404)
        org = OrganizationRepository.get_by_id(org_id)
        return jsonify(org.to_dict()) if org else ('Not found', 404)

    @app.route('/api/organizations/<org_id>/goals', methods=['GET', 'POST'])
    def api_goals(org_id):
        if request.method == 'POST':
            data = request.json
            goal = StrategicGoalRepository.create(organization_id=org_id, **data)
            return jsonify(goal.to_dict()), 201
        return jsonify([g.to_dict() for g in StrategicGoalRepository.get_by_organization(org_id)])

    @app.route('/api/chat/sessions', methods=['GET', 'POST'])
    def api_chat_sessions():
        if request.method == 'POST':
            data = request.json
            session = ChatRepository.create_session(
                mode=data.get('mode', 'general'),
                organization_id=data.get('organization_id'),
                title=data.get('title'),
                context=data.get('context')
            )
            return jsonify(session.to_dict()), 201
        return jsonify([s.to_dict() for s in ChatRepository.get_sessions(limit=20)])

    @app.route('/api/chat/sessions/<session_id>', methods=['GET', 'DELETE'])
    def api_chat_session(session_id):
        if request.method == 'DELETE':
            return jsonify({'success': ChatRepository.delete_session(session_id)})
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        messages = ChatRepository.get_messages(session_id)
        return jsonify({'session': session.to_dict(), 'messages': [m.to_dict() for m in messages]})

    @app.route('/api/chat/sessions/<session_id>/stream', methods=['POST'])
    def api_chat_stream(session_id):
        if not chat_engine:
            return jsonify({'error': 'Chat engine not available'}), 503
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        user_message = data.get('message', '')
        ChatRepository.add_message(session_id, 'user', user_message)

        messages = ChatRepository.get_messages(session_id)
        history = [{'role': m.role, 'content': m.content} for m in messages[:-1]]
        mode = ConversationMode(session.mode) if session.mode else ConversationMode.GENERAL
        context = session.context or {}

        def generate():
            full_response = []
            for chunk in chat_engine.chat_stream(user_message, mode=mode, history=history, context=context):
                full_response.append(chunk)
                yield f"data: {chunk}\n\n"
            ChatRepository.add_message(session_id, 'assistant', ''.join(full_response))
            yield "data: [DONE]\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')

    @app.route('/api/chat/prompts/<mode>')
    def api_suggested_prompts(mode):
        if chat_engine:
            try:
                return jsonify({'prompts': chat_engine.get_suggested_prompts(ConversationMode(mode))})
            except ValueError:
                pass
        return jsonify({'prompts': []})

    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'executive-intelligence', 'ai_enabled': chat_engine is not None})

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return render_template('404.html'), 404

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
