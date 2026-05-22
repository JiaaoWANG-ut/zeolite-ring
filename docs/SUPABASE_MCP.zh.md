# 在 Cursor 里连接 Supabase MCP

参考官方文档：[Supabase MCP Server](https://supabase.com/docs/guides/ai-tools/mcp)

本项目已在 `.cursor/mcp.json` 预配置好 MCP 地址，绑定 project：

- **Project ref**: `rbiizuchnzklduinnqxx`
- **URL**: `https://rbiizuchnzklduinnqxx.supabase.co`
- **模式**: `read_only=true`（只读，更安全）
- **功能**: `docs,development,debugging`（文档、密钥查询、Auth 日志）

---

## 安装步骤（Cursor）

### 方法一：使用项目配置（推荐）

1. 用 Cursor 打开本仓库 `zeolite-ring`
2. 打开 **Cursor Settings → Tools & MCP**
3. 若已识别 `.cursor/mcp.json`，会看到 **supabase** 服务器
4. 点击 **Connect** / **Login** —— 会弹出浏览器让你登录 Supabase 并授权
5. 登录时选择包含 `rbiizuchnzklduinnqxx` 项目的 Organization
6. 授权完成后 **重启 Cursor** 或 Reload Window

### 方法二：手动添加

在 **Cursor Settings → Tools & MCP → Add MCP Server**，填入：

| 字段 | 值 |
|------|-----|
| Name | `supabase` |
| Type | HTTP |
| URL | `https://mcp.supabase.com/mcp?project_ref=rbiizuchnzklduinnqxx&read_only=true&features=docs,development,debugging` |

保存后同样会触发 Supabase OAuth 登录。

---

## 验证是否连接成功

在 Cursor Agent 里问：

> 用 Supabase MCP 查一下 project URL 和 publishable keys

或：

> 用 MCP 看一下 Auth 最近的 logs

若 MCP 已连接，Agent 会调用 `get_project_url`、`get_publishable_keys`、`get_logs` 等工具。

---

## 可用工具（与本项目相关）

| 工具 | 用途 |
|------|------|
| `get_project_url` | 确认 API URL |
| `get_publishable_keys` | 查看 anon / publishable key |
| `get_logs` | 查 Auth / API 错误日志（登录失败排查） |
| `search_docs` | 搜 Supabase 文档 |
| `get_advisors` | 安全/性能建议 |

本项目**只用 Supabase Auth**，不用数据库表，因此未启用 database 写操作。

---

## 安全建议（官方）

- MCP 仅用于**开发调试**，不要连生产敏感数据
- 保持 Cursor **每次工具调用需手动确认**
- 已启用 `read_only=true` + `project_ref` 限定到单个项目

---

## SSH / 无浏览器环境（可选）

若无法 OAuth，可在 [Supabase Access Tokens](https://supabase.com/dashboard/account/tokens) 生成 PAT，在 MCP 配置中加 header：

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=rbiizuchnzklduinnqxx&read_only=true",
      "headers": {
        "Authorization": "Bearer YOUR_SUPABASE_PAT"
      }
    }
  }
}
```

**不要把 PAT 提交到 Git。**
