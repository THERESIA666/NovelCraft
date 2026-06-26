"""
AI小说写作助手 (轻量版) - Flask 主应用
"""
import os
import json
import uuid
import secrets
from flask import Flask, render_template, request, jsonify, Response, send_file, session, redirect
from flask_cors import CORS
from utils.ai_client import AIClient, SYSTEM_PROMPT
from utils.novel_manager import NovelManager
from utils.exporter import NovelExporter
from utils.auth import user_manager, login_required, admin_required

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 7
CORS(app, supports_credentials=True)

BASE_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'novels')
os.makedirs(BASE_DATA_DIR, exist_ok=True)

exporter = NovelExporter()
ai_clients = {}
stop_flags = {}
novel_managers = {}


def get_novel_manager():
    username = session.get('username', 'anonymous')
    if username not in novel_managers:
        user_dir = os.path.join(BASE_DATA_DIR, username)
        novel_managers[username] = NovelManager(user_dir)
    return novel_managers[username]


def get_ai_client(session_id):
    if session_id not in ai_clients:
        ai_clients[session_id] = AIClient()
    return ai_clients[session_id]


# ==================== 小说管理 API ====================

@app.route('/api/novels', methods=['GET'])
def list_novels():
    novels = get_novel_manager().list_novels()
    return jsonify({'success': True, 'novels': novels})


@app.route('/api/novels', methods=['POST'])
def create_novel():
    data = request.json or {}
    title = data.get('title', '未命名小说')
    characters = data.get('characters', [])
    plot = data.get('plot', '')
    novel = get_novel_manager().create_novel(title, characters, plot)
    return jsonify({'success': True, 'novel': novel})


@app.route('/api/novels/<novel_id>', methods=['GET'])
def get_novel(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    return jsonify({'success': True, 'novel': novel})


@app.route('/api/novels/<novel_id>', methods=['PUT'])
def update_novel(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    data = request.json or {}
    if 'title' in data:
        novel['title'] = data['title']
    if 'characters' in data:
        novel['characters'] = data['characters']
    if 'plot' in data:
        novel['plot'] = data['plot']
    get_novel_manager().save_novel(novel_id, novel)
    return jsonify({'success': True, 'novel': novel})


@app.route('/api/novels/<novel_id>', methods=['DELETE'])
def delete_novel(novel_id):
    if get_novel_manager().delete_novel(novel_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '小说不存在'}), 404


# ==================== 内容管理 API ====================

@app.route('/api/novels/<novel_id>/content', methods=['GET'])
def get_content(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    content = get_novel_manager().get_content(novel_id)
    return jsonify({'success': True, 'content': content, 'new_content': novel.get('new_content', '')})


@app.route('/api/novels/<novel_id>/content', methods=['PUT'])
def update_content(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    data = request.json or {}
    content = data.get('content', '')
    get_novel_manager().save_content(novel_id, content)
    return jsonify({'success': True})


# ==================== 角色管理 API ====================

@app.route('/api/novels/<novel_id>/characters', methods=['GET'])
def get_characters(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    return jsonify({'success': True, 'characters': novel.get('characters', [])})


@app.route('/api/novels/<novel_id>/characters', methods=['POST'])
def update_characters(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    data = request.json or {}
    characters = data.get('characters', [])
    novel['characters'] = characters
    get_novel_manager().save_novel(novel_id, novel)
    return jsonify({'success': True, 'characters': characters})


# ==================== 情节大纲 API ====================

@app.route('/api/novels/<novel_id>/plot', methods=['GET'])
def get_plot(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    return jsonify({'success': True, 'plot': novel.get('plot', '')})


@app.route('/api/novels/<novel_id>/plot', methods=['POST'])
def update_plot(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    data = request.json or {}
    plot = data.get('plot', '')
    novel['plot'] = plot
    get_novel_manager().save_novel(novel_id, novel)
    return jsonify({'success': True, 'plot': plot})


# ==================== AI对话 API ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    novel_id = data.get('novel_id')
    message = data.get('message', '')
    api_key = data.get('api_key', '')
    api_base = data.get('api_base', 'https://api.deepseek.com/v1')
    model = data.get('model', 'deepseek-chat')
    temperature = data.get('temperature', 0.8)
    max_tokens = data.get('max_tokens', 4096)

    if not api_key:
        return jsonify({'success': False, 'error': '请先配置API Key'}), 400
    if not message:
        return jsonify({'success': False, 'error': '消息不能为空'}), 400

    context = {}
    if novel_id:
        novel = get_novel_manager().get_novel(novel_id)
        if novel:
            context = {
                'title': novel.get('title', ''),
                'characters': novel.get('characters', []),
                'plot': novel.get('plot', ''),
                'content': get_novel_manager().get_content(novel_id)
            }

    history = get_novel_manager().get_history(novel_id) if novel_id else []
    client = get_ai_client(session_id)
    client.configure(api_key, api_base, model, temperature, max_tokens)
    stop_flags[session_id] = False

    def generate():
        try:
            for chunk in client.chat_stream(message, context, history):
                if stop_flags.get(session_id, False):
                    break
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route('/api/chat/stop', methods=['POST'])
def stop_chat():
    data = request.json or {}
    session_id = data.get('session_id', 'default')
    stop_flags[session_id] = True
    return jsonify({'success': True})


@app.route('/api/chat/save', methods=['POST'])
def save_chat():
    data = request.json or {}
    novel_id = data.get('novel_id')
    message = data.get('message', '')
    response_text = data.get('response', '')

    if not novel_id:
        return jsonify({'success': False, 'error': '缺少小说ID'}), 400

    get_novel_manager().add_history(novel_id, message, response_text)

    result = {'success': True, 'content_updated': False, 'suggestions': {}}

    # 替换内容 → 完全替换
    replace_content = _extract_tagged_content(response_text, '替换内容')
    if replace_content:
        # 安全检查：防止AI用拒绝消息覆盖全文
        if _is_refusal(replace_content):
            result['content_updated'] = False
            result['warning'] = 'AI返回了疑似拒绝内容，已阻止覆盖全文'
            return jsonify(result)
        # 安全检查：替换内容过短时拦截
        current_content = get_novel_manager().get_content(novel_id)
        if len(current_content) > 1000 and len(replace_content) < 50:
            result['content_updated'] = False
            result['warning'] = 'AI返回替换内容过短，疑似出错，已阻止覆盖'
            return jsonify(result)

        get_novel_manager().save_content(novel_id, replace_content)
        novel = get_novel_manager().get_novel(novel_id)
        novel['new_content'] = replace_content
        get_novel_manager().save_novel(novel_id, novel)
        result['content_updated'] = True
        result['content_replaced'] = True
        return jsonify(result)

    # 小说内容 → 追加
    append_content = _extract_tagged_content(response_text, '小说内容')
    if append_content:
        current_content = get_novel_manager().get_content(novel_id)
        new_content = current_content + '\n\n' + append_content
        get_novel_manager().save_content(novel_id, new_content.strip())
        novel = get_novel_manager().get_novel(novel_id)
        novel['new_content'] = append_content
        get_novel_manager().save_novel(novel_id, novel)
        result['content_updated'] = True

    # 角色建议
    char_suggestions = _extract_character_suggestions(response_text)
    if char_suggestions:
        result['suggestions']['characters'] = char_suggestions

    # 情节建议
    plot_suggestion = _extract_tagged_content(response_text, '情节建议')
    if plot_suggestion:
        result['suggestions']['plot'] = plot_suggestion

    return jsonify(result)


@app.route('/api/novels/<novel_id>/apply-suggestion', methods=['POST'])
def apply_suggestion(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    data = request.json or {}
    suggest_type = data.get('type', '')
    value = data.get('value')
    if suggest_type == 'characters':
        novel['characters'] = value
    elif suggest_type == 'plot':
        novel['plot'] = value
    else:
        return jsonify({'success': False, 'error': '无效的建议类型'}), 400
    get_novel_manager().save_novel(novel_id, novel)
    return jsonify({'success': True, 'novel': novel})


def _is_refusal(text):
    """检测文本是否为AI拒绝响应"""
    refusal_patterns = ['抱歉', '我无法', '不能生成', '不能继续', '违反',
                        '色情', '换个话题', '不建议', '请理解']
    text_stripped = text.strip()
    if len(text_stripped) < 100:
        for p in refusal_patterns:
            if p in text_stripped: return True
    if len(text_stripped) < 300:
        if sum(1 for p in refusal_patterns if p in text_stripped) >= 2: return True
    return False


def _extract_tagged_content(text, tag_name):
    import re
    pattern = rf'【{tag_name}】\s*\n?(.*?)\n?\s*【/{tag_name}】'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_character_suggestions(text):
    import re, json
    json_str = _extract_tagged_content(text, '角色建议')
    if not json_str:
        return None
    try:
        characters = json.loads(json_str)
        if isinstance(characters, list) and len(characters) > 0:
            for char in characters:
                if not (isinstance(char, dict) and 'name' in char):
                    return None
            return characters
    except (json.JSONDecodeError, TypeError):
        pass
    return None


# ==================== 续写 API ====================

@app.route('/api/novels/<novel_id>/continue', methods=['POST'])
def continue_writing(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404

    data = request.json or {}
    session_id = data.get('session_id', 'default')
    api_key = data.get('api_key', '')
    api_base = data.get('api_base', 'https://api.deepseek.com/v1')
    model = data.get('model', 'deepseek-chat')
    temperature = data.get('temperature', 0.8)
    max_tokens = data.get('max_tokens', 4096)
    start_from = data.get('start_from', '')
    instruction = data.get('instruction', '')

    if not api_key:
        return jsonify({'success': False, 'error': '请先配置API Key'}), 400

    content = get_novel_manager().get_content(novel_id)
    if not start_from:
        start_from = content[-500:] if len(content) > 500 else content

    context = {
        'title': novel.get('title', ''),
        'characters': novel.get('characters', []),
        'plot': novel.get('plot', ''),
        'content': content
    }

    history = get_novel_manager().get_history(novel_id)
    client = get_ai_client(session_id)
    client.configure(api_key, api_base, model, temperature, max_tokens)
    stop_flags[session_id] = False

    prompt = f"""请续写以下小说内容。

续写起点：
{start_from}

"""
    if instruction:
        prompt += f"续写要求：{instruction}\n\n"
    prompt += """请使用【小说内容】...【/小说内容】标签包围你写的新内容。"""

    def generate():
        try:
            for chunk in client.chat_stream(prompt, context, history, is_continuation=True):
                if stop_flags.get(session_id, False):
                    break
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


# ==================== 导出 API ====================

@app.route('/api/novels/<novel_id>/export', methods=['GET'])
def export_novel(novel_id):
    novel = get_novel_manager().get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    export_format = request.args.get('format', 'txt')
    content = get_novel_manager().get_content(novel_id)
    title = novel.get('title', '未命名小说')
    characters = novel.get('characters', [])
    plot = novel.get('plot', '')

    parts = [f"《{title}》", "=" * 40]
    if characters:
        parts.append("\n【角色介绍】")
        for char in characters:
            if isinstance(char, dict):
                parts.append(f"  {char.get('name', '')}：{char.get('description', '')}")
            else:
                parts.append(f"  {char}")
    if plot:
        parts.append("\n【情节大纲】")
        parts.append(f"  {plot}")
    parts.append("\n【正文】")
    parts.append("=" * 40)
    parts.append(content)
    full_content = '\n'.join(parts)

    export_dir = os.path.join(os.path.dirname(BASE_DATA_DIR), 'exports')
    os.makedirs(export_dir, exist_ok=True)

    if export_format == 'txt':
        filepath = exporter.export_txt(title, full_content, export_dir)
        return send_file(filepath, as_attachment=True, download_name=f'{title}.txt',
                        mimetype='text/plain; charset=utf-8')
    elif export_format == 'docx':
        filepath = exporter.export_docx(title, full_content, characters, plot, export_dir)
        return send_file(filepath, as_attachment=True, download_name=f'{title}.docx')
    elif export_format == 'pdf':
        filepath = exporter.export_pdf(title, full_content, characters, plot, export_dir)
        return send_file(filepath, as_attachment=True, download_name=f'{title}.pdf')
    else:
        return jsonify({'success': False, 'error': f'不支持的格式: {export_format}'}), 400


# ==================== 认证 API ====================

@app.route('/api/auth/register', methods=['POST'])
def auth_register():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    success, msg = user_manager.register(username, password)
    if success:
        session['username'] = username.lower()
        session.permanent = True
        user = user_manager.get_user(username)
        return jsonify({'success': True, 'message': msg,
                        'user': {'username': username, 'is_admin': user['is_admin']}})
    return jsonify({'success': False, 'error': msg}), 400


@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    success, result = user_manager.login(username, password)
    if success:
        session['username'] = username.lower()
        session.permanent = True
        return jsonify({'success': True,
                        'user': {'username': username, 'is_admin': result['is_admin']}})
    return jsonify({'success': False, 'error': result}), 401


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    session.clear()
    return jsonify({'success': True})


@app.route('/api/auth/me', methods=['GET'])
def auth_me():
    if 'username' not in session:
        return jsonify({'success': False, 'code': 'NOT_LOGGED_IN'}), 401
    user = user_manager.get_user(session['username'])
    if not user:
        session.clear()
        return jsonify({'success': False, 'code': 'NOT_LOGGED_IN'}), 401
    return jsonify({'success': True,
                    'user': {'username': session['username'], 'is_admin': user['is_admin']}})


# ==================== 管理员 API ====================

@app.route('/api/admin/novels', methods=['GET'])
@admin_required
def admin_list_all_novels():
    all_novels = []
    base = BASE_DATA_DIR
    if os.path.exists(base):
        for username in os.listdir(base):
            user_dir = os.path.join(base, username)
            if not os.path.isdir(user_dir):
                continue
            nm = NovelManager(user_dir)
            novels = nm.list_novels()
            for n in novels:
                n['owner'] = username
                all_novels.append(n)
    all_novels.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
    return jsonify({'success': True, 'novels': all_novels})


@app.route('/api/admin/novels/<owner>/<novel_id>', methods=['DELETE'])
@admin_required
def admin_delete_novel(owner, novel_id):
    user_dir = os.path.join(BASE_DATA_DIR, owner)
    if not os.path.exists(user_dir):
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    nm = NovelManager(user_dir)
    if nm.delete_novel(novel_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '小说不存在'}), 404


@app.route('/api/admin/novels/<owner>/<novel_id>', methods=['GET'])
@admin_required
def admin_get_novel_content(owner, novel_id):
    user_dir = os.path.join(BASE_DATA_DIR, owner)
    if not os.path.exists(user_dir):
        return jsonify({'success': False, 'error': '用户不存在'}), 404
    nm = NovelManager(user_dir)
    novel = nm.get_novel(novel_id)
    if not novel:
        return jsonify({'success': False, 'error': '小说不存在'}), 404
    content = nm.get_content(novel_id)
    return jsonify({'success': True, 'novel': novel, 'content': content})


# ==================== 页面路由 ====================

@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
