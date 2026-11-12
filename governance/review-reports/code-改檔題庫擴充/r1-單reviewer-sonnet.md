severity: minor

審完整份 diff,並跑了 `python3.14 scripts/test_lumos.py -k goldset`(39 支全過)。沒有 blocker 或 major。下面是兩條 minor,之後是本案鏡頭與 manifest 的逐項回答。

## Findings

### 1. 〔minor〕計劃與筆記寫「不帶 `--per-file` 就是舊行為」,程式不是
severity: minor
blocking: no
`governance/eval/build_goldset.py` 的 `edit_cases` 不管有沒有帶 `--per-file`,都會先過 `_hook_would_fire` 和新加的 samples/fixtures 過濾。

走一遍:輸入是 git 歷史裡改過 `.github/workflows/ci.yml` 或 `governance/eval/x.jsonl`。
- 舊程式:`.yml` 不在任何排除規則裡,會出題;`.jsonl` 因路徑含 "eval" 也會出題。
- 新程式(預設 `per_file=1`):`_decide_one` 副檔名不在 `CODE_EXTS`,回 None,不出題。
- 同一個預設參數,同一段歷史,取出的題目集合變了。

下面這幾處的措辭都不準:
- 計劃〈回退〉
- 〈依據來源〉表的「不帶選項時行為不變」
- `Systems/retrieval-ranking` 的 WHY:「預設 1=舊行為」

只有「每支檔一題」這條維持舊行為,出題母體已經變了。
S3 的 `[keeps]` 只釘「既有題與標註不動」,沒有說題目集合不變,所以條款本身沒錯,錯在上面幾處說明。
這會讓照〈回退〉操作的人以為把 `--per-file` 拿掉就回到舊出題母體,實際不會。

引句:「`--per-file` 不帶就是舊行為;要整段拿掉,把那道判斷與兩個選項的程式移除即可。」

另外,`--force-full` 路徑(`build_goldset.py:325` 的 `edit_cases(want * 2)`)也套用了新母體。計劃沒提這條,但方向一致,不算錯。

### 2. 〔minor〕抽題端的片段去重與 `_run_append` 的預先過濾沒有測試,驗證紀錄的「各拿掉一次都翻紅」說過頭了
severity: minor
blocking: no
`t_goldset_file_quota_cap` 的抽題端只用 `src/hot.py` 三次不同的新增行。
- `edit_cases` 裡的 `if (f, delta) in deltas: continue` 從沒被走到。把它拿掉,兩條抽題端斷言照綠(`len(hot)==2`、兩個不同提交)。
- `_run_append` 整個函式 repo 內沒有任何測試呼叫(grep `_run_append` 在 `scripts/test_lumos.py` 無命中)。預先過濾那行拿掉,最後一道把關(`append_edit_cases`)仍會擋下,所以資料不會壞。

具體後果是:題庫已有熱門檔滿額時,`--append 20 --per-file 3` 的 `pairs` 會被已滿額檔的候選占掉名額,每個多花約 14 秒跑兩次影響查詢。最後被丟掉,實際加的題少於 20,而且是靜默的。

Verification 筆記寫的是「新加的五道判斷…各拿掉一次,測試都翻紅」。那五道裡對應抽題端片段去重的這一道,測試沒有覆蓋它。

引句:`# 先在這裡扣掉名額已滿與重複的,省下建池(每題兩次影響查詢);最後把關仍是 append_edit_cases 的同一套判斷`

## 本案鏡頭

1. **掛鉤腳本當模組載入**:沒有 import 時的副作用。`scripts/hooks/claude/impact-hook.py` 模組層級只有 import、常數、函式定義和編譯好的 regex;讀 stdin、`_clean_path_env` 和寫事件都在 `if __name__ == "__main__":` 底下。`spec_from_file_location` 加 `exec_module` 不會觸發它。載入後的模組快取在 `_HOOK_MOD`,不會重複載入。
2. **既有題名額與去重**:兩處都有算進去。
   - 題庫的 `commit` 欄實測全是 8 碼。`edit_cases` 回傳 `cur_sha[:8]`,`_edit_quota` 也取 `[:8]`,8 碼對 40 碼不會對不上。
   - `_run_append` 預先過濾:`per`、`seen_commits`、`seen_deltas` 都由題庫現有題初始化,新選中的題會即時更新 `per`。走一遍:題庫已有 F@A,`per_file=3`,`edit_cases` 回 F@A、F@B、F@C。A 被擋,B 加入使 `per` 到 2,C 再加入到 3,總共 3 題,沒有超出。
   - `append_edit_cases` 最後把關用同一套 `_edit_quota`,測試有釘。
   - 候選上限 `n*4 + sum(per.values())*per_file` 夠大,足以容納被題庫現有提交占掉的候選。
3. **計劃〈條款〉與程式**:S1、S2 和程式一致,S3 的「不就地改輸入、空池不進卷」也還成立。不一致處就是上面 finding 1。

## manifest
3323 條全是 `lint:ruff` 的舊告警,依派工詞不逐條判。

## 圖譜鏡頭
這次沒附固定席節點(鏡頭計算超時),沒有合約行或殘留決策可逐條答。diff 內有三處圖譜相關改動:
- `Systems/retrieval-ranking` 新增兩條 WHY,帶 `[test:]` 綁定且測試存在,不影響既有合約。
- `Issues/圖譜筆記本身會洩漏標註答案` 把 REVISIT 加上 `[closed:]`,另加 2027-02-13 的 REVISIT。
- `Projects/改檔題庫擴充_計劃` 的 `lands_in` 指向 `Systems/retrieval-ranking`,該節點 `about_code` 已新增 `build_goldset.py`,符合「每支檔有家」。

## 角色卡
- **be-api-compat**:`edit_cases`、`append_edit_cases`、`_run_append` 新增的參數都有預設值,CLI 新旗標也有預設,舊呼叫端不用改。`edit_cases(...)` 在 repo 內的呼叫端只有 `_run_append` 和 `--force-full` 那一處(`build_goldset.py:325`)。
- **be-authz**:不適用,這份 diff 沒有端點。

最高嚴重度:minor
