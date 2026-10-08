severity: clean

架構對齊結論:第 1 輪修正的三處寫法都沿用既有做法,沒有引入第二種。

- `_need_src`:新測試 `t_graph_discipline_negation_revisit_source` 在函式開頭、`load` 之前呼叫 `_need_src(...)`,傳精確檔或目錄,跟既有用法相同。
  file: `scripts/test_lumos.py:146`(定義,只認檔案系統實況)
  file: `scripts/test_lumos.py:3738`(既有同型:`_need_src("docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md")`)
  file: `scripts/test_lumos.py:10231`(既有同型:`_need_src("docs/lumos-toolchain-knowledge")`)
- 模擬消費專案的測試 `t_negation_hint_consumer_sim`:既有已有同類手搭環境的先例,新測試沿用同一套路(mkdtemp 放進去、subprocess 跑 `-k`、斷言 rc0 且零 ✗ 且 skip)。沒有共用的搭環境函式可沿用,既有各測試都是自己搭。
  file: `scripts/test_lumos.py:31034`(`t_vendored_consumer_srconly_skip_regression`,手搭 scripts/ 加 hooks、spawn 子進程)
  file: `scripts/test_lumos.py:41344`(`_profile_stack_mismatch` 那支,照 `_VENDORED_TOOLKIT` 鋪檔;新測試再加 `_VENDORED_TREE_DIRS` 是因為需要 templates,既有 31034 那支沒複製 templates)
  複製集合的差異有理由(範本要在),且用的是安裝實際清單,比 31034 手寫檔名更貼近真實。
- `_note_shape_negation_parse` 回 dict `{mode, warns, bad_value}`、`_note_shape_negation_config` 保留成兩值薄包裝、doctor 讀結構化欄位:跟 `_drift_config_parts` 同形(具名欄位、doctor 不拆提醒文字)。
  file: `scripts/lumos:28752`(`_drift_config_parts`)
  file: `scripts/lumos:25413`(薄包裝,保留兩值解包的既有呼叫端 `scripts/lumos:25700`)

最高等級:clean
