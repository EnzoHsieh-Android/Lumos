severity: minor

# 正確性(修補鏡頭)第二輪報告

白話版:這輪修補大致站得住。我造了一個小 repo,把批次比對、符號連結、子模組、目錄與檔同名、`--out` 各種路徑都實際跑過,沒有找到會讓結果出錯或讓人被誤導成「沒問題」的洞。留下三個行為上的小缺口,都不擋。

## 驗過、無 finding 的部分

- **批次 ls-tree 的基本比對**:已讀,無 finding。
  - 實測提交裡只有、會談目錄沒有的檔和節點,分類正確(只在提交裡 / 找不到 / 不合字元集)。
  - 目錄 `scripts/dirname` 不會被當成檔列出來。
  - 提交裡的符號連結(mode 120000)被排除,不會被當成一般檔。
  - 子模組(160000)被排除。
  - 同一路徑不可能同時是目錄與檔,所以沒有同名衝突。
- **`_vault_node_path` 沒有誤擋合法連結**:已讀,無 finding。實測含空白(`Systems/空白 名`)、中文名、片假名、`Issues/事故一` 全部正常附上。`Systems/../../x` 被擋並計入「指到圖譜外面」。
- **`--out` 對手冊寫的用法**:已讀,無 finding。實測下列寫法都通過。
  - 裸檔名 `rN-snapshot.md`
  - `governance/review-reports/x/r1.md`(含自動建目錄)
  - `./sub/../a.md`
  - 以 repo 根開頭的絕對路徑

  這些會被擋:`/tmp/...`、`../outside.md`、`.git/x.md`、`.GIT/x.md`、符號連結上層。
- **其他修補**:已讀,無 finding。
  - `_write_bytes_atomic` 任何例外(含 BaseException)都清暫存。
  - `_load_hook_file` 關 bytecode,缺函式回原因。
  - 入口設的 `GIT_GRAFT_FILE=/dev/null/...` 在 git 2.39 下 log、rev-list、commit 都不吐警告。
  - `_mark_event` 統一用 `except Exception`,符合註解的意圖。
- **be-api-compat**:`--json` 只新增 `scan_truncated` 欄位,沒有改名或刪欄位。`_nodehome_landing_sizes`、`_lens_spec_linked`、`_lens_spec_code_files` 的回傳形狀改了,但 repo 內只有 `cmd_dispatch_lens_spec` 一個呼叫端。舊呼叫端不受影響。
- **be-authz**:這兩條命令都是本機唯讀或寫 repo 內檔案的命令列工具,沒有端點,不適用。路徑越界已由 `_vault_node_path` 與 `_spec_freeze_out_path` 把關。
- **資料狀態五問**:
  - 空:提交裡沒有節點時 `cidx` 是空 dict(不是 None),節點全歸「找不到」,說明有講。
  - 部分失敗:ls-tree 逾時或失敗回 None,印「算到一半」。
  - 重複:`seen` 去重。
  - 過期:被 gc 的提交走 `spec_rev_missing`。
  - 併發:`--out` 是原子換檔,同時兩次寫,後者勝出,可接受。

## Finding 1:預算被 impact 吃光後,落點段只剩一行空標題

severity: minor
blocking: 否 — 說明行有講「算到一半」,不會讓審查員誤以為落點不存在。
引句:「landing, tr_land = _nodehome_landing_sizes(root, vault_rel, text, commit=full, cidx=cidx, deadline=deadline)」

問題:落點是便宜的記憶體比對,卻排在最貴的 impact 迴圈之後,共用同一個 `deadline`。impact 先把預算用完,落點迴圈一開始就 break。輸出裡 `落點現況(計劃的 lands_in;…):` 後面一個項目都沒有。`landing` 計數是 1,看起來像有東西。同一份輸出的標頭又寫著「超預算沒算」。

失敗情境(實測):把 `_LENS_SPEC_BUDGET` 調成 5 秒,計劃寫 3 個程式檔、2 個 lands_in。
- 預期:落點兩篇照列。
- 實際:`skipped_files` 是全部 3 個,`scan_truncated: True`,落點只剩空標題行。

預設 30 秒時,本 repo 一次 impact 約 3.5 秒,3 個檔約 10 秒,碰不到上限。但 impact 較慢的後端大 repo 會碰到。

建議:落點和連結(便宜的)先算完,最後才讓 impact 用剩餘預算。標題行只在至少有一項時才印。

佐證:``file: `scripts/lumos:49556` ``

## Finding 2:計劃裡寫成 NFD 的名字,提交寫法歸「找不到/錯字」,工作樹寫法卻找得到

severity: minor
blocking: 否 — 只影響附帶資訊的完整度,說明還有提示「可能是錯字」。
引句:「    if rel not in cidx:」

問題:批次比對是字串逐字相等。macOS 的 git 會把路徑存成 NFC,計劃內文若是 NFD(例如從 macOS 檔名複製來的)就比不到。
- 工作樹寫法:APFS 不分正規化,`is_file()` 找得到。
- 提交寫法:同一個名字被歸為「找不到」。

計劃「路徑」有檢查 NFC,但內文的連結、落點、程式檔候選沒有。

失敗情境(實測):提交裡有 `Systems/ガ2.md`(NFC),計劃寫 `[[Systems/ガ2]]` 的 NFD 形式。
- 預期:列為「只在那個提交裡」。
- 實際:被計入「N 個連結在…都找不到(可能是還沒提交的新節點或錯字)」。

程式檔候選(`scripts/Café2.py` 的 NFD 寫法)連「找不到」都不計,完全沉默。

建議:查 `cidx` 前先把候選與節點名做 NFC 正規化。

佐證:``file: `scripts/lumos:49473` ``(`_nodehome_landing_missing`)、``file: `scripts/lumos:49432` ``(`_lens_spec_code_files`)

## Finding 3:`--out` 指到會談的另一個工作樹會被拒,而這正是此功能的典型情境

severity: minor
blocking: 否 — 錯誤訊息講明「快照放 repo 裡」,有繞法(寫進計劃所在 repo 再複製)。
引句:「outp = _spec_freeze_out_path(root, cwd, str(out))」

問題:spec-freeze 要在計劃所在的工作樹跑,`root` 就是那個工作樹。編排者通常想把快照放進會談工作樹的 `governance/review-reports/...`(卷證在那裡),那是另一個 repo 根。範本只寫 `--out {rN-snapshot.md}`,沒說必須放計劃所在 repo。

失敗情境(實測):在 repo A 跑 `spec-freeze <計劃> --out /tmp/zz.md` 或 `--out ../outside.md`。
- 結果:rc 2,`out_outside_repo`。
- 對照:裸檔名會把快照寫進計劃所在工作樹的根目錄,留下一個未追蹤檔。

建議:範本與手冊直接寫「`--out` 要在計劃所在 repo 底下,再自己複製到卷證」。

佐證:``file: `scripts/lumos:49824` ``;範本 ``file: `skills/lumos-design-loop/templates.md:40` ``

## 附註(不獨立成條)

- 「算到一半」那句固定寫「超過時間預算」,但 `cidx is None` 也可能是 ls-tree 失敗(非逾時)造成,原因說得不精確。
- `_lens_spec_code_files` 在湊滿 5 個程式檔後直接 break,後面的候選不會被看到,也不算「算到一半」。這個上限是舊的,只是說明沒講。

實驗環境已刪除。

最高等級 minor,blocking 0 條。
