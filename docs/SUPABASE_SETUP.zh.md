# Supabase 配置指南（Zeolite Ring）

Supabase 是**云端托管**服务，不需要自己部署服务器。你要做的是：在 Supabase 控制台创建一个 Project，把 URL 和 anon key 填进本项目。

> **关于 MCP**：当前 Cursor 环境**没有** Supabase MCP。无法由我代你在 Supabase 后台点击创建项目；你需要在浏览器里完成一次创建，然后把密钥发我或运行下面的配置脚本。

---

## 第一步：创建 Supabase 项目

1. 打开 [https://supabase.com/dashboard](https://supabase.com/dashboard) 并登录（GitHub 账号即可）
2. 点击 **New project**
3. 填写：
   - **Name**: `zeolite-ring`（任意）
   - **Database Password**: 自己记好（本项目 Auth 不用直连数据库，但创建项目时必须设）
   - **Region**: 选离用户近的（如 `West US` 或 `East Asia`）
4. 等待约 1–2 分钟，项目状态变为 **Active**

---

## 第二步：复制 API 密钥

1. 左侧 **Project Settings**（齿轮）→ **API**
2. 复制这两项：
   - **Project URL** → 形如 `https://xxxxxxxx.supabase.co`
   - **anon public** key → 形如 `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. 在本项目根目录运行：

```bash
python3 scripts/configure_supabase.py \
  --url "https://xxxx.supabase.co" \
  --anon-key "eyJhbGciOi..."
```

或手动编辑 `assets/js/config.js`。

---

## 第三步：配置 Auth 回调 URL

假设你的 Cloudflare Pages 域名为 `https://zeolite-ring.pages.dev`（换成你的实际域名）：

1. Supabase → **Authentication** → **URL Configuration**
2. 设置：
   - **Site URL**: `https://zeolite-ring.pages.dev`
   - **Redirect URLs**（每行一个）:
     ```
     https://zeolite-ring.pages.dev/viewer.html
     https://zeolite-ring.pages.dev/landing.html
     http://localhost:8080/viewer.html
     http://localhost:8080/landing.html
     ```
3. 点击 **Save**

---

## 第四步：开启登录方式

### Email（邮箱 + 密码 / Magic Link）

1. **Authentication** → **Providers** → **Email**
2. 确认 **Enable Email provider** 已打开
3. 开发阶段可暂时关闭 **Confirm email**（方便测试注册）

### Google OAuth

1. 打开 [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. **Create Credentials** → **OAuth client ID** → **Web application**
3. 填写：
   - **Authorized JavaScript origins**:
     ```
     https://zeolite-ring.pages.dev
     http://localhost:8080
     ```
   - **Authorized redirect URIs**:
     ```
     https://xxxx.supabase.co/auth/v1/callback
     ```
     （`xxxx` 换成你的 Supabase Project URL 里的子域名）
4. 复制 **Client ID** 和 **Client Secret**
5. Supabase → **Authentication** → **Providers** → **Google** → 粘贴并 **Save**

---

## 第五步：推送到 GitHub

```bash
git add assets/js/config.js
git commit -m "Configure Supabase auth"
git push origin main
```

Cloudflare Pages 会自动重新部署。

---

## 验证

1. 打开 `https://你的域名/landing.html`
2. 点击 **Enter Viewer**
3. 测试：
   - Google 登录
   - 邮箱注册 / 登录
   - Magic Link

登录成功后应跳转到 `viewer.html`；未登录直接访问 `viewer.html` 会被重定向回 landing。

---

## 常见问题

| 问题 | 处理 |
|------|------|
| Google 登录后白屏 | 检查 Redirect URLs 是否包含 `/viewer.html` |
| `Invalid login credentials` | 邮箱是否已确认；或先用 Magic Link |
| 本地能登、线上不能 | Site URL 和 Redirect URLs 是否用了 Pages 域名 |
| 不想配 Supabase 先预览 | 保持 `config.js` 为占位符，viewer 会以 Dev mode 跳过登录 |

---

## 安全说明

- **anon key 可以写在前端**，这是 Supabase 官方推荐做法
- 不要把 **service_role** key 放进前端或 Git
- 本项目只用 Auth，不暴露数据库表，无需额外 RLS 配置
