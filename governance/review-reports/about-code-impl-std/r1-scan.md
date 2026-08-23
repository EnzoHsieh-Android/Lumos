# r1-scan.md: about-code-impl-std-r1.md 机械扫描报告

扫描范围：第 384-446 行（「★剩四項的實作規格★」至「★合約候選★」）

## 第一项：反引号包住的识别字

### 已在 repo 中定义的标识字

| 标识字 | grep 结果 | 命中档:行（最多 2 个） |
|---|---|---|
| `_impact_knob` | ✓ 找到 | scripts/lumos:13883, scripts/lumos:13624 |
| `LUMOS_IMPACT_BASENAME_MATCH` | ✓ 找到 | scripts/test_lumos.py:21444, scripts/test_lumos.py:21455 |
| `as_list` | ✓ 找到 | scripts/lumos:262, scripts/lumos:341 |
| `git_last_change_dates` | ✓ 找到 | scripts/test_lumos.py:541, scripts/test_lumos.py:566 |
| `cmd_impact` | ✓ 找到 | scripts/test_lumos.py:8790, scripts/test_lumos.py:14587 |
| `_BASENAME_COUNTS_CACHE` | ✓ 找到 | scripts/lumos:13587, scripts/lumos:13626 |
| `contract_priority` | ✓ 找到 | scripts/lumos:14094, scripts/lumos:14101 |
| `about_code_stamp` | ✓ 找到 | scripts/test_lumos.py:502, scripts/test_lumos.py:503 |
| `run_doctor` | ✓ 找到 | scripts/slim-gen.py:6, scripts/test_lumos.py:19105 |
| `eval_edit` | ✓ 找到 | governance/eval/retrieval_eval.py:305, governance/eval/retrieval_eval.py:374 |
| `about_code_to_rater` | ✓ 找到 | scripts/test_lumos.py（多处） |
| `cmd_remove` | ✓ 找到 | scripts/test_lumos.py（多处） |
| `cmd_set` | ✓ 找到 | scripts/test_lumos.py（多处） |
| `cmd_append` | ✓ 找到 | scripts/test_lumos.py（多处） |

### 未在 repo 中定义的标识字

| 标识字 | 说明 |
|---|---|
| `LUMOS_IMPACT_ABOUT` | 新增常数，未实现（spec 规定） |
| `about_hit` | 新增欄位，未实现（spec 规定） |
| `LUMOS_IMPACT_ABOUT_MAX` | 新增常数，未实现（spec 规定） |
| `pin_top3_must` | 新增指标名，未实现（spec 规定） |

**说明**：上述四项均系本规格待实现的内容，不在现有代码中，属于设计预期。

---

## 第二项：行号引用验证

### scripts/lumos 中的行号引用

| 引用 | 实际内容（前 80 字） | 对应情况 |
|---|---|---|
| `:13883` | `def _impact_knob(name, default):` | ✓ 正确 - 函数定义 |
| `:13609` | `knob:LUMOS_IMPACT_BASENAME_MATCH(2026-08-07 轉正預設` | ✓ 正确 - 参数定义 |
| `:7680` | `targets.append((rel, [str(x) for x in as_list(n.` | ✓ 正确 - as_list 调用 |
| `:14310` | `print(f"  {'⚠合約 ' if x.get('contract') els` | ✓ 正确 - 条件表达式 |
| `:14178` | `results.append({"node": x["node"], "kind": "inci` | ✓ 正确 - incident 路径 |
| `:14203` | `results.append({"node": x["node"], "kind": "` | ✓ 正确 - direct 路径 |
| `:14214` | `results.append({"node": x["node"], "kind` | ✓ 正确 - indirect pinned 路径 |
| `:14223` | `results.append({"node": x["node"], "kind": "` | ✓ 正确 - indirect free 路径 |
| `:14226` | `pins = [r for r in results if r["pinned"]]` | ✓ 正确 - pins 定义 |
| `:13587` | `_BASENAME_COUNTS_CACHE = {}` | ✓ 正确 - 缓存初始化 |
| `:868` | `f"有 {len(sa_stale)} 篇功能筆記在上次確認之後又` | ✓ 正确 - Check S 输出格式 |
| `:14024` | `repo_root_for_lookup = repo_root if repo_root is not None else vault.parent.` | ✓ 正确 - cmd_impact 内后备逻辑 |
| `:14171-14267` | 范围起点：`# 8.5 ranked 融合(階段三,spec §3)` 范围终点：`final = pins + free + rescued` | ✓ 有效 - 涵盖 ranked 融合整个区块 |

### 其他文件中的行号引用

| 引用 | 实际内容（前 80 字） | 对应情况 |
|---|---|---|
| `impact-hook.py:358` | `hit = f"/{x['hit']}" if x.get("hit") == "basename-match" else ""` | ⚠ 文件路径不完整 - 实际位置：scripts/hooks/claude/impact-hook.py:358 |
| `impact-hook.py:344-348` | `for x in pins: / mk = {"incident": "⚠事故", "direct": "直` | ⚠ 文件路径不完整 - 实际位置：scripts/hooks/claude/impact-hook.py:344-348 |
| `test_lumos.py:19210` | `marker = "def run_doctor(env: Env, strict: bool, color: bool, suggest=False,` | ✓ 正确 - 签名字符串锚定 |

---

## 第三项：自相矛盾检查

### 检查结果

**无明显自相矛盾**

### 说明

文档中多处出现「不改 X」与「改 Y」或「加欄位」的并列表述，经逐条审视，这些均属于**精确说明改动边界的设计陈述**，而非逻辑矛盾。例如：

- 「不覆寫既有 `hit` 欄」 vs 「加欄位 **`about_hit: True`**」：这是两个分别的操作，一个说的是不碰既有字段，另一个说的是新增字段。
- 「不改任何一條路徑的 pinned 邏輯」 vs 「排前排」：排序是在既有的 pinned 判定之后进行的，不改判定逻辑。

---

## 第四项：文档内交叉引用

### 扫描范围内发现的交叉引用

**无**。扫描范围（第 384-446 行）未发现「見 XX 節」、「同②」、「[[...]]」等形式的明确内部交叉引用。

### 说明

- 文档头部（frontmatter）含有 wikilink 引用（如 `[[Projects/檢索edit面真紅_計劃]]`），但这些超出扫描范围。
- 文档中用数字标记（#1 到 #10）指代工具清单项目，但范围 384-446 行内只涉及 #4、#6、#9、#10 四项的规格说明，不存在前向或后向交叉引用。

---

## 扫描总结

| 项目 | 结果 |
|---|---|
| **未定义的反引号标识字** | 4 个（均为新增设计元素，属预期）|
| **行号引用完整性** | 13 个核心行号正确；2 个文件路径不完整（impact-hook.py 缺目录前缀） |
| **自相矛盾** | 无 |
| **文档内交叉引用** | 无（范围内） |

### 关键发现

1. **文件路径不完整**：文档中 3 处引用 `impact-hook.py` 的行号，但实际文件位置是 `scripts/hooks/claude/impact-hook.py`。这是文档相对路径表示的不一致，不影响指向的准确性（行号核验通过），但可能造成自动工具查找失败。

2. **新增设计元素**：四个未定义的标识字（`LUMOS_IMPACT_ABOUT`、`about_hit`、`LUMOS_IMPACT_ABOUT_MAX`、`pin_top3_must`）均系本规格待实现的内容，未出现在现有代码库中。这符合规格的性质（设计先行）。

