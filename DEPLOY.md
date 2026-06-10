# 🤖 小超 AI 陪伴助手 - iPhone 部署指南

## 📋 你需要准备

- 一个 LLM API Key（推荐 DeepSeek，便宜好用）
- 一个 GitHub 账号
- 一个 Render.com 账号（免费注册，用 GitHub 登录）

---

## 🚀 步骤一：获取 API Key（2分钟）

1. 打开 https://platform.deepseek.com/
2. 注册/登录
3. 点击「API Keys」→「创建 API Key」
4. 复制保存好（只显示一次！）

---

## 🚀 步骤二：上传到 GitHub（5分钟）

1. 打开 https://github.com/new 创建新仓库
   - 仓库名：`ai-companion`（选 Private 更安全）
   - 不要勾选 README
   - 点击「Create repository」

2. 把项目文件上传到仓库：
   - 进入仓库页面 → 「uploading an existing file」
   - 把 `ai-companion-pwa` 文件夹里的**所有文件**拖进去
   - 点击「Commit changes」

3. 修改配置文件：
   - 在 GitHub 上打开 `config.yaml`
   - 点击 ✏️ 编辑
   - 把 `your-api-key-here` 改成你的 DeepSeek API Key
   - 把 `base_url` 改成 `https://api.deepseek.com/v1`
   - 把 `model` 改成 `deepseek-chat`
   - 点击「Commit changes」

---

## 🚀 步骤三：部署到 Render（3分钟）

1. 打开 https://dashboard.render.com/
2. 点击「New」→「Web Service」
3. 连接你的 GitHub，选择 `ai-companion` 仓库
4. 填写：
   - **Name**：`xiaochao`（或任意名）
   - **Runtime**：Docker
   - **Instance Type**：Free
5. 点击「Create Web Service」
6. 等待部署完成（约3-5分钟）
7. 部署成功后，Render 会给你一个网址，类似：
   `https://xiaochao-xxxx.onrender.com`

---

## 🚀 步骤四：iPhone 上添加（1分钟）

1. 打开 iPhone 的 **Safari**（必须用 Safari！）
2. 访问你部署的网址
3. 点击底部的 **分享按钮** 📤
4. 向下滑，点击 **「添加到主屏幕」**
5. 点击 **「添加」**

🎉 搞定！桌面上就有「小超」图标了，点开跟原生App一模一样！

---

## 🎤 语音使用

- 点击 🎤 按钮 → 开始说话 → 说完自动识别发送
- 首次使用会请求麦克风权限，点「允许」

---

## ⚠️ 注意事项

- Render 免费版会在15分钟无访问后休眠，首次打开要等30秒冷启动
- 冷启动慢的话可以升级 Render 付费版（$7/月），常驻不停
- API Key 不要公开，仓库选 Private
- 对话历史存在浏览器本地，清缓存会丢（服务端也有保存）

---

## 🔧 可选：自定义

| 想改什么 | 改哪里 |
|---------|--------|
| AI名字/性格 | `config.yaml` → personality |
| 语音音色 | `config.yaml` → voice.voice_name |
| 自主判断频率 | `config.yaml` → autonomy.think_interval |
| 访问密码 | `config.yaml` → server.password |

edge-tts 可用音色列表：zh-CN-XiaoxiaoNeural、zh-CN-YunxiNeural、zh-CN-XiaoyiNeural
