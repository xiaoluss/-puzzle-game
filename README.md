# 解谜游戏 - 答案验证系统

## 项目结构

```
puzzle-game/
├── frontend/          # Vue 3 前端 (Vite)
│   ├── src/
│   │   ├── components/game/    # 游戏组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # API 接口
│   │   └── utils/             # 工具函数
│   └── package.json
├── backend/           # Python Flask 后端
│   ├── app.py         # 入口
│   ├── models.py      # 数据库模型
│   ├── routes/        # API 路由
│   └── requirements.txt
└── story_data/        # 剧情示例
```

## 启动方式

### 1. 后端
```bash
cd backend
pip install -r requirements.txt
python app.py
```
后端运行在 http://localhost:5000

### 2. 前端
```bash
cd frontend
npm install
npm run dev
```
前端运行在 http://localhost:3000

## 使用方法

1. 打开 http://localhost:3000 → 注册/登录
2. 进入管理后台 `/admin` → 创建角色 → 创建章节 → 编辑场景
3. 返回游戏 `/game` → 选择章节开始游玩

## 场景类型

| 类型 | 说明 |
|------|------|
| dialog | 对话场景，有角色头像和打字机效果 |
| narrative | 叙述场景，剧情描述文字 |
| puzzle_text | 填空题，输入文本答案 |
| puzzle_choice | 选择题，点选选项 |
| puzzle_image | 图片题，点击图片区域 |

## 功能

- 注册/登录 (JWT)
- 剧情管理后台 (章节/场景/角色 CRUD)
- 打字机效果对话
- 多题型答案验证 (填空/选择/图片)
- 提示系统 (3次错误后显示答案)
- 游戏进度保存
