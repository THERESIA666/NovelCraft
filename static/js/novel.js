/**
 * Novel.js - 小说项目管理
 * 负责小说列表、创建、选择、删除等操作
 */

// ==================== 状态 ====================
let currentNovelId = null;
let currentNovel = null;

// ==================== API调用 ====================

async function apiCall(method, url, body = null) {
    const opts = {
        method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);

    const resp = await fetch(url, opts);
    return resp.json();
}

// ==================== 小说列表 ====================

async function loadNovelList() {
    try {
        const data = await apiCall('GET', '/api/novels');
        if (data.success) {
            renderNovelList(data.novels);
        }
    } catch (e) {
        console.error('加载小说列表失败:', e);
    }
}

function renderNovelList(novels) {
    const container = document.getElementById('novelList');
    if (!novels.length) {
        container.innerHTML = '<div class="empty-hint">暂无小说，点击上方按钮创建</div>';
        return;
    }

    container.innerHTML = novels.map(n => `
        <div class="novel-list-item ${n.id === currentNovelId ? 'active' : ''}" onclick="selectNovel('${n.id}')">
            <div class="novel-title">${escapeHtml(n.title)}</div>
            <div class="novel-meta">
                <span>${n.word_count || 0} 字</span>
                <span>${formatDate(n.updated_at)}</span>
            </div>
            <div class="novel-actions-mini">
                <button onclick="event.stopPropagation(); deleteNovelConfirm('${n.id}')" title="删除">🗑️</button>
            </div>
        </div>
    `).join('');
}

// ==================== 小说选择和切换 ====================

async function selectNovel(novelId) {
    try {
        const data = await apiCall('GET', `/api/novels/${novelId}`);
        if (!data.success) {
            alert('加载小说失败: ' + data.error);
            return;
        }

        currentNovelId = novelId;
        currentNovel = data.novel;

        // 更新UI
        document.getElementById('currentNovelTitle').textContent = currentNovel.title;
        document.getElementById('exportBtn').disabled = false;
        document.getElementById('continueBtn').disabled = false;
        document.getElementById('genCharBtn').disabled = false;
        document.getElementById('genPlotBtn').disabled = false;
        document.getElementById('autoContinueBtn').disabled = false;
        document.getElementById('sendBtn').disabled = false;

        // 显示侧边栏信息
        document.getElementById('charSection').style.display = 'block';
        document.getElementById('plotSection').style.display = 'block';
        renderCharacters(currentNovel.characters || []);
        renderPlot(currentNovel.plot || '');

        // 加载内容
        await loadContent();
        // 加载对话历史
        await loadHistory();
        // 刷新列表高亮
        await loadNovelList();

        // 更新对话提示
        updateChatPlaceholder();

    } catch (e) {
        console.error('选择小说失败:', e);
    }
}

function updateChatPlaceholder() {
    const input = document.getElementById('chatInput');
    if (currentNovelId && currentNovel) {
        input.placeholder = `和AI讨论《${currentNovel.title}》...`;
    } else {
        input.placeholder = '请先创建或选择一部小说...';
    }
}

// ==================== 新建小说 ====================

function openNewNovel() {
    document.getElementById('newNovelModal').classList.add('active');
    document.getElementById('novelTitle').focus();
}

function closeNewNovel() {
    document.getElementById('newNovelModal').classList.remove('active');
    document.getElementById('novelTitle').value = '';
    document.getElementById('novelCharacters').value = '';
    document.getElementById('novelPlot').value = '';
}

async function createNovel() {
    const title = document.getElementById('novelTitle').value.trim() || '未命名小说';
    const charactersText = document.getElementById('novelCharacters').value.trim();
    const plot = document.getElementById('novelPlot').value.trim();

    // 解析角色文本
    let characters = [];
    if (charactersText) {
        // 简单解析：每行一个角色，格式 "名字：描述"
        characters = charactersText.split('\n').filter(line => line.trim()).map(line => {
            const colonIndex = line.indexOf('：');
            if (colonIndex === -1) return { name: line.trim(), description: '' };
            return {
                name: line.substring(0, colonIndex).trim(),
                description: line.substring(colonIndex + 1).trim()
            };
        });
    }

    try {
        const data = await apiCall('POST', '/api/novels', { title, characters, plot });
        if (data.success) {
            closeNewNovel();
            await loadNovelList();
            await selectNovel(data.novel.id);

            // 如果没有角色，提示AI建议
            if (!characters.length) {
                addWelcomeMessage();
            }
        } else {
            alert('创建失败: ' + data.error);
        }
    } catch (e) {
        console.error('创建小说失败:', e);
        alert('创建小说失败，请重试');
    }
}

function addWelcomeMessage() {
    const container = document.getElementById('chatMessages');
    // 清空欢迎消息
    const welcome = container.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message assistant';
    msgDiv.innerHTML = `
        <div class="message-label">🤖 AI助手</div>
        <div class="message-content">我注意到你还没有设定角色和情节。需要我帮你构思吗？你可以告诉我：
<br><br>• 你想写什么类型的故事？（玄幻、言情、悬疑、科幻...）
<br>• 有没有大致的想法或灵感？
<br><br>或者直接说"帮我设计角色"，我来为你推荐！</div>
    `;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

// ==================== 删除小说 ====================

function deleteNovelConfirm(novelId) {
    if (!confirm('确定要删除这部小说吗？此操作不可撤销！')) return;

    apiCall('DELETE', `/api/novels/${novelId}`).then(data => {
        if (data.success) {
            if (currentNovelId === novelId) {
                currentNovelId = null;
                currentNovel = null;
                document.getElementById('currentNovelTitle').textContent = '未选择小说';
                document.getElementById('exportBtn').disabled = true;
                document.getElementById('continueBtn').disabled = true;
                document.getElementById('sendBtn').disabled = true;
                document.getElementById('charSection').style.display = 'none';
                document.getElementById('plotSection').style.display = 'none';
                document.getElementById('novelContent').innerHTML = '<div class="empty-hint">选择一部小说以查看内容</div>';
                document.getElementById('novelActions').style.display = 'none';
                document.getElementById('chatMessages').innerHTML = `
                    <div class="welcome-message">
                        <div class="welcome-icon">📖</div>
                        <h2>欢迎使用AI小说写作助手</h2>
                        <p>请先创建一部小说或选择已有小说开始写作。</p>
                    </div>`;
            }
            loadNovelList();
        }
    });
}

// ==================== 角色管理 ====================

function renderCharacters(characters) {
    const container = document.getElementById('characterList');
    if (!characters.length) {
        container.innerHTML = '<div class="empty-hint" style="padding:10px;font-size:12px;">暂无角色</div>';
        return;
    }

    container.innerHTML = characters.map(c => {
        const name = typeof c === 'string' ? c : (c.name || '未知');
        const desc = typeof c === 'string' ? '' : (c.description || c.role || c.personality || '');
        return `<div class="character-item">
            <div class="char-name">${escapeHtml(name)}</div>
            ${desc ? `<div class="char-desc">${escapeHtml(desc)}</div>` : ''}
        </div>`;
    }).join('');
}

// ==================== 角色/情节编辑弹窗 ====================

let charPlotEditMode = ''; // 'characters' | 'plot'

function editCharacters() {
    if (!currentNovelId) return;
    charPlotEditMode = 'characters';

    const current = currentNovel?.characters || [];
    const text = current.map(c => {
        if (typeof c === 'string') return c;
        const parts = [c.name || ''];
        if (c.description) parts.push(c.description);
        if (c.role) parts.push('身份：' + c.role);
        if (c.personality) parts.push('性格：' + c.personality);
        if (c.appearance) parts.push('外貌：' + c.appearance);
        return parts.join('：');
    }).join('\n');

    document.getElementById('editCpTitle').textContent = '👥 编辑角色';
    document.getElementById('editCpBody').innerHTML = `
        <div class="form-group">
            <label>角色列表（每行一个，格式：名字：描述）</label>
            <textarea id="editCpText" rows="10" placeholder="张三：主角，年轻侠客&#10;李四：神秘剑客，性格冷酷&#10;（可以包含：身份/性格/外貌等描述）"></textarea>
            <small>每行一个角色。AI建议的角色也会出现在这里供你修改。</small>
        </div>
    `;
    document.getElementById('editCpText').value = text;
    document.getElementById('editCharPlotModal').classList.add('active');
}

function editPlot() {
    if (!currentNovelId) return;
    charPlotEditMode = 'plot';

    const current = currentNovel?.plot || '';
    document.getElementById('editCpTitle').textContent = '📋 编辑情节大纲';
    document.getElementById('editCpBody').innerHTML = `
        <div class="form-group">
            <label>情节大纲</label>
            <textarea id="editCpText" rows="10" placeholder="描述故事的整体走向、主要冲突、章节安排等..."></textarea>
            <small>可以详细也可以简略，AI会根据大纲来规划写作方向。</small>
        </div>
    `;
    document.getElementById('editCpText').value = current;
    document.getElementById('editCharPlotModal').classList.add('active');
}

function closeCharPlotEdit() {
    document.getElementById('editCharPlotModal').classList.remove('active');
    charPlotEditMode = '';
}

async function saveCharPlotEdit() {
    const text = document.getElementById('editCpText').value;

    if (charPlotEditMode === 'characters') {
        const characters = text.split('\n').filter(line => line.trim()).map(line => {
            const colonIndex = line.indexOf('：');
            if (colonIndex === -1) return { name: line.trim(), description: '' };
            return {
                name: line.substring(0, colonIndex).trim(),
                description: line.substring(colonIndex + 1).trim()
            };
        });

        const data = await apiCall('POST', `/api/novels/${currentNovelId}/characters`, { characters });
        if (data.success) {
            currentNovel.characters = characters;
            renderCharacters(characters);
            showToast('✅ 角色已更新');
        }
    } else if (charPlotEditMode === 'plot') {
        const data = await apiCall('POST', `/api/novels/${currentNovelId}/plot`, { plot: text });
        if (data.success) {
            currentNovel.plot = text;
            renderPlot(text);
            showToast('✅ 情节大纲已更新');
        }
    }

    closeCharPlotEdit();
}

// ==================== 情节大纲管理 ====================

function renderPlot(plot) {
    const container = document.getElementById('plotSummary');
    if (!plot) {
        container.innerHTML = '<div class="empty-hint" style="padding:10px;font-size:12px;">暂无大纲</div>';
        return;
    }
    container.textContent = plot;
}

// ==================== 工具函数 ====================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoStr) {
    if (!isoStr) return '';
    try {
        const d = new Date(isoStr);
        const now = new Date();
        const diff = now - d;
        if (diff < 60000) return '刚刚';
        if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前';
        if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前';
        return d.toLocaleDateString('zh-CN');
    } catch {
        return '';
    }
}
