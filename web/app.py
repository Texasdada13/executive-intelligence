"""Executive Intelligence - Flask Web Application"""
import os
import sys
from flask import Flask, render_template, request, jsonify, Response, stream_with_context

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_config
from src.database.models import db
from src.database.repository import OrganizationRepository, StrategicGoalRepository, ExecutiveMetricsRepository, BoardReportRepository, ChatRepository
from src.ai_core.chat_engine import ChatEngine, ConversationMode
from src.ai_core.file_analyzer import create_file_analyzer
from src.patterns.executive_scoring import create_business_health_engine
from src.patterns.benchmark_engine import create_executive_benchmarks
from src.database.models import UploadedFile
from src.demo.data_generator import create_executive_demo_generator
from src.reports.report_generator import create_report_generator


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
    file_analyzer = create_file_analyzer()
    report_generator = create_report_generator()

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

    @app.route('/api/chat/sessions/<session_id>/suggestions', methods=['GET'])
    def api_chat_suggestions(session_id):
        """Get context-aware suggestions for a chat session."""
        if not chat_engine:
            return jsonify({'suggestions': [], 'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        messages = ChatRepository.get_messages(session_id)
        history = [{'role': m.role, 'content': m.content} for m in messages]
        context = session.context or {}
        discussed_topics = session.discussed_topics or []
        dismissed_prompts = session.dismissed_suggestions or []

        suggestions = chat_engine.get_dynamic_suggestions(
            mode=session.mode or 'general',
            context=context,
            conversation_history=history,
            discussed_topics=discussed_topics,
            dismissed_prompts=dismissed_prompts,
            max_suggestions=4
        )

        return jsonify({
            'suggestions': suggestions,
            'context_summary': {
                'mode': session.mode,
                'discussed_topics': discussed_topics,
                'message_count': len(messages)
            }
        })

    @app.route('/api/chat/sessions/<session_id>/dismiss', methods=['POST'])
    def api_dismiss_suggestion(session_id):
        """Dismiss a suggestion so it won't appear again."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        prompt_text = data.get('prompt')

        if prompt_text:
            dismissed = session.dismissed_suggestions or []
            if prompt_text not in dismissed:
                dismissed.append(prompt_text)
                session.dismissed_suggestions = dismissed
                db.session.commit()

        return jsonify({'success': True})

    @app.route('/api/chat/sessions/<session_id>/topics', methods=['POST'])
    def api_track_topics(session_id):
        """Track discussed topics from a message."""
        if not chat_engine:
            return jsonify({'error': 'Chat engine not available'}), 503

        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        data = request.json
        message = data.get('message', '')
        new_topics = chat_engine.extract_topics(message)

        discussed = session.discussed_topics or []
        for topic in new_topics:
            if topic not in discussed:
                discussed.append(topic)

        session.discussed_topics = discussed
        db.session.commit()

        return jsonify({
            'new_topics': new_topics,
            'all_topics': discussed
        })

    # ==================== FILE UPLOAD API ====================

    @app.route('/api/chat/sessions/<session_id>/upload', methods=['POST'])
    def api_upload_file(session_id):
        """Upload a file for analysis."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        content = file.read()
        filename = file.filename

        try:
            result = file_analyzer.analyze_file(content, filename)
        except Exception as e:
            return jsonify({'error': f'Failed to analyze file: {str(e)}'}), 400

        uploaded_file = UploadedFile(
            session_id=session_id,
            filename=filename,
            file_type=result.file_type,
            file_size=len(content),
            analysis_result=result.to_dict(),
            context_summary=result.data_summary,
            row_count=result.row_count,
            column_count=result.column_count,
            detected_metrics=result.detected_metrics
        )
        db.session.add(uploaded_file)
        db.session.commit()

        return jsonify({
            'file_id': uploaded_file.id,
            'filename': filename,
            'analysis': result.to_dict()
        }), 201

    @app.route('/api/chat/sessions/<session_id>/files', methods=['GET'])
    def api_list_files(session_id):
        """List files uploaded to a session."""
        session = ChatRepository.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        files = UploadedFile.query.filter_by(session_id=session_id).all()
        return jsonify({'files': [f.to_dict() for f in files]})

    @app.route('/api/chat/sessions/<session_id>/files/<file_id>', methods=['GET', 'DELETE'])
    def api_file_detail(session_id, file_id):
        """Get or delete a specific file."""
        uploaded_file = UploadedFile.query.filter_by(id=file_id, session_id=session_id).first()
        if not uploaded_file:
            return jsonify({'error': 'File not found'}), 404

        if request.method == 'DELETE':
            db.session.delete(uploaded_file)
            db.session.commit()
            return jsonify({'success': True})

        return jsonify(uploaded_file.to_dict())

    # ==================== DASHBOARD API ====================

    @app.route('/api/dashboard/<org_id>')
    def api_dashboard_data(org_id):
        """Get dashboard data for an organization."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        goals = StrategicGoalRepository.get_by_organization(org_id)
        metrics = ExecutiveMetricsRepository.get_latest(org_id)

        # Calculate goal metrics
        goals_on_track = sum(1 for g in goals if g.status in ['on_track', 'completed'])
        goals_at_risk = sum(1 for g in goals if g.status == 'at_risk')
        goals_behind = sum(1 for g in goals if g.status == 'behind')
        total_goals = len(goals)

        # Goal data for charts
        goal_data = [{
            'title': g.title,
            'category': g.category,
            'progress': round((g.current / g.target) * 100, 1) if g.target and g.target > 0 else 0,
            'status': g.status,
            'priority': g.priority
        } for g in goals]

        # Financial metrics (from metrics or defaults)
        financial = {
            'revenue_growth': 12.5,
            'profit_margin': 18.2,
            'cash_runway': 24,
            'burn_rate': 125000
        }

        # Customer metrics
        customer = {
            'nps_score': 42,
            'churn_rate': 3.2,
            'csat_score': 4.1,
            'ltv_cac_ratio': 3.5
        }

        # People metrics
        people = {
            'engagement_score': 78,
            'attrition_rate': 8.5,
            'hiring_velocity': 12,
            'diversity_index': 0.72
        }

        # C-Suite health scores
        csuite_health = {
            'ceo': 85,
            'cfo': 78,
            'cmo': 72,
            'cto': 81,
            'coo': 76,
            'chro': 69,
            'ciso': 74,
            'clo': 82
        }

        # Calculate overall business health grade
        avg_score = sum(csuite_health.values()) / len(csuite_health)
        if avg_score >= 90:
            grade = 'A'
        elif avg_score >= 80:
            grade = 'B'
        elif avg_score >= 70:
            grade = 'C'
        elif avg_score >= 60:
            grade = 'D'
        else:
            grade = 'F'

        # Trend data
        import random
        trend_data = {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
            'revenue': [1200000, 1350000, 1280000, 1450000],
            'profit': [180000, 220000, 195000, 260000]
        }

        return jsonify({
            'organization': org.to_dict(),
            'health': {
                'grade': grade,
                'score': round(avg_score, 1),
                'csuite_scores': csuite_health
            },
            'goals': {
                'total': total_goals,
                'on_track': goals_on_track,
                'at_risk': goals_at_risk,
                'behind': goals_behind,
                'items': goal_data
            },
            'financial': financial,
            'customer': customer,
            'people': people,
            'trend_data': trend_data
        })

    # ==================== EXPORT API ====================

    @app.route('/api/export/<org_id>/csv')
    def api_export_csv(org_id):
        """Export dashboard data as CSV."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        goals = StrategicGoalRepository.get_by_organization(org_id)

        goals_on_track = sum(1 for g in goals if g.status in ['on_track', 'completed'])
        goals_at_risk = sum(1 for g in goals if g.status == 'at_risk')
        goals_behind = sum(1 for g in goals if g.status == 'behind')

        csuite_health = {'ceo': 85, 'cfo': 78, 'cmo': 72, 'cto': 81, 'coo': 76, 'chro': 69, 'ciso': 74, 'clo': 82}
        avg_score = sum(csuite_health.values()) / len(csuite_health)
        grade = 'A' if avg_score >= 90 else 'B' if avg_score >= 80 else 'C' if avg_score >= 70 else 'D' if avg_score >= 60 else 'F'

        data = {
            'health': {'grade': grade, 'score': round(avg_score, 1), 'csuite_scores': csuite_health},
            'goals': {
                'total': len(goals),
                'on_track': goals_on_track,
                'at_risk': goals_at_risk,
                'behind': goals_behind,
                'items': [{
                    'title': g.title,
                    'category': g.category,
                    'progress': round((g.current / g.target) * 100, 1) if g.target and g.target > 0 else 0,
                    'status': g.status,
                    'priority': g.priority
                } for g in goals]
            },
            'financial': {'revenue_growth': 12.5, 'profit_margin': 18.2, 'cash_runway': 24, 'burn_rate': 125000},
            'customer': {'nps_score': 42, 'churn_rate': 3.2, 'csat_score': 4.1, 'ltv_cac_ratio': 3.5},
            'people': {'engagement_score': 78, 'attrition_rate': 8.5, 'hiring_velocity': 12, 'diversity_index': 0.72}
        }

        report_type = request.args.get('type', 'full')
        csv_content = report_generator.generate_csv(data, report_type)

        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=executive_report_{org_id}.csv'}
        )

    @app.route('/api/export/<org_id>/html')
    def api_export_html(org_id):
        """Export dashboard data as HTML report."""
        org = OrganizationRepository.get_by_id(org_id)
        if not org:
            return jsonify({'error': 'Organization not found'}), 404

        goals = StrategicGoalRepository.get_by_organization(org_id)

        goals_on_track = sum(1 for g in goals if g.status in ['on_track', 'completed'])
        goals_at_risk = sum(1 for g in goals if g.status == 'at_risk')
        goals_behind = sum(1 for g in goals if g.status == 'behind')

        csuite_health = {'ceo': 85, 'cfo': 78, 'cmo': 72, 'cto': 81, 'coo': 76, 'chro': 69, 'ciso': 74, 'clo': 82}
        avg_score = sum(csuite_health.values()) / len(csuite_health)
        grade = 'A' if avg_score >= 90 else 'B' if avg_score >= 80 else 'C' if avg_score >= 70 else 'D' if avg_score >= 60 else 'F'

        data = {
            'health': {'grade': grade, 'score': round(avg_score, 1), 'csuite_scores': csuite_health},
            'goals': {
                'total': len(goals),
                'on_track': goals_on_track,
                'at_risk': goals_at_risk,
                'behind': goals_behind,
                'items': [{
                    'title': g.title,
                    'category': g.category,
                    'progress': round((g.current / g.target) * 100, 1) if g.target and g.target > 0 else 0,
                    'status': g.status,
                    'priority': g.priority
                } for g in goals]
            },
            'financial': {'revenue_growth': 12.5, 'profit_margin': 18.2, 'cash_runway': 24, 'burn_rate': 125000},
            'customer': {'nps_score': 42, 'churn_rate': 3.2, 'csat_score': 4.1, 'ltv_cac_ratio': 3.5},
            'people': {'engagement_score': 78, 'attrition_rate': 8.5, 'hiring_velocity': 12, 'diversity_index': 0.72}
        }

        html_content = report_generator.generate_html_report(data, org.name)
        return Response(html_content, mimetype='text/html')

    # ==================== DEMO DATA API ====================

    @app.route('/api/demo/generate', methods=['POST'])
    def api_generate_demo():
        """Generate demo executive data."""
        data = request.json or {}
        org_name = data.get('organization_name')
        seed = data.get('seed')

        generator = create_executive_demo_generator(seed)
        demo_data = generator.generate_full_demo(org_name)

        return jsonify(demo_data)

    @app.route('/api/demo/load', methods=['POST'])
    def api_load_demo():
        """Generate demo data and load it into the database."""
        data = request.json or {}
        org_name = data.get('organization_name', 'Demo Enterprise Corp')
        seed = data.get('seed')

        generator = create_executive_demo_generator(seed)
        demo_data = generator.generate_full_demo(org_name)

        # Create organization
        org = OrganizationRepository.create(
            name=demo_data['organization']['name'],
            industry=demo_data['organization']['industry'],
            annual_revenue=demo_data['organization']['annual_revenue'],
            employee_count=demo_data['organization']['employee_count']
        )

        # Create strategic goals
        for goal_data in demo_data['strategic_goals']:
            StrategicGoalRepository.create(
                organization_id=org.id,
                title=goal_data['title'],
                category=goal_data['category'],
                target=goal_data['target'],
                current=goal_data['current'],
                status=goal_data['status'],
                priority=goal_data['priority'],
                owner=goal_data['owner']
            )

        return jsonify({
            'success': True,
            'organization_id': org.id,
            'organization_name': org.name,
            'goals_created': len(demo_data['strategic_goals']),
            'financial_metrics': demo_data['financial_metrics'],
            'customer_metrics': demo_data['customer_metrics'],
            'people_metrics': demo_data['people_metrics'],
            'metrics_summary': demo_data['metrics_summary']
        }), 201

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
