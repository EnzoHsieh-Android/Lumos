severity: minor

## F1 自動跑什麼的速查表沒補上推送前的漂移檢查
severity: minor
blocking: 否
引句:「推送時自動跑(2026-09-30 接線):`scripts/hooks/pre-push` 對每個要推的 ref、`.github/workflows/ci.yml` 在 push 事件的 drift check 那一步」
file: `skills/lumos-project-notes/commands/08-自動跑的.md:7`
1. 接手的人查「git push 前自動跑什麼」會翻到 08 的 pre-push 那一列,那列列了 anchor verify、全套測試、home check、note-shape、code-loop check、doctor --ci,沒有 drift check;CI 那一列也只寫「同 pre-push + code-loop check」。
2. 這個 patch 沒動 skills/,所以那份指令文件跟實際掛鉤不一致。commands/06 沒有 pre-push 閘門清單,不需要補;commands/04 第 12 列的 drift ack 已寫「推送閘每次都唸同一筆」,可用。
3. 具體後果:有人被擋下(block 模式)或看到 warn 提醒,回頭查「這是哪一道」,在 08 找不到。

## F2 CI 註解裡「前一版」沒有定義、句子不通
severity: minor
blocking: 否
引句:「前一版是 40 個 0 或本機找不到時,lumos 從跟主線的分岔點算(同 note-shape 那步,前一版原樣交給它)」
file: `.github/workflows/ci.yml:149`
1. 這段註解出現兩次「前一版」,全檔與圖譜沒有任何「前一版」的指涉,讀者會以為有舊版做法。
2. 從上下文看,要講的是「before 是 40 個 0 或本機找不到時,由 lumos 從跟主線的分岔點算」;「前一版」像是編輯時留下的殘字。
3. 純註解,不影響行為(測試 ⑦⑧ 全綠)。

## 已驗證沒問題(供參考,不算 finding)
- 重現:在我自己的 clone 跑 `python3 scripts/test_lumos.py -k t_prepush_and_ci_wire_drift_check`,12 項全綠。
- 擋下訊息教的指令能跑:`LUMOS_SKIP_DRIFT_CHECK=1 git push` 由測試 ④ 實際跑過掛鉤;`drift_check.gate` 設 warn 寫在 `.lumos/config.json` 與程式讀的位置一致;`lumos drift fix` / `lumos drift ack --kind` 由 check 自己印,子命令存在。
- 三篇筆記新寫的句子跟程式一致:
  - bound-tests-gate 的 WHY 說「_range 對新分支換成空樹」,對得上 `pp_range_for` 的行為;說「共用推送起點判法算分岔點、頂端已在主線就不查」,對得上 `_lens_push_base`;說「淺層 clone 由 lumos 跳過並記帳」,對得上 `_note_audit_resolve`;說「只認 rc1 擋」,對得上掛鉤的 `dr_rc -eq 1`。
  - 存量漂移守衛的 WHY「doctor 開頭會唸存量漂移檢查是 warn」,對得上 `_drift_gate_doctor_lines`(已接線且非 block 才唸)。
  - CI 全套測試在 drift 步驟前面,對得上 ci.yml 步驟順序(全套在 55 行、drift 在 149 行)。
- 沒有新寫程式行號引用、沒有無來源的 FACT/FLOW/DEP:新句都是 WHY/RULE/TEST 或一般說明行;`lumos lint` 三篇 0 問題,`note-shape --diff` 與 `home check --diff` 在 clone 上無輸出(通過)。
- `[test:t_prepush_and_ci_wire_drift_check]` 綁的測試存在於 patch 內。
- 上線標記:618ee85f 的 pre-push 沒有 "drift check" 字串,新掛鉤第一次出現在此提交;`_DRIFT_GOLIVE_MARK` 是子字串比對,標記行與註解都不會誤點更早的提交。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區 [事故]:不影響。drift check 段落插在 code-loop 分支與 tag 兩路之後、`impact_done` 之前,沒動分支名判斷與 `_rbranch` 路徑;那個事故是分支名判定盲區,這裡沒碰。
- Systems/存量漂移守衛 [家]:新加的 WHY、RULE 改動、about_code 兩條與掛鉤行為一致;RULE 行仍帶 since 與 retire 欄位,retire 條件「接進掛鉤與 CI」半數達成,寫法保留合理。
- Systems/每支檔有家:不影響。掛鉤的 home check 段落未動;新 drift 段落在它之後、無 continue 提早跳過。
- Systems/筆記內容閘:不影響。note-shape 那段沒動,新段落沿用同一套 rc 處理(非 1 放行)。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要有前置斷言):新測試 t_prepush_and_ci_wire_drift_check 有前置斷言(①先斷言 rc==1 且 code-loop 在 drift 前、SUITE 沒跑;⑧先斷言 body 非空才比 rc),不違反;翻紅釘寫在 docstring,我未逐一還原驗證。
- Systems/anchor-integrity ★RISK★:anchor-baseline.json 已隨 pre-push 與 test_lumos.py 兩個雜湊更新並改 note;符合該節點要求,不影響。
- Systems/lumos-cli-lifecycle、lumos-cli-read ★INVARIANT★:re-inject 與 search 排除 superseded 兩條合約都跟 pre-push 的 drift 段落無關,不影響。
- Systems/bound-tests-gate 與其他「只列名」節點(canary-audit、design-loop、guard-kill、slim-install 等):bound-tests-gate 是這次的家,已判如上;其餘只列名、與 diff 無牽連程式路徑,不影響。
- 規格閘 KEY(pre-push 在 code-loop check 之前多一段 spec-gate):新段落在 code-loop 之後,不衝突;bound-tests-gate 的 WHY 順序敘述與掛鉤實際順序一致。

最高等級:minor
