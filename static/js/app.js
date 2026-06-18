/**
 * App.js - 主应用逻辑
 * 初始化、主题切换、字体背景、设置面板
 */

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadAllSettings();
    initSidebar();
    initCloseHandlers();
    loadNovelList();
    cacheSystemPrompt();
    console.log('📖 AI小说写作助手已就绪');
});

// ==================== 认证检查 ====================

let currentUser = null;

async function checkAuth() {
    try {
        const r = await fetch('/api/auth/me');
        if (r.status === 401) {
            window.location.href = '/login';
            return;
        }
        const d = await r.json();
        if (d.success) {
            currentUser = d.user;
            document.getElementById('userInfo').textContent = currentUser.username;
            if (currentUser.is_admin) {
                document.getElementById('adminBtn').style.display = 'inline-flex';
            }
        }
    } catch (e) {
        console.error('Auth check failed');
    }
}

async function doLogout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/login';
}

// ==================== 管理面板 ====================

async function openAdminPanel() {
    document.getElementById('adminModal').classList.add('active');
    await loadAdminNovels();
}

function closeAdminPanel() {
    document.getElementById('adminModal').classList.remove('active');
}

async function loadAdminNovels() {
    const container = document.getElementById('adminNovelList');
    container.innerHTML = '<div class="empty-hint">加载中...</div>';

    try {
        const r = await fetch('/api/admin/novels');
        const d = await r.json();
        if (!d.success) {
            container.innerHTML = '<div class="empty-hint">加载失败</div>';
            return;
        }

        if (!d.novels.length) {
            container.innerHTML = '<div class="empty-hint">暂无小说</div>';
            return;
        }

        container.innerHTML = d.novels.map(n => `
            <div style="background:var(--bg-input);border-radius:8px;padding:12px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <strong>${escapeHtml(n.title)}</strong>
                    <span style="color:var(--text-muted);font-size:11px;margin-left:8px;">by ${escapeHtml(n.owner)}</span>
                    <div style="font-size:11px;color:var(--text-muted);margin-top:2px;">${n.word_count || 0} 字 · ${formatDate(n.updated_at)}</div>
                </div>
                <div style="display:flex;gap:6px;">
                    <button class="btn btn-sm btn-outline" onclick="adminViewNovel('${n.owner}','${n.id}')">查看</button>
                    <button class="btn btn-sm btn-outline" style="border-color:var(--danger);color:var(--danger);" onclick="adminDeleteNovel('${n.owner}','${n.id}')">删除</button>
                </div>
            </div>
        `).join('');
    } catch (e) {
        container.innerHTML = '<div class="empty-hint">加载失败</div>';
    }
}

async function adminViewNovel(owner, novelId) {
    try {
        const r = await fetch(`/api/admin/novels/${owner}/${novelId}`);
        const d = await r.json();
        if (d.success) {
            const content = d.content || '(暂无内容)';
            alert(`《${d.novel.title}》by ${owner}\n\n${content.slice(0, 500)}${content.length > 500 ? '...' : ''}`);
        }
    } catch (e) {
        alert('查看失败');
    }
}

async function adminDeleteNovel(owner, novelId) {
    if (!confirm(`确定删除 ${owner} 的小说吗？此操作不可撤销！`)) return;

    try {
        const r = await fetch(`/api/admin/novels/${owner}/${novelId}`, { method: 'DELETE' });
        const d = await r.json();
        if (d.success) {
            showToast('✅ 已删除');
            await loadAdminNovels();
        } else {
            showToast('❌ ' + (d.error || '删除失败'));
        }
    } catch (e) {
        showToast('❌ 删除失败');
    }
}

// 预加载系统提示词到缓存，debug面板用
function cacheSystemPrompt() {
    fetch('/api/system-prompt')
        .then(r => r.json())
        .then(d => { if (d.success) window._cachedSystemPrompt = d.prompt; })
        .catch(() => {});
}

// ==================== 设置加载/保存 ====================

function loadAllSettings() {
    // 主题
    const theme = localStorage.getItem('xs_theme') || 'dark';
    applyTheme(theme);

    // API设置
    const provider = localStorage.getItem('xs_provider') || 'deepseek';
    const apiKey = localStorage.getItem('xs_api_key');
    const apiBase = localStorage.getItem('xs_api_base') || 'https://api.deepseek.com/v1';
    const model = localStorage.getItem('xs_model') || 'deepseek-chat';

    document.getElementById('apiProvider').value = provider;
    if (apiKey) document.getElementById('apiKey').value = apiKey;
    document.getElementById('apiBase').value = apiBase;

    // 根据保存的provider更新模型选项
    onProviderChange(true);
    document.getElementById('modelSelect').value = model;

    // 写作设置
    const temperature = localStorage.getItem('xs_temperature') || '0.8';
    const maxTokens = localStorage.getItem('xs_max_tokens') || '4096';
    document.getElementById('temperature').value = temperature;
    document.getElementById('maxTokens').value = maxTokens;
    document.getElementById('tempValue').textContent = temperature;

    document.getElementById('temperature').addEventListener('input', function() {
        document.getElementById('tempValue').textContent = this.value;
    });

    // 字体
    const fontFamily = localStorage.getItem('xs_font');
    if (fontFamily) {
        document.documentElement.style.setProperty('--font-content', fontFamily);
    }
    updateFontPresetActive(fontFamily);

    // 背景色
    const bgColor = localStorage.getItem('xs_bg_color');
    if (bgColor) {
        document.documentElement.style.setProperty('--bg-primary', bgColor);
        document.documentElement.style.setProperty('--bg-body', bgColor);
    }

    // 背景图
    const bgImage = localStorage.getItem('xs_bg_image');
    if (bgImage) {
        applyBackgroundImage(bgImage);
    }
}

function saveAllSettingsToStorage() {
    localStorage.setItem('xs_provider', document.getElementById('apiProvider').value);
    localStorage.setItem('xs_api_key', document.getElementById('apiKey').value.trim());
    localStorage.setItem('xs_api_base', document.getElementById('apiBase').value.trim());
    localStorage.setItem('xs_model', document.getElementById('modelSelect').value);
    localStorage.setItem('xs_temperature', document.getElementById('temperature').value);
    localStorage.setItem('xs_max_tokens', document.getElementById('maxTokens').value);

    document.getElementById('sendBtn').disabled = !currentNovelId;

    showToast('✅ 设置已保存');
}

// ==================== API服务商切换 ====================

function onProviderChange(isInit) {
    const sel = document.getElementById('apiProvider');
    const option = sel.options[sel.selectedIndex];
    const provider = sel.value;

    if (provider === 'custom') {
        document.getElementById('apiBaseGroup').style.display = 'block';
        if (!isInit) {
            document.getElementById('apiBase').value = '';
            document.getElementById('modelSelect').innerHTML = '<option value="">请手动输入模型名</option>';
        }
        return;
    }

    // 预设服务商：自动填充base URL和模型列表
    const base = option.dataset.base;
    const models = option.dataset.models.split(',');

    document.getElementById('apiBaseGroup').style.display = 'block';
    if (!isInit) {
        document.getElementById('apiBase').value = base;
    }

    const modelNames = {
        'deepseek-chat': 'DeepSeek V3',
        'deepseek-reasoner': 'DeepSeek R1 (推理)',
        'gpt-4o': 'GPT-4o (推荐)',
        'gpt-4-turbo': 'GPT-4 Turbo',
        'gpt-4': 'GPT-4',
    };

    document.getElementById('modelSelect').innerHTML = models.map(m =>
        `<option value="${m}">${modelNames[m] || m}</option>`
    ).join('');

    if (!isInit) {
        document.getElementById('modelSelect').value = option.dataset.model;
    }
}

// ==================== 主题切换 ====================

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('xs_theme', theme);

    const icon = document.getElementById('themeIcon');
    if (icon) icon.textContent = theme === 'dark' ? '🌙' : '☀️';

    // 更新主题按钮状态
    const darkBtn = document.getElementById('themeDark');
    const lightBtn = document.getElementById('themeLight');
    if (darkBtn) darkBtn.classList.toggle('active', theme === 'dark');
    if (lightBtn) lightBtn.classList.toggle('active', theme === 'light');
}

function setTheme(theme, btn) {
    applyTheme(theme);
    // 更新按钮active状态
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
}

// ==================== 字体 ====================

document.addEventListener('click', function(e) {
    const fontBtn = e.target.closest('.font-preset');
    if (!fontBtn) return;

    const fontFamily = fontBtn.dataset.font;
    document.documentElement.style.setProperty('--font-content', fontFamily);
    localStorage.setItem('xs_font', fontFamily);
    updateFontPresetActive(fontFamily);
    showToast('✅ 字体已更新');
});

function updateFontPresetActive(fontFamily) {
    document.querySelectorAll('.font-preset').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.font === fontFamily);
    });
}

// ==================== 背景 ====================

document.addEventListener('click', function(e) {
    const colorBtn = e.target.closest('#bgColorPresets .color-preset');
    if (!colorBtn) return;

    const bgColor = colorBtn.dataset.bg;
    document.querySelectorAll('#bgColorPresets .color-preset').forEach(b => b.classList.remove('active'));
    colorBtn.classList.add('active');

    if (bgColor) {
        document.documentElement.style.setProperty('--bg-primary', bgColor);
        document.documentElement.style.setProperty('--bg-body', bgColor);
        localStorage.setItem('xs_bg_color', bgColor);
    } else {
        // 默认背景
        document.documentElement.style.removeProperty('--bg-primary');
        document.documentElement.style.removeProperty('--bg-body');
        localStorage.removeItem('xs_bg_color');
    }
});

function applyBgImage() {
    const url = document.getElementById('bgImageUrl').value.trim();
    if (!url) return;
    applyBackgroundImage(url);
    localStorage.setItem('xs_bg_image', url);
    showToast('✅ 背景图已应用');
}

function clearBgImage() {
    document.documentElement.style.setProperty('--bg-body-overlay', 'none');
    localStorage.removeItem('xs_bg_image');
    document.getElementById('bgImageUrl').value = '';
    showToast('✅ 背景图已清除');
}

function applyBackgroundImage(url) {
    document.documentElement.style.setProperty(
        '--bg-body-overlay',
        `url(${url})`
    );
}

// ==================== 设置面板 ====================

function openSettings() {
    document.getElementById('settingsModal').classList.add('active');
    // 刷新API key显示
    const apiKey = localStorage.getItem('xs_api_key');
    if (apiKey) document.getElementById('apiKey').value = apiKey;

    // 重置到第一个tab
    switchSettingsTab('api');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function saveSettings() {
    saveAllSettingsToStorage();
    closeSettings();
}

function switchSettingsTab(tab) {
    document.querySelectorAll('.stab').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.settings-panel').forEach(p => p.style.display = 'none');

    const tabMap = { api: 'settingsApi', appearance: 'settingsAppearance', writing: 'settingsWriting' };
    const tabBtn = document.querySelector(`.stab[onclick*="${tab}"]`);
    const panel = document.getElementById(tabMap[tab]);

    if (tabBtn) tabBtn.classList.add('active');
    if (panel) panel.style.display = 'block';
}

// ==================== 侧边栏 ====================

function initSidebar() {
    document.getElementById('sidebarToggle').addEventListener('click', function() {
        document.getElementById('sidebar').classList.toggle('collapsed');
    });
}

// ==================== 弹窗关闭 ====================

function initCloseHandlers() {
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) overlay.classList.remove('active');
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(o => {
                if (o.id !== 'confirmModal') o.classList.remove('active');
            });
        }
    });
}

// ==================== Toast ====================

function showToast(message) {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 2200);
}

// ==================== 提示词调试 ====================

function showPromptDebug() {
    const last = window._lastPromptInfo;
    if (!last) {
        showToast('⚠️ 还没有发送过消息，请先和AI对话');
        return;
    }

    document.getElementById('debugSystem').value = last.systemPrompt || '(未加载)';
    document.getElementById('debugContext').value = last.context || '(无上下文)';
    document.getElementById('debugPrefix').value = last.prefix || '(无前缀)';
    document.getElementById('debugUserMsg').value = last.userMessage || '(无消息)';

    document.getElementById('debugModal').classList.add('active');
}

function closeDebug() {
    document.getElementById('debugModal').classList.remove('active');
}

// ==================== 离开提醒 ====================

window.addEventListener('beforeunload', function(e) {
    if (isEditing) {
        e.preventDefault();
        e.returnValue = '你有未保存的编辑，确定离开吗？';
        return e.returnValue;
    }
});
