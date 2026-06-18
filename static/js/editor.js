/**
 * Editor.js - 小说内容展示和编辑模块
 * 负责内容加载、展示、编辑、标签页切换
 */

let currentTab = 'full'; // 'full' | 'new'
let isEditing = false;
let fullContent = '';
let newContent = '';

// ==================== 内容加载 ====================

async function loadContent() {
    if (!currentNovelId) return;

    try {
        const data = await apiCall('GET', `/api/novels/${currentNovelId}/content`);
        if (data.success) {
            fullContent = data.content || '';
            newContent = data.new_content || '';

            document.getElementById('novelActions').style.display = 'flex';
            renderContent();
        }
    } catch (e) {
        console.error('加载内容失败:', e);
    }
}

// ==================== 内容渲染 ====================

function renderContent() {
    const container = document.getElementById('novelContent');

    if (isEditing) {
        // 编辑模式
        const contentToEdit = currentTab === 'full' ? fullContent : newContent;
        container.innerHTML = `<textarea id="contentEditor">${escapeHtml(contentToEdit)}</textarea>`;
        container.classList.add('editing');
        document.getElementById('saveEditBtn').style.display = 'inline-flex';
        document.getElementById('cancelEditBtn').style.display = 'inline-flex';
        document.getElementById('editToggleBtn').style.display = 'none';
    } else {
        // 浏览模式
        const contentToShow = currentTab === 'full' ? fullContent : newContent;
        if (contentToShow) {
            container.innerHTML = formatNovelContent(contentToShow);
        } else {
            container.innerHTML = '<div class="empty-hint">' +
                (currentTab === 'full' ? '还没有内容，在左侧对话中让AI开始写作吧！' : '本次对话还没有新增内容') +
                '</div>';
        }
        container.classList.remove('editing');
        document.getElementById('saveEditBtn').style.display = 'none';
        document.getElementById('cancelEditBtn').style.display = 'none';
        document.getElementById('editToggleBtn').style.display = 'inline-flex';
        document.getElementById('editToggleBtn').textContent = '✏️ 编辑模式';
    }
}

function formatNovelContent(text) {
    // 将文本转换为格式化的HTML
    let html = escapeHtml(text);
    // 保留段落间距
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = '<p>' + html + '</p>';
    return html;
}

// ==================== 标签页切换 ====================

function switchTab(tab) {
    currentTab = tab;
    document.getElementById('tabFull').classList.toggle('active', tab === 'full');
    document.getElementById('tabNew').classList.toggle('active', tab === 'new');
    renderContent();
}

// ==================== 编辑模式 ====================

function toggleEditMode() {
    isEditing = true;
    renderContent();

    // 聚焦编辑器
    setTimeout(() => {
        const editor = document.getElementById('contentEditor');
        if (editor) editor.focus();
    }, 100);
}

function cancelEditMode() {
    isEditing = false;
    renderContent();
}

async function saveContentEdit() {
    const editor = document.getElementById('contentEditor');
    if (!editor) return;

    const newText = editor.value;

    try {
        // 根据当前标签更新对应内容
        if (currentTab === 'full') {
            await apiCall('PUT', `/api/novels/${currentNovelId}/content`, { content: newText });
            fullContent = newText;
        } else {
            // 更新新增内容
            await apiCall('PUT', `/api/novels/${currentNovelId}`, { new_content: newText });
            if (currentNovel) currentNovel.new_content = newText;
            newContent = newText;
        }
        isEditing = false;
        renderContent();
    } catch (e) {
        alert('保存失败: ' + e.message);
    }
}

// ==================== 导出 ====================

function openExport() {
    if (!currentNovelId) {
        alert('请先选择一部小说');
        return;
    }
    document.getElementById('exportModal').classList.add('active');
}

function closeExport() {
    document.getElementById('exportModal').classList.remove('active');
}

function exportNovel(format) {
    if (!currentNovelId) return;

    const url = `/api/novels/${currentNovelId}/export?format=${format}`;
    window.open(url, '_blank');
    closeExport();
}
