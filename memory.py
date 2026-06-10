"""AI 陪伴助手 PWA - 记忆系统"""
import json
import os
import time
from datetime import datetime


class Memory:
    def __init__(self, data_dir: str, config: dict):
        self.data_dir = data_dir
        self.config = config
        self.context_rounds = config["memory"]["context_rounds"]
        self.max_facts = config["memory"]["max_long_term_facts"]
        self.profile_path = os.path.join(data_dir, "user_profile.json")
        self.memory_path = os.path.join(data_dir, "long_term_memory.json")
        self.conv_dir = os.path.join(data_dir, "conversations")
        self.conversation: list[dict] = []
        self.user_profile: dict = self._load_json(self.profile_path, {
            "name": "", "habits": [], "preferences": [],
            "important_events": [], "relationships": [],
        })
        self.long_term: list[dict] = self._load_json(self.memory_path, [])
        self.last_proactive_time: float = 0

    def _load_json(self, path: str, default):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, path: str, data):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content, "timestamp": time.time()})

    def get_context_messages(self) -> list[dict]:
        recent = self.conversation[-(self.context_rounds * 2):]
        return [{"role": m["role"], "content": m["content"]} for m in recent]

    def add_facts(self, facts: list[str]):
        for fact in facts:
            existing = [f["text"] for f in self.long_term]
            if fact not in existing:
                self.long_term.append({"text": fact, "created_at": datetime.now().isoformat()})
        if len(self.long_term) > self.max_facts:
            self.long_term = self.long_term[-self.max_facts:]
        self._save_json(self.memory_path, self.long_term)

    def get_memory_summary(self) -> str:
        if not self.long_term: return ""
        return "\n".join([f"- {item['text']}" for item in self.long_term[-30:]])

    def get_profile_summary(self) -> str:
        parts, p = [], self.user_profile
        if p.get("name"): parts.append(f"名字：{p['name']}")
        if p.get("habits"): parts.append(f"习惯：{', '.join(p['habits'])}")
        if p.get("preferences"): parts.append(f"偏好：{', '.join(p['preferences'])}")
        if p.get("important_events"): parts.append(f"重要事件：{', '.join(p['important_events'])}")
        return "\n".join(parts)

    def update_profile(self, field: str, value):
        if field in self.user_profile:
            if isinstance(self.user_profile[field], list):
                if value not in self.user_profile[field]: self.user_profile[field].append(value)
            else:
                self.user_profile[field] = value
            self._save_json(self.profile_path, self.user_profile)

    def save_all(self):
        self._save_json(self.profile_path, self.user_profile)
        self._save_json(self.memory_path, self.long_term)
        if self.conversation:
            date_str = datetime.now().strftime("%Y-%m-%d")
            conv_file = os.path.join(self.conv_dir, f"{date_str}.json")
            existing = self._load_json(conv_file, [])
            existing.extend(self.conversation)
            self._save_json(conv_file, existing)
            self.conversation = []
