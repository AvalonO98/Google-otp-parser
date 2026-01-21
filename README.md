# Google Authenticator 解析工具
一款基于 Python + Streamlit 开发的在线工具，支持解析 Google Authenticator 导出的二维码/URL，提取 OTP 账户信息，并生成可直接导入其他验证器的标准二维码，无需本地配置复杂环境。

## 📋 项目介绍
### 核心功能
- 🖼️ **二维码上传解析**：直接上传 Google Authenticator 导出的二维码图片，自动提取 URL 并解析；
- 📝 **URL 粘贴解析**：粘贴二维码解析后的 URL，提取账户密钥、发行方、验证类型等核心信息；
- 🎨 **生成导入二维码**：为解析后的每个 OTP 账户生成标准二维码，可直接扫描导入微软验证器、Authy、1Password 等工具；
- 📥 **二维码下载**：支持下载生成的 OTP 二维码，方便离线使用；
- 🚀 **在线部署**：可通过 Cloudflare Pages 一键部署，无需本地搭建服务器。

### 技术栈
- 前端/交互：Streamlit
- 二维码解析：pyzbar + Pillow
- 二维码生成：qrcode
- 数据解析：protobuf
- 部署平台：Cloudflare Pages

## 🔧 本地运行
### 环境要求
- Python 3.8+
- 系统依赖（二维码解析）：
  - Windows：需安装 [zbar](https://github.com/NaturalHistoryMuseum/pyzbar-wheels/releases) 预编译包
  - macOS：`brew install zbar`
  - Linux：`sudo apt-get install libzbar0`

### 运行步骤
1. 克隆/下载项目代码到本地：
   ```bash
   git clone https://github.com/你的用户名/ga-parser.git
   cd ga-parser
   ```
2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 编译 Protobuf 文件（若未自动生成 `OtpMigration_pb2.py`）：
   ```bash
   # 需先安装 protoc 编译器（参考常见问题）
   protoc --python_out=. OtpMigration.proto
   ```
4. 启动应用：
   ```bash
   streamlit run app.py
   ```
5. 浏览器访问 `http://localhost:8501` 即可使用。

## ☁️ Cloudflare Pages 部署步骤
### 前置准备
1. 拥有 GitHub 账号，并将项目代码上传到 GitHub 仓库（确保包含以下文件：`app.py`、`requirements.txt`、`OtpMigration.proto`、`.gitignore`）；
2. 拥有 Cloudflare 账号（免费版即可）。

### 部署流程
#### 步骤 1：关联 GitHub 仓库
1. 登录 [Cloudflare 控制台](https://dash.cloudflare.com/)，点击左侧「Pages」→「创建项目」；
2. 选择「连接到 Git」，授权 Cloudflare 访问你的 GitHub 账号；
3. 选择上传好的 `ga-parser` 仓库，点击「开始设置」。

#### 步骤 2：配置构建参数（核心）
| 配置项                | 取值                                                                 |
|-----------------------|----------------------------------------------------------------------|
| 项目名称              | 自定义（如 `ga-parser`）                                             |
| 生产分支              | `main`（或你的默认分支）                                             |
| 构建命令              | 见下方「构建命令」                                                   |
| 构建输出目录          | `.streamlit`                                                         |
| 根目录                | 留空                                                                 |

**构建命令（复制粘贴即可）**：
```bash
# 安装protoc编译器 + 编译proto文件 + 安装依赖 + 启动应用
sudo apt-get update && sudo apt-get install -y protobuf-compiler=3.12.4-1ubuntu7.22.04.1 && protoc --python_out=. OtpMigration.proto && pip install -r requirements.txt && streamlit run app.py --server.port 8080 --server.headless true
```

#### 步骤 3：配置环境变量
点击「环境变量」→「添加变量」，新增以下变量：
| 变量名          | 取值       | 说明                     |
|-----------------|------------|--------------------------|
| `PYTHON_VERSION` | `3.10`    | 指定兼容的Python版本     |
| `PROTOBUF_VERSION` | `4.21.12` | 与protoc版本匹配         |

#### 步骤 4：完成部署
1. 点击「保存并部署」，Cloudflare 会自动拉取代码、执行构建命令、启动应用；
2. 等待部署完成（约 1-2 分钟），部署成功后会生成一个 Cloudflare 子域名（如 `ga-parser.xxx.pages.dev`）；
3. 访问该域名即可使用在线工具。

## ❓ 常见问题
### 1. 本地运行提示 `TypeError: Couldn't parse file content!`
- 原因：手动复制的 `OtpMigration_pb2.py` 文件损坏，或 protobuf 版本与 protoc 不兼容；
- 解决：
  1. 卸载现有 protobuf：`pip uninstall protobuf -y`；
  2. 安装兼容版本：`pip install protobuf==4.21.12`；
  3. 删除错误的 `OtpMigration_pb2.py`，重新编译：`protoc --python_out=. OtpMigration.proto`。

### 2. Windows 安装 pyzbar 失败
- 解决：下载对应 Python 版本的预编译包（如 `pyzbar‑0.1.9‑cp310‑cp310‑win_amd64.whl`），手动安装：
  ```bash
  pip install pyzbar‑0.1.9‑cp310‑cp310‑win_amd64.whl
  ```
  预编译包下载地址：[pypi.org/project/pyzbar/#files](https://pypi.org/project/pyzbar/#files)

### 3. Cloudflare 部署后页面无法访问
- 检查构建命令是否包含 `--server.port 8080 --server.headless true`；
- 确认构建输出目录填写 `.streamlit`；
- 查看 Cloudflare 构建日志，确认 protoc 安装、proto 编译步骤无报错。

## 📄 许可证
本项目基于 MIT 许可证开源，你可自由使用、修改、分发本项目代码。
