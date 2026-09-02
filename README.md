# 均冠人力资源看板 · GitHub 自动同步

在线花名册（金山文档）→ 看板（GitHub Pages）全自动同步，不依赖千问办公、不依赖本机电脑开机。

## 工作流程

每天 09:00 / 21:00（北京时间）自动执行：
1. 调用金山文档 AirScript webhook 取数（全员名册 / 总表 / 招聘职位登记表）
2. 重建看板全部指标
3. 生成 `index.html`
4. 部署到 GitHub Pages

花名册有变动后，最多延迟一个轮询周期（半天内）看板即更新。

## 一次性配置步骤（约 10 分钟）

### 1. 注册 GitHub 账号
https://github.com/signup （免费，用邮箱注册）

### 2. 创建仓库
- 点右上角「+」→ New repository
- Repository name 填：`junguan-hr-dashboard`
- **Public**（公开，Actions 免费额度不限；私有会有限额，虽然也够用）
- 其余默认，点 Create repository

### 3. 上传本包全部文件
- 在仓库页面点 `Add file` → `Upload files`
- 把本文件夹里的所有文件拖入（注意要包含 `.github` 文件夹和里面的 workflow 文件）
- 提交（Commit changes）

### 4. 配置两个密钥（Secrets）
仓库页面 → Settings → Secrets and variables → Actions → New repository secret，添加两个：

| 名称 | 值 |
|---|---|
| `KDOCS_WEBHOOK_URL` | 金山文档 AirScript 的 webhook 地址（形如 `https://www.kdocs.cn/api/v3/ide/file/.../sync_task`） |
| `KDOCS_AIRSCRIPT_TOKEN` | 金山文档脚本令牌（脚本编辑器里生成，半年有效，到期需更新） |

### 5. 开启 GitHub Pages
仓库页面 → Settings → Pages
- Source 选 **GitHub Actions**
- 保存即可

### 6. 首次运行
仓库页面 → Actions → 左侧 `Update HR Dashboard` → 右侧 `Run workflow` 手动跑一次。
运行成功后，看板地址为：

```
https://<你的GitHub用户名>.github.io/junguan-hr-dashboard/
```

### 7. 验证
打开上面的网址，确认看板数据显示正常（数据快照为当天日期）。此后每天 09:00/21:00 自动更新。

## 日常维护

- 改更新频率：编辑 `.github/workflows/update-dashboard.yml` 里的 cron（UTC 时间，北京时间减 8 小时）
- 令牌到期：在金山文档脚本编辑器重新生成令牌，回到 GitHub Settings → Secrets 更新 `KDOCS_AIRSCRIPT_TOKEN` 即可
- 看板样式/指标改动：修改本仓库里的 `dashboard_template_v2.html`（指标逻辑在 `build_data_v2.py`），提交后手动 Run workflow 生效
- 令牌是最高权限凭证，请勿外泄；若泄露请到脚本编辑器重新生成
