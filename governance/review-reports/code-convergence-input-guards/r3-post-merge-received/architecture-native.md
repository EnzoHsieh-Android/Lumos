severity: major

finding: post-merge-架构对齐-post-merge-codex-F1  
severity: major  
blocking: true  
引句:「blobs = _nodehome_cat_blobs(root,」  
证据file: `scripts/lumos:32538`  
证据file: `scripts/lumos:29312`  
证据file: `scripts/lumos:29356`  
现象：新提醒一次读取最多 50 篇笔记的新旧版本，即最多 100 个 blob，但只限制篇数、不限制单档或总字节数；底层 `capture_output=True` 会把全部内容缓冲进内存。一个超大笔记即可让提交前钩子耗尽内存或被系统终止，越过原定“提醒失败只讲一句、不影响判定”的 fail-open 边界。  
本批新增判准：合并前分支已为同类固定树批量读取建立 `_nodehome_cat_blobs_capped`，包含单档、总量及截止时间限制。主线新提醒引入第二条无上限批读路径，属于具体架构分叉，不是风格差异。应复用有界入口，并将超限项计入 skipped。

finding: post-merge-架构对齐-post-merge-codex-F2  
severity: minor  
blocking: false  
引句:「skipped = max(0, len(cands) - _NS_CLOSE_SUMMARY_MAX_NOTES) + len(bad)」  
证据file: `scripts/lumos:32536`  
证据file: `scripts/lumos:32561`  
证据file: `scripts/lumos:32571`  
现象：若状态变动超过 50 篇、前 50 篇都没有摘要问题，而第 51 篇以后未检查，`items` 为空会提前返回，连“另有 N 篇没看”也不输出。纯内存调用 `_ns_close_summary_emit(..., [], 1, None)` 的实测输出为空。  
本批新增判准：冻结 patch 自己声明超限项应“不看、讲一句”；当前控制流没有兑现。第二机制 `c7` 之后可能补捉，因此不是 major，但提交当下提醒存在确定漏报。

架构核对结果：

- 提交当下提醒仍只在 `note-shape --staged` 执行；存量问题由 `c7` 扫描负责，分层方向正确。
- 三个固定树补助函数及 `cmd_home_check` 与整合前 `75ae9279` 逐字一致。
- push-end 仍由终点版本配置裁判；没有改成逐历史提交读取设置。提交前起点／索引分别分类，是 staged 输入快照保护，不应误改成 push-end 历史政策。
- 固定 HEAD 再核为 `25683c65991e3602335462406893cfa2099b5746`，工作树无变更。

图谱镜头逐条核对：

- `canary-record未落盘事件`：分支确实触及 `cmd_canary`；镜头只给 Issue 名、无正文或合约，未用它推导结论。
- `lumos-cli-read`：本批没有改变 search 路径；只是因共同归属档案被带入。绑定状态仅表示测试名存在。
- `design-loop`：未改变其处置闸触发。
- `pitfalls-code-loop`：只有风险标记，没有可直接裁判的合约行。
- `bound-tests-gate`：没有改变 bound-tests 执行路径。
- `guard-kill`：冻结 closure 提到一次执行，但文字不可信，且本批未改 guard-kill 实作，未据此宣称通过。
- `授权与归属`：没有触及档头、vendored 白名单或 deinit 删除路径。
- `测试假绿形态`：测试档确实有改；镜头明确“有”只代表方法存在。因沙盒无法运行测试，未把它算成验证通过。
- 其余节点只有名称、没有内容；外部码表补选超时，均未拿来下判断。

实读／未读／费用：

- 完整实读：`incoming-source.patch` 569/569 行、`closure.patch` 44/44 行、`graph-lens.txt` 57/57 行。
- 选择性实读：相关 `scripts/lumos` 函数、对应测试与合并拓扑；未宣称读完整个 repo。
- 未读：材料目录其余文件、其他席报告、镜头中只列名节点的全文。
- 测试未执行：唯读环境没有可写临时目录，测试在收集前失败；仅完成 AST 解析及纯内存核心判定。
- 费用保守估计约 5,500/1,800 行，已超额；主要来自误展开的 2,624 行全量 diff 清单。另有数次调用超过 100 行。一次 `git diff-tree --check` 意外显示了 review-reports 路径及一行内容；未继续读取，也未用于结论。