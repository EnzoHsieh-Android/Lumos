severity: minor

## 問1 分層與依賴方向
對齊。新碼全放在 scripts/lumos 的 update 區(_vendor_toolchain 正上方),由 cmd_update 呼叫;_reinject_compute 抽成純算法、_reinject_claude_block 只負責寫回,與 _reinject_all 的上下層方向一致;_vendored_pending、_toolchain_src_ok 由套用與預覽共用,沒有跨層直呼。
引句:「c = _reinject_compute(root, target, _expected_claude_body(root, slug))」
佐證:scripts/lumos:20311(_reinject_compute)、scripts/lumos:20872(_vendored_pending)、scripts/lumos:20278(_reinject_targets 沿用)

## 問2 命名與錯誤處理
大致對齊:私有函式 `_` 前綴、訊息中文白話、擋下訊息與 _vendor_toolchain 原文相同。有兩處小差異,見 F1、F2。
引句:「print("lumos update --dry-run(僅預演,不改動):")」
佐證:scripts/lumos:20955(沿用 cmd_deinit 預覽開頭格式,deinit 在 scripts/lumos:20020 前後)

## 問3 第二種做法
沒有引入新的呼叫模式:git 呼叫沿用 _sp_run_text,子行程加隔離家目錄的測法沿用 t_update_syncs_global_from_fresh_not_stale 的結構。僅有 F3 一處繞過既有小工具。
引句:「sha = _sp_run_text(["git", "-C", str(src), "rev-parse", "--short", "HEAD"])」
佐證:scripts/lumos:1546(_sp_run_text 定義)、scripts/lumos:1478(同一用法)

## F1 預覽的 root 標籤與 deinit 預覽不同
severity: minor
blocking: 否
引句:「print(f"  專案: {root}")」
佐證:file: scripts/lumos:20956;對照 cmd_deinit 預覽 `print(f"  root: {root}")`(scripts/lumos:20018 附近,cmd_deinit 起於 scripts/lumos:19976)
說明:開頭第一行沿用了 deinit 格式,但下一行標籤從 `root:` 變 `專案:`。兩個 --dry-run 預覽並列時欄位名不一致。

## F2 shell 引號直接用 shlex,沒走既有 _sh_quote
severity: minor
blocking: 否
引句:「q = _shlex.quote(str(Path(src).resolve()))」
佐證:file: scripts/lumos:20947;對照 scripts/lumos:438(_sh_quote,docstring 正是「印給人照貼的指令裡的參數加 shell 引號」)
說明:同檔已有包好用途的 _sh_quote,新碼另 import shlex 重做同一件事。不過 scripts/lumos:1203 也是直接用 _shlex.quote,所以鄰居本身也有兩種,結構不壞,列 minor。⚠ 判不準是否算「自創工具」,取較輕者。

## F3 例外吞法:預覽端細分例外,鄰居 deinit 用寬接
severity: minor
blocking: 否
引句:「except (UnicodeDecodeError, OSError) as e:」
佐證:file: scripts/lumos:20886 起的 _update_rule_plan;對照 scripts/lumos:19990(cmd_deinit 的 `except Exception:`)
說明:新碼接得更窄且有理由(註解已說明讀不了的分類),方向比鄰居好,但與鄰居的吞法風格不同。純一致性提示,不要求改。

不對齊共 3 條,其中重大 0 條
