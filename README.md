<p align="center">
  <img src="icon.ico" width="80" alt="MiMo Code Logo">
</p>

<h1 align="center">MiMo Code Desktop</h1>

<p align="center">
  <strong>开源 AI 编程智能体，拥有跨会话记忆</strong>
</p>

<p align="center">
  <a href="https://mimo.xiaomi.com/mimocode">官网</a> ·
  <a href="https://mimo.xiaomi.com/mimocode/start">文档</a> ·
  <a href="https://github.com/XiaomiMiMo/MiMo-Code">GitHub</a>
</p>

---

## 简介

基于 [MiMo Code](https://github.com/XiaomiMiMo/MiMo-Code) 的桌面客户端，使用 Python + pywebview 将 Web UI 封装为原生 Windows 桌面应用。

**MiMo Code** 是小米开源的 AI 编程智能体，基于 MiMo-V2.5 大模型，支持跨会话记忆、多模式协作、权限管理等特性。

## 快速开始

### 环境要求

- Windows 10/11（自带 Edge WebView2）
- Python 3.10+
- mimo.exe（从 [MiMo Code](https://github.com/XiaomiMiMo/MiMo-Code) 获取）

### 安装依赖

```bash
pip install pywebview
```

### 启动

双击 `MiMoCode-启动点这里.bat` 即可启动桌面应用。

或命令行启动：

```bash
python app.py
```

## 功能特性

| 功能 | 说明 |
|------|------|
| 🤖 智能编程 | 基于 MiMo-V2.5，支持代码生成、调试、重构 |
| 💾 跨会话记忆 | 持久化项目记忆，跨对话保留上下文 |
| 🔐 权限管理 | AI 操作电脑时弹出审批对话框 |
| 💭 活动面板 | 右侧展示思考过程、工具调用、文件变更 |
| 🎯 多种模式 | build（构建）、plan（规划）、compose（编排） |
| 🎨 深色主题 | 琥珀金配色，护眼舒适 |

## 文件结构

```
MiMo-Code/
├── MiMoCode-启动点这里.bat   启动入口
├── 使用说明.txt               功能介绍
├── app.py                     桌面应用主程序
├── index.html                 Web UI
├── icon.ico                   应用图标
└── bin/
    └── mimo.exe               AI 后端引擎
```

## 技术架构

```
┌─────────────────────────────────────┐
│  MiMo Code Desktop (pywebview)      │
│  ┌───────────────────────────────┐  │
│  │  Edge WebView2 (原生渲染)     │  │
│  │  index.html (Web UI)          │  │
│  └──────────────┬────────────────┘  │
│                 │ HTTP API          │
│  ┌──────────────▼────────────────┐  │
│  │  mimo.exe serve (端口 3456)   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## 相关链接

- [MiMo Code 官网](https://mimo.xiaomi.com/mimocode)
- [MiMo Code 文档](https://mimo.xiaomi.com/mimocode/start)
- [MiMo 模型 (HuggingFace)](https://huggingface.co/XiaomiMiMo)
- [MiMo API 平台](https://platform.xiaomimimo.com/)

## 许可协议

MIT License · [Xiaomi MiMo Team](https://github.com/XiaomiMiMo)
