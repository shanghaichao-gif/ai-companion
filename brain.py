"""AI 陪伴助手 PWA - 核心大脑"""
import json
from openai import OpenAI


class Brain:
    def __init__(self, config: dict):
        self.config = config
        self.client = OpenAI(
            api_key=config["llm"]["api_key"],
            base_url=config["llm"]["base_url"],
        )
        self.model = config["llm"]["model"]
        self.temperature = config["llm"]["temperature"]
        self.max_tokens = config["llm"]["max_tokens"]
        self.system_prompt = config["personality"]["system_prompt"].format(
            name=config["personality"]["name"],
            style=config["personality"]["style"],
            catchphrase=config["personality"]["catchphrase"],
        )

    def chat(self, messages: list[dict], user_profile: str = "", long_term_memory: str = "") -> str:
        system_content = self.system_prompt
        if user_profile:
            system_content += f"\n\n【用户画像】\n{user_profile}"
        if long_term_memory:
            system_content += f"\n\n【关于用户的重要记忆】\n{long_term_memory}"

        full_messages = [{"role": "system", "content": system_content}] + messages
        response = self.client.chat.completions.create(
            model=self.model, messages=full_messages,
            temperature=self.temperature, max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content.strip()

    def autonomous_think(self, messages: list[dict], user_profile: str = "", long_term_memory: str = "") -> dict:
        think_prompt = self.system_prompt + "\n\n你现在处于自主思考模式。根据用户画像、记忆和最近对话，判断是否需要主动做什么。"
        if user_profile:
            think_prompt += f"\n\n【用户画像】\n{user_profile}"
        if long_term_memory:
            think_prompt += f"\n\n【关于用户的重要记忆】\n{long_term_memory}"

        think_prompt += """
\n\n请用JSON格式回复（不要markdown代码块）：
{"should_act": true/false, "action_type": "greet/remind/comfort/chat/none", "reason": "原因", "message": "要说的话"}

判断标准：
- 用户最近情绪低落 → comfort
- 到了用户通常忙碌/休息的时间 → greet
- 用户之前提过某个待办/约定 → remind
- 很久没互动 → chat
- 没有特别的事 → should_act=false
"""
        think_messages = [{"role": "system", "content": think_prompt}]
        if messages:
            think_messages += messages[-6:]

        response = self.client.chat.completions.create(
            model=self.model, messages=think_messages,
            temperature=0.3, max_tokens=512,
        )
        try:
            return json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError:
            return {"should_act": False, "action_type": "none", "reason": "解析失败", "message": ""}

    def extract_memory(self, text: str) -> list[str]:
        extract_prompt = f"""从以下用户说的话中提取值得长期记住的关键信息。
只提取事实性信息（偏好、习惯、重要事件、人际关系等），忽略闲聊废话。
每条一个要点，返回JSON数组。没有值得记住的返回空数组。

用户说：{text}

格式：["要点1", "要点2"]"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0.1, max_tokens=256,
        )
        try:
            return json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError:
            return []
