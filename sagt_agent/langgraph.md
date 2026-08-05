## langgraph.json说明
可以把langgraph理解成一个容器，langgraph.json就是这个“容器”的部署描述文件（类似web.xml）

"graphs": { "sagt": "src/graphs/sagt_graph/sagt_graph.py:graph" },  // 业务主体

"http": { "app": "src/webapp/webapp.py:app" },                      // 自定义路由

"auth": { "path": "src/auth/auth.py:auth" }                         // 认证钩子

### Server 启动时做的事
1. 读 langgraph.json，import 你的 graph 对象，注册为 graph_id = sagt
2. 把你的自定义 FastAPI 路由合并进它自己的 HTTP 应用
3. 把你的 auth 钩子挂到所有请求的前置校验上
4. 自动注入基础设施：收到 /runs 请求时，帮你把 checkpointer（对话状态持久化）、store、config 都准备好再执行你的 graph