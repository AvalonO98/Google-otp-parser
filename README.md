# Google Authenticator 解析工具
一款基于 Python + Streamlit 开发的在线工具，支持解析 Google Authenticator 导出的二维码/URL，提取 OTP 账户信息，并生成可直接导入其他验证器的标准二维码，无需本地配置复杂环境。

## 📋 项目介绍
### 核心功能
- 🖼️ **二维码上传解析**：直接上传 Google Authenticator 导出的二维码图片，自动提取 URL 并解析；
- 📝 **URL 粘贴解析**：粘贴二维码解析后的 URL，提取账户密钥、发行方、验证类型等核心信息；
- 🎨 **生成导入二维码**：为解析后的每个 OTP 账户生成标准二维码，可直接扫描导入微软验证器、Authy、1Password 等工具；
- 📥 **二维码下载**：支持下载生成的 OTP 二维码，方便离线使用；
- 🚀 **在线部署**：可通过 Railway 一键部署，完美适配 Python 动态服务，无需本地搭建服务器。

### 技术栈
- 前端/交互：Streamlit
- 二维码解析：pyzbar + Pillow
- 二维码生成：qrcode
- 数据解析：protobuf
- 部署平台：Railway（适配 Python 动态服务的免费平台）

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

## ☁️ Railway 部署步骤（推荐）
Railway 是适配 Python 动态服务的免费部署平台，完美支持 Streamlit 应用长期运行，无需复杂配置。

### 前置准备
1. 拥有 GitHub 账号，并将项目代码上传到 GitHub 仓库（确保包含以下文件：`app.py`、`requirements.txt`、`OtpMigration.proto`、`.gitignore`）；
2. 拥有 Railway 账号（免费版即可，推荐用 GitHub 账号授权登录）。

### 部署流程
#### 步骤 1：注册并登录 Railway
1. 访问 [Railway 官网](https://railway.app/)；
2. 点击「Login」→ 选择「Continue with GitHub」，授权 Railway 访问你的 GitHub 账号。

#### 步骤 2：创建项目并关联 GitHub 仓库
1. 在 Railway 控制台首页，点击「New Project」（蓝色按钮）；
2. 选择「Deploy from GitHub repo」；
3. 若仓库未显示，点击「Configure GitHub App」，勾选你的 `ga-parser` 仓库后刷新；
4. 选择目标仓库（如 `你的用户名/ga-parser`），点击「Import」。

#### 步骤 3：配置构建/启动命令（核心）
1. 进入项目页面，点击顶部「Settings」→ 左侧「Build & Deploy」；
2. 配置以下参数：

| 配置项                | 取值                                                                 |
|-----------------------|----------------------------------------------------------------------|
| Build Command         | `apt-get update && apt-get install -y protobuf-compiler && protoc --python_out=. OtpMigration.proto` |
| Start Command         | `streamlit run app.py --server.port $PORT --server.headless true --server.enableCORS false --server.enableXsrfProtection false` |
| Root Directory        | 留空                                                                 |

3. 点击页面底部「Save Changes」保存配置，Railway 会自动触发重新部署。

#### 步骤 4：完成部署并访问
1. 回到项目「Deployments」标签页，等待部署完成（约 1-2 分钟）；
2. 部署成功后，Railway 会生成一个公开域名（如 `ga-parser-xxxx.up.railway.app`）；
3. 点击该域名，即可在线使用 Google Authenticator 解析工具。

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

### 3. Railway 部署提示 `protoc: not found`
- 原因：构建命令未安装 protoc 编译器；
- 解决：确认「Build Command」包含 `apt-get install -y protobuf-compiler`，保存后重新部署。

### 4. Railway 访问域名显示「Connection Refused」
- 原因：启动命令未使用 Railway 自动分配的端口；
- 解决：确认「Start Command」中端口参数为 `--server.port $PORT`（而非固定 8080）。

### 5. Railway 部署后二维码解析功能异常
- 原因：缺少系统级 zbar 依赖；
- 解决：修改「Build Command」，新增 zbar 安装：
  ```bash
  apt-get update && apt-get install -y protobuf-compiler libzbar0 && protoc --python_out=. OtpMigration.proto
  ```

## 📄 许可证
本项目基于 MIT 许可证开源，你可自由使用、修改、分发本项目代码。
