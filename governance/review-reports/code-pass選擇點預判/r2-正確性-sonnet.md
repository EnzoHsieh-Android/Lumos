severity: minor

## c1 「沒有遠端」放行分支沒有任何測試守,改壞照綠
severity: minor
blocking: 否

引句:「        print(f"{P} 沒有遠端,選擇點留給推送前判")」
file: `scripts/lumos:73413`(`_codeloop_pass_choice`,修後版 826ce8451)

失敗場景:
- 輸入是沒設任何 git remote 的 Kotlin 專案(本機專案、首推前)。這時 `_lens_default_remote` 回 None,走到 `return True` 放行。
- 我在 826ce8451 的獨立 worktree 把這個 `return True` 改成 `return False`,跑 `python3.14 scripts/test_lumos.py -k codeloop_pass_choice`,結果 `24 passed, 0 failed`。
- 原因是四支新測試的夾具都先 `git remote add origin`(`_cpc_repo`)。S12 只列 detached 與沒有 kotlin 平台,沒有「沒有遠端」。
- 改壞的後果是 pass 回 False 但 `bad` 清單是空的:沒有擋下訊息、不寫留痕、pass 失敗卻說不出原因。本地專案就整個無法記通過。

歸因:未判定。這是新增程式的覆蓋缺口,修前版 ccca94927 的程式也沒有對應測試。
- 修前、修後兩版對「沒有遠端」的改壞都沒有測試會紅。
- 修後版用 `return False` 的改壞,實跑 24 全綠。

## c2 多個遠端且沒有 origin 時印「沒有遠端」,而且預判整個跳過
severity: minor
blocking: 否

引句:「    remote = _lens_default_remote(rr, None, None)」
file: `scripts/lumos:69981`(`_lens_default_remote`:只有一個遠端或有 origin 才回值,否則 None)

失敗場景:
- 輸入是有 `fork`、`upstream` 兩個遠端、沒有 origin,且目前分支沒設 `branch.<名>.remote`。
- 我實跑 `_lens_default_remote`,回 `None`,於是 pass 印「沒有遠端,選擇點留給推送前判」並放行。
- 事實上有兩個遠端,訊息錯了。
- 預判整個沒做,真推送時才被擋,正是「pass 放行、推送前擋下」的分歧,而且訊息沒教救法。

歸因:有證據的原有漏查。`_lens_default_remote` 是既有函式,這個呼叫與訊息在修前版 ccca94927 就有,修補沒動這段。
- 修前、修後兩版對這個輸入的結果相同:都印「沒有遠端」並放行。

## 三問與已驗主張(claim / input / expected / case_source / before / after / attribution)

**G1 repair:分支名含斜線、增量只算新增那行。**
- input:`feat/sit` 已推過,本機追蹤 `refs/remotes/origin/feat/sit`,再加一行。
- expected:只列新增那行。
- case_source:`t_codeloop_pass_choice_range`。
- after:實跑通過,24 全綠。
- before:未驗。我沒有跑修前版,也沒有修前測試可比,原因是修前沒有該案例。
- 判定:已驗修後行為成立。因果(修補造成)未判定。

**G1 preserve:detached、沒有 kotlin 平台。**
- case_source:`t_codeloop_pass_choice_skips`。
- after:通過。
- before:未驗。

**G2 repair:印推送前原文加 pass 出口。**
- case_source:`t_codeloop_pass_choice_blocks`、`t_codeloop_pass_choice_survived`。
- after:通過,含「先跑 lumos choice-kill」「不用先提交」「要先提交才算」。
- 備註:修後版印的原文裡,`缺紀錄` 的處置句仍寫「提交治理帳」,與 pass 出口的「不用先提交」同時出現,靠出口澄清。這是文字張力,不是錯誤。

**G2 preserve:push 的訊息與事件不變、push 與 pass 各記一筆。**
- case_source:S9(`t_codeloop_pass_choice_blocks`)。
- after:`被擋 2 筆(推送 1、pass 預判 1` 通過。
- 舊帳沒有 site 欄,`t_gov_stats_choice_kill` 的 S22 通過,算推送。

**G3、G4 repair。**
- 測試已拆成四支,名字互不為子字串。
- after:`-k codeloop_pass_choice` 剛好挑到 4 支,各 18 到 49 秒。

**G5 文件類。**
- 筆記 pitfalls-code-loop〈代碼審記通過前的選擇點預判〉寫明 pass 直接呼叫 `_choice_push_round(site="pass")`,與程式一致。

**鏡頭 4:pass 與推送前判同一件事。**
- 帳來源不同:pass 讀工作目錄,推送前讀被推版本。
  - 這個分歧是設計內。S2 實證:紀錄沒提交時,pass 過、推送前擋缺紀錄。
  - 訊息有教「紀錄跟帳本一起提交」。
- 範圍起點:同一支 `_push_range_start`。
  - 追蹤分支缺失時多看已推過的提交,是多擋、不少擋。
- 我另驗到:追蹤分支缺失、且頂端已在主線時,範圍是 `0000..tip`,`git diff` 跑不起來。
  - pass 與推送前同樣走「算不出來只提醒、記 unverified」,沒有分歧。
  - 這是原有行為,且失敗開放,不報。

**固定席節點(逐條判)。**
- bound-tests-gate、pitfalls-code-loop、guard-kill、design-loop、測試假綠形態、lumos-cli-read:不影響。diff 沒動那些合約的對象。
  - 新增 `site` 預設 `push`,推送路徑行為不變。
  - 事件多的 `site` 欄位,舊讀者看不到、不受影響。
- 測試假綠形態:新測試以斷言驗行為。唯一缺口是 c1。

**未驗範圍。**
- 沒跑全套。
- 沒跑 Gradle 或真 ast-grep,只用測試夾具的假 ast-grep。
- 沒驗併發寫帳。
- `_lens_default_remote` 裡 `--short` 遇同名 tag 的情形,只靠讀碼推斷,未實測。

總結:最高嚴重度 minor
