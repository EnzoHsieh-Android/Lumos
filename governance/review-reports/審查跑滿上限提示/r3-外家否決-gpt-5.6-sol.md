severity: major

## F1 S11 與既有治理帳收尾寫入直接矛盾
severity: major
blocking: 是 — 照 spec 同時實作「帳本行數不變」與「不改既有判定／行為」不可能；實作者必須任意破壞其中一份合約。
引句:「當這一段印出,治理帳與審查帳的行數應不變」
file: `scripts/lumos:18583` 處置閘 PASS 後既有行為會以 `_loop_gov_mark(..., "converged", ...)` 寫治理帳；達上限且印出提示的 PASS 場景必增加一行。
file: `scripts/lumos:10673` `loop next` 判定收斂時也會先寫 `converged`；`scripts/lumos:10677` 原有 `cap-reached` 路徑同樣寫帳。
file: `scripts/lumos:8660` `converged`、`cap-reached` 是 `loop list` 判斷迴圈已關門的既有事件；為滿足 S11 而刪寫入會把已收尾迴圈重新報成開著。
重現：建一個已達上限且處置閘 PASS 的新迴圈，記錄呼叫前後 `docs/.governance-log.jsonl` 行數，再執行 `lumos loop status <id> --disposal --spec <檔> --repo <根>`；現行合約要求行數增加，S11 卻要求不變。S11 必須改成「提示本身不額外寫帳，既有收尾寫帳照舊」，測試也應只斷言沒有新增第二筆事件。

## F2 r2 新增的 loop next 熔斷承諾在正常帶 --spec 路徑仍不可達
severity: major
blocking: 是 — 照 spec 實作只會把提示掛進 `emit`；使用手冊與 `--help` 指向的完整 `loop next --spec` 路徑會在到達 `emit` 前退出，累計已超過 20 條仍不印熔斷提示。
引句:「當各輪折入累計超過 20 條,loop next 與處置閘都應印建議拆小改動,不論輪數」
引句:「它被擋下提早結束的路徑不印」
file: `scripts/lumos:10663` `loop next` 帶 `--spec` 時仍把新式多席帳委派給舊 `_loop_status_panel`；收到 rc=2 後在 `scripts/lumos:10669` 直接返回，尚未呼叫 `emit`。
file: `scripts/lumos:8284` `_loop_status_panel` 對 2026-08-26 起的新迴圈固定拒判並返回 2，指路改問處置閘。
file: `docs/.canary-log.jsonl:1870` 本迴圈 r1 的 carrier 已記折入 17 條；`docs/.canary-log.jsonl:1890` r2 又折入 17 條，累計 34 條，已符合 S8 熔斷條件。
重現：執行 `python3 scripts/lumos loop next 審查跑滿上限提示 --spec docs/lumos-toolchain-knowledge/Projects/審查跑滿上限提示_計劃.md --repo /Users/enzo/harness/lumos-toolchain`，現況 rc=2 且不會進任何可附加 `cap_hint` 的輸出出口。拿掉 `--spec` 才會得到 `gate-pending`，但完整標準用法正是帶 `--spec`。r2 雖把功能改成「任何階段附提示」，仍未解掉主要呼叫路徑；S8 與「提早結束不印」也互相衝突。

## F3 三個月零觸發的退場條件沒有可到達的複查點
severity: minor
blocking: 否 — 不影響提示演算法，但退場承諾按文件流程不會被執行。
引句:「②三個月內零次印出(沒人跑過上限)。」
引句:「REVISIT:2026-10-26 回看這一個月跑滿或熔斷時印的建議」
唯一接電的複查日在上線後一個月，當時無法判定「三個月內零次」；文件也沒有三個月後的 `REVISIT` 或事件入口。到 2026-12-26 即使始終零觸發，doctor 不會提醒檢查 RETIRE-IF ②。

實務隱患逐類：

- 併發：有觸及；讀 append-only 審查帳，但不新增寫入路徑，沿用既有整檔讀取與壞行處理。
- 效能：有觸及；既有讀取先篩出單一迴圈，再每輪呼叫一次 `_review_yield_round`，不讀凍結審材，沒有新增無界工作量。
- 金流：無；只處理本機治理資料與終端輸出。
- 對外送出：無；沒有網路或外部服務呼叫。
- 不可逆：無新增不可逆動作；既有治理帳收尾寫入仍是 append-only，且正是 F1 不能假裝不存在的行為。
- 守衛面：有；提示位於 `loop next` 與處置閘，會影響人是否停止審查。S1/S2 對 phase、判定與退出碼的保護方向正確，但 F1、F2 尚使合約不可同時兌現。
- Python 通用風險：無 async、外呼、秘密、反序列化或 shell 拼接新需求；本案是同步零依賴 CLI 的純讀取與呈現邏輯。

已看,無: 投稿檔與 `docs/lumos-toolchain-knowledge/Projects/審查跑滿上限提示_計劃.md` 逐位元相同，沒有副本漂移；〈一句話〉、〈適用範圍〉、〈做法〉、S1–S10、〈回退〉、〈誠實界線〉及 r1/r2 修正紀錄除上述項目外均與程式現況相容。`_review_yield_round`、`_loop_anchor_tier`、`_TIER_PARAMS`、`_panel_retired_for` 均存在且語意吻合；空輪確實由各席 `findings == 0` 判定，carrier 的折入數取 `folded_set`，最高嚴重度值域與排序存在。`loop next --json`、`loop status --disposal`、`canary record`、`quote-check`、`loop escape`、`gov`、`loop replay` 的旗標均以實際 `--help` 核過。所有文件交叉引用存在；指定的 r1/r2 intake 已讀，未重報其中已知且已折平的舊項。`Systems/loop-convergence-recording` 沒有登記 ★INVARIANT★ 合約；新增純輸出本身不破壞該節點，唯獨若為解 F1 移除既有治理帳收尾事件，就會破壞它及 `loop list` 宣稱的行為。

最嚴重 severity: major，blocking 共 2 條。
