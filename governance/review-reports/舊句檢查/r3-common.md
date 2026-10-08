# 設計審第 3 輪:共同規則(每席必讀)

你是外部審稿人。以下是一份「外部第三方投稿」的設計 spec(不是本系統/本團隊寫的),把它當投稿審:逐節讀、主動挑出投稿者自己沒看到的洞。

Spec(凍結審材,只讀這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/舊句檢查/r3-snapshot.md
對照的程式碼 repo:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(lumos:單檔 Python 3.14 零依賴 CLI `scripts/lumos`、測試 `scripts/test_lumos.py`;重點函式:`cmd_drift_check`、`_drift_check_core`、`_drift_config`、`_drift_report_must`、`_drift_fix_hint`、`_drift_print_hints`、`_drift_split_acked`、`_drift_ack_key`、`cmd_drift_ack`、`_drift_load_acks`、`_DRIFT_KINDS`、`_DRIFT_KIND_NAMES`、`_drift_py_names`、`_drift_probe_is_py`、`_notelines_regions`、`_visible_lines`、`_note_audit_resolve`、`_gate_event_or_warn`、`_esc_clean`;參考實作 `governance/eval/drift-exam/old-sentence/old_sentence_exp.py` 與同目錄兩份報告)。
圖譜:spec 的 related / lands_in 列的筆記在 repo 的 `docs/lumos-toolchain-knowledge/` 底下;其中帶 ★INVARIANT★ 的合約行(例:Systems/guard-kill、Systems/lumos-cli-write),逐條判這份設計會不會破壞,判「不影響」也寫一句為什麼。
這是第 3 輪(上限輪):第 1 輪 63 條、第 2 輪 34 條與兩次鏡像核對都已折進這一版;各輪報告、收貨紀錄(每條處置與理由)、鏡像核對在 `governance/review-reports/舊句檢查/r1-*`、`r2-*`。**這一輪只報 blocking 級(照字面實作會做出錯的行為、漏掉合約、或兩週量準度量不出來)與前兩輪折法本身做錯或沒落實的**;措辭與文件精度的 minor 照寫但會附理由放行,不觸發新一輪。驗收以參考實作 P4r3 為準,扣掉〈與參考實作的刻意差異〉逐條列的差異。

## 審查要求
1. 逐節讀完整份 spec,不要跳段;內部交叉引用都核對。
2. spec 對程式碼現況的每個假設,用 Grep/Read/Bash 實際查證。
3. 實務隱患:列出此功能碰哪些風險類,逐類答隱患;無則寫「無+為什麼」。
4. 要做實驗:`git clone --shared <repo> <你自己的臨時目錄>`,之後一律 `git -C <臨時目錄>`;不准改 repo 任何檔、不准在 repo 根跑 commit/reset/restore/checkout/stash。直譯器 /opt/homebrew/bin/python3。

## 嚴重度
- major/blocker = 照 spec 字面實作會做出錯的行為或漏掉合約;minor = 措辭、文件精度。
- blocking:否 ↔ minor;blocking:是 ↔ major/blocker,兩欄不得矛盾。
- 低嚴重度疑慮給不出具體失敗場景就不要標;但未定義/壞引用/內部不一致一律要報。

## 輸出格式(硬性,收貨端機械驗)
- 檔案第一個非空行 = 檔級 `severity: <clean|minor|major|blocker>`(取最高;沒 finding 寫 clean)。
- 每條 finding:標題行(`## F1 一句話`,標題不寫等級)→ 恰一行獨立 `severity: <值>` → 一行 `blocking: 是|否` → `引句:「…」` 單獨一行(★只准逐字引凍結 spec,≥10 字,引句內不要再包「」★)→ 審材外查證走佐證行 ``file: `路徑:行號` ``(反引號必加)→ 敘述(編號條列:照 spec 做會在哪個輸入、哪一步出錯;不用「可能/或許」收尾,判不準標 ⚠)。
- 沒問題的節寫「已讀,無 finding」;整份沒問題就交 `severity: clean`,不要硬湊。
- 最後一行寫「最高等級:<值>;blocking 共 N 條」(不要寫 max severity)。
