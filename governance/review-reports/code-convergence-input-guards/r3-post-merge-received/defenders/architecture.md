severity:维持原major  
裁決: concern

finding: post-merge-架构对齐-post-merge-codex-F1

引句：「`blobs = _nodehome_cat_blobs(root, ...)`」

现象判准：HIT  
本批新增判准：MISS

证据：

- d9 基线已经通过 `_nodehome_cat_blobs` 一次读取最多 50 篇笔记的新旧版本：`scripts/lumos@d9f28e3b44d8617ea2313c2f306f7c05ca0d37f5:32429-32443`。
- 候选执行完全相同的调用和后续解码：`scripts/lumos@25683c65991e3602335462406893cfa2099b5746:32536-32550`。
- 两版 `_ns_close_summary_collect` 的固定源码 SHA-256 均为 `8f70405a78f345075eb038e4feb69b39365c6f2b2233cdaa1c614fe99ae7e91c`。
- 两版底层 `_nodehome_cat_blobs` 也相同，SHA-256 均为 `673757dc95d8fc25bcff3752c5d01280cd2c34273dc1f48bb659a4e6d4008dca`。它确实以 `capture_output=True` 缓冲整批内容：候选 `scripts/lumos:29344-29372`；d9 `scripts/lumos:29336-29364`。
- 上游在 d9 已由 note-shape 路径调用该收集器：`scripts/lumos@d9f28e3b44d8617ea2313c2f306f7c05ca0d37f5:32385`；候选对应 `scripts/lumos:32492`。
- `git blame` 显示 d9 的整段收集器来自 `b0e7c1d56a2b607ef6c66b25e0c77ca05de7a5cf`（`feat: 結案時摘要沒跟著改會提醒,舊帳列進存量漂移`）。候选是双亲合并提交，其第二亲正是 d9。
- 原始 base60 材料因此包含后来进入 main 的改动；不能把这段 main 来源代码算作 `d9..25683c65` 本批新增。

第二机制判定：

- 候选新增的固定树路径 `_nodehome_staged_route_tests` 在 `scripts/lumos:29470-29505` 调用 `_nodehome_cat_blobs_capped`。
- capped 包装器并未实现另一套读取机制；它先检查大小，随后仍调用既有 `_nodehome_cat_blobs`：`scripts/lumos:29312-29341`。
- 因此这里是同一 reader 的两个调用策略，不是本批另建第二套 reader。close-summary 的无界调用是真实旧问题，但不是候选相对 d9 新增，也不能作为本批 blocking 回归。未宣称问题已经修复。

finding: post-merge-架构对齐-post-merge-codex-F2  
severity: minor  
blocking: false

引句：「`skipped = max(0, len(cands) - _NS_CLOSE_SUMMARY_MAX_NOTES) + len(bad)`」

证据：

- `scripts/lumos:32536`
- `scripts/lumos:32561`
- `scripts/lumos:32571`

现象：若状态变动超过 50 篇、前 50 篇都没有摘要问题，`items` 为空会在 `scripts/lumos:32561` 提前返回，无法执行 `scripts/lumos:32571-32572` 的 skipped 提醒。依指示保留该真实漏提醒，不对 F2 另作裁决；本轮未重跑原报告的纯内存试验。

验证边界：

- 仅做固定提交源码、上下游、测试规范和函数文本哈希核对；未读取其他席报告内容。
- 文件系统为只读，未运行需要建立临时仓库的动态复现，也未声称测试通过。
- 无法写回 `/tmp/lumos-seat-staging/code-convergence-post-merge/architecture-native.md`；以上为完整替换稿。