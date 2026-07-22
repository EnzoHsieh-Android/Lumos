---
type: verification
status: pass
date: 2026-07-22
valid_under:
  - "cmd_install 尾端呼叫 _sync_global_claude(來源 repo 自身);_install_hooks_py ②③委派同函式"
  - "_prune_dangling 只剪懸空、_RETIRED_CLAUDE_HOOKS 主動刪撤除 hook 殘留真檔"
revalidate_when:
  - "動 _sync_global_claude/_install_hooks_py/cmd_install 或 _GLOBAL_CLAUDE_HOOKS/_RETIRED_CLAUDE_HOOKS 常數"
plan_refs:
  - "[[Projects/install全域hook同步_計劃]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:t_install_global_hook_sync 9 checks(copy 三 hook/settings 註冊/撤除 code-loop-guard 真檔刪+註冊剪/使用者自訂 hook 不誤剪/冪等)+既有 t_install_hooks_py/t_merge_settings_*/t_hook_copy_list_completeness 迴歸全綠(漂移守衛改指 _GLOBAL_CLAUDE_HOOKS 常數);全套 1335 綠(1 fail 為漂移守衛真相源遷移,已修)
  KEY:全域機器自癒缺口補上——cmd_install 尾端加 _sync_global_claude(不需專案 vault),別台只全域裝 lumos 的機器 `./install.sh` 即清舊 Stop 註冊(code-loop-guard nag);_install_hooks_py ②③委派同函式消雙寫
  KEY:撤除 hook 主動刪(_RETIRED_CLAUDE_HOOKS 常數)——補[[Issues/hook卸載殘留註冊]]殘尾:_prune_dangling 只清懸空,真檔還在時不剪;主動刪→變懸空→prune 收,對稱操作補齊「刪腳本」半
  KEY:blast radius 測試重壓——machine-global settings.json 寫入,假 HOME(HOME=tmp)隔離、既有內容保留、不誤剪使用者 hook、冪等四項全綠
  VERIFY:spec 過機械前置(lint/pitfalls);standard 檔(machine config 有 prod 面不 light、非 gate 不 high);TDD 紅→綠
---
# 2026-07-22_install全域hook同步

全域機器自癒缺口修法落地。spec：[[Projects/install全域hook同步_計劃]]。緣起：別台只全域裝 lumos 的機器 pull 後全域 Stop 舊註冊仍彈訊息（`install` 不碰全域、`update` 綁專案跑不了）。

- 測試：`t_install_global_hook_sync` 9＋既有 install/merge/prune/copy-list 迴歸 → 全套 1335 綠。
- 修法：抽 `_sync_global_claude(src_repo)`（copy 現役 hooks＋刪撤除 hook 殘留＋跑 merge prune 懸空）；`cmd_install` 尾端呼叫（來源 repo 自身）、`_install_hooks_py` ②③委派消雙寫。
- 同步：`Issues/hook卸載殘留註冊` 補殘尾 KEY、漂移守衛 `t_hook_copy_list_completeness` 改指 `_GLOBAL_CLAUDE_HOOKS` 常數新真相源。
