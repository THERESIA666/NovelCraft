"""
AI小说写作助手 - 小说项目管理模块
"""
import os
import json
import uuid
import shutil
from datetime import datetime


class NovelManager:
    """管理小说项目的创建、读取、更新、删除"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def _get_novel_dir(self, novel_id):
        """获取小说项目目录"""
        return os.path.join(self.data_dir, novel_id)

    def _ensure_novel_dir(self, novel_id):
        """确保小说目录存在"""
        novel_dir = self._get_novel_dir(novel_id)
        os.makedirs(novel_dir, exist_ok=True)
        return novel_dir

    def list_novels(self):
        """列出所有小说"""
        novels = []
        if not os.path.exists(self.data_dir):
            return novels

        for novel_id in os.listdir(self.data_dir):
            meta_path = os.path.join(self.data_dir, novel_id, 'meta.json')
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                    # 确保meta中有id
                    meta['id'] = novel_id
                    # 获取内容长度
                    content_path = os.path.join(self.data_dir, novel_id, 'content.txt')
                    if os.path.exists(content_path):
                        with open(content_path, 'r', encoding='utf-8') as f:
                            meta['word_count'] = len(f.read())
                    else:
                        meta['word_count'] = 0
                    novels.append(meta)
                except (json.JSONDecodeError, IOError):
                    continue

        # 按更新时间倒序排列
        novels.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        return novels

    def create_novel(self, title='未命名小说', characters=None, plot=''):
        """创建新小说"""
        novel_id = str(uuid.uuid4())[:8]
        novel_dir = self._ensure_novel_dir(novel_id)

        novel = {
            'id': novel_id,
            'title': title,
            'characters': characters or [],
            'plot': plot,
            'new_content': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # 保存元数据
        meta_path = os.path.join(novel_dir, 'meta.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(novel, f, ensure_ascii=False, indent=2)

        # 创建空内容文件
        content_path = os.path.join(novel_dir, 'content.txt')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write('')

        # 创建空历史文件
        history_path = os.path.join(novel_dir, 'history.json')
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)

        return novel

    def get_novel(self, novel_id):
        """获取小说详情"""
        meta_path = os.path.join(self.data_dir, novel_id, 'meta.json')
        if not os.path.exists(meta_path):
            return None

        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                novel = json.load(f)
            novel['id'] = novel_id
            return novel
        except (json.JSONDecodeError, IOError):
            return None

    def save_novel(self, novel_id, novel_data):
        """保存小说元数据"""
        novel_dir = self._ensure_novel_dir(novel_id)
        novel_data['updated_at'] = datetime.now().isoformat()

        meta_path = os.path.join(novel_dir, 'meta.json')
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(novel_data, f, ensure_ascii=False, indent=2)

    def delete_novel(self, novel_id):
        """删除小说"""
        novel_dir = self._get_novel_dir(novel_id)
        if os.path.exists(novel_dir):
            shutil.rmtree(novel_dir)
            return True
        return False

    def get_content(self, novel_id):
        """获取小说完整内容"""
        content_path = os.path.join(self.data_dir, novel_id, 'content.txt')
        if os.path.exists(content_path):
            try:
                with open(content_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except IOError:
                return ''
        return ''

    def save_content(self, novel_id, content):
        """保存小说内容"""
        novel_dir = self._ensure_novel_dir(novel_id)
        content_path = os.path.join(novel_dir, 'content.txt')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_history(self, novel_id):
        """获取对话历史"""
        if not novel_id:
            return []

        history_path = os.path.join(self.data_dir, novel_id, 'history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def add_history(self, novel_id, user_message, assistant_response):
        """添加一条对话历史"""
        if not novel_id:
            return

        history_path = os.path.join(self.data_dir, novel_id, 'history.json')
        history = self.get_history(novel_id)

        history.append({
            'user': user_message,
            'assistant': assistant_response,
            'timestamp': datetime.now().isoformat()
        })

        novel_dir = self._ensure_novel_dir(novel_id)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def clear_history(self, novel_id):
        """清空对话历史"""
        if not novel_id:
            return

        history_path = os.path.join(self.data_dir, novel_id, 'history.json')
        novel_dir = self._ensure_novel_dir(novel_id)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False)
