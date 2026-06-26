"""
AI小说写作助手 (轻量版) - AI通信模块
"""
from openai import OpenAI


SYSTEM_PROMPT = """你是一个专业的小说写作助手。你的任务是帮助用户创作小说。

## 你的能力
1. **角色设定**：帮助用户设计和完善小说角色（姓名、性格、背景、外貌等）
2. **情节构思**：帮助用户构建故事大纲、章节划分、情节发展
3. **内容写作**：根据角色和情节设定写出小说正文
4. **续写**：在已有内容基础上继续写作
5. **修改润色**：根据用户要求修改、润色、改写特定内容，包括删除段落

## 重要规则

### 关于角色
- 如果用户没有提供角色信息，主动建议适合故事的角色
- 当你给出角色建议时，必须使用以下标签格式：
  【角色建议】
  [
    {"name": "角色名", "role": "身份/职业", "personality": "性格特征", "appearance": "外貌描述", "description": "补充说明"}
  ]
  【/角色建议】
- 注意：角色建议必须是合法的JSON数组格式
- 在用户确认角色之前，不要开始正式写作

### 关于情节
- 如果用户没有提供情节大纲，可以先和用户讨论故事方向，然后给出建议
- 当你给出情节建议时，必须使用以下标签格式：
  【情节建议】
  情节大纲内容...
  【/情节建议】
- 在用户确认情节之前，不要开始正式写作

### 写作格式（极其重要，必须严格遵守）

你有三种内容标签。用错会导致作者丢失全文。

#### 【小说内容】—— 新写或续写
**作用**：把新内容追加到全文末尾，不影响已有内容。
**何时用**：开始新章节、续写下一段、新增场景。

#### 【替换内容】—— 重写整篇文章
**作用**：彻底替换全文，标签内必须包含新的完整全文。
**何时用**：仅当作者明确要求"重写全文"时。
**⚠️ 绝不要在【替换内容】里只放修改的那一小段！** 那样会导致全文被替换成一小段。
**不确定用哪个 → 用【小说内容】。追加永远安全。**

#### 角色/情节建议
- 角色：**【角色建议】** JSON数组 **【/角色建议】**
- 情节：**【情节建议】** 内容 **【/情节建议】**
- 正文之外不要使用内容标签

### 交流风格
- 用中文交流
- 热情、专业、有创造力
- 当用户提出修改意见时，认真理解并执行
- 如果用户的要求会影响故事逻辑，友善地指出并提供替代方案

### 续写要求
- 续写时保持与前文一致的风格、人称、时态
- 确保情节连贯，不出现矛盾
- 在前文基础上自然推进故事发展
"""


class AIClient:
    """API客户端（兼容OpenAI格式）"""

    def __init__(self):
        self.client = None
        self.model = 'deepseek-chat'
        self.temperature = 0.8
        self.max_tokens = 4096

    def configure(self, api_key, base_url='https://api.deepseek.com/v1', model='deepseek-chat',
                  temperature=0.8, max_tokens=4096):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _build_context_prompt(self, context):
        parts = []
        if context.get('title'):
            parts.append(f"当前小说：《{context['title']}》")
        if context.get('characters'):
            parts.append("\n已确认的角色设定：")
            for char in context['characters']:
                if isinstance(char, dict):
                    name = char.get('name', '未知')
                    desc = char.get('description', '')
                    role = char.get('role', '')
                    personality = char.get('personality', '')
                    appearance = char.get('appearance', '')
                    parts.append(f"- {name}")
                    if role: parts.append(f"  身份：{role}")
                    if personality: parts.append(f"  性格：{personality}")
                    if appearance: parts.append(f"  外貌：{appearance}")
                    if desc: parts.append(f"  描述：{desc}")
                else:
                    parts.append(f"- {char}")
        if context.get('plot'):
            parts.append(f"\n情节大纲：\n{context['plot']}")
        if context.get('content'):
            content = context['content']
            if len(content) > 2000:
                content = '...（前文省略）...\n' + content[-2000:]
            parts.append(f"\n已有内容：\n{content}")
        return '\n'.join(parts) if parts else ''

    def _build_messages(self, user_message, context, history, is_continuation=False):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        context_prompt = self._build_context_prompt(context)
        if context_prompt:
            messages.append({"role": "system", "content": f"以下是当前小说的背景信息：\n\n{context_prompt}"})
        if is_continuation:
            messages.append({"role": "system", "content": "你现在处于续写模式。请根据已有内容和用户的续写要求，用【小说内容】...【/小说内容】标签写出新的内容。保持风格一致，情节连贯。"})
        for entry in history[-10:]:
            messages.append({"role": "user", "content": entry.get('user', '')})
            messages.append({"role": "assistant", "content": entry.get('assistant', '')})
        messages.append({"role": "user", "content": user_message})
        return messages

    def chat_stream(self, user_message, context=None, history=None, is_continuation=False):
        if context is None: context = {}
        if history is None: history = []
        messages = self._build_messages(user_message, context, history, is_continuation)
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages,
                temperature=self.temperature, max_tokens=self.max_tokens, stream=True
            )
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            error_msg = str(e)
            if 'api_key' in error_msg.lower() or 'authentication' in error_msg.lower():
                yield f"\n❌ API Key 错误，请检查您的API Key是否正确配置。\n错误详情：{error_msg}"
            elif 'rate' in error_msg.lower():
                yield f"\n⏳ API请求频率过高，请稍后重试。\n错误详情：{error_msg}"
            elif 'timeout' in error_msg.lower():
                yield f"\n⏱️ 请求超时，请检查网络连接后重试。\n错误详情：{error_msg}"
            else:
                yield f"\n❌ 请求出错：{error_msg}"
