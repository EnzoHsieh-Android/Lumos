severity: minor

## F1 度量式撤除條件在沒有本機帳的機器上會把例行事件數成 0
severity: minor
blocking: 否
引句:「# 本機帳的時間不該讓暖機護欄提早放行;只有本機帳時 oldest 為 None,照暖機規則不判」
file: `scripts/lumos:3973`、`scripts/lumos:3978`
未能重現(沒有實際 RULE 帶度量條件可驗;grep 全 vault 只有計劃文提到 `retire:度量` 寫法,沒有生效中的 RULE)。
1. 某 RULE 寫 `[retire:度量 note-shape.hinted == 0 近4週]`(或 `<` 閾值),note-shape/hinted 屬 _GOV_LOCAL_PAIRS,分流後只進本機帳。
2. 另一台機器或新 clone 跑完整 doctor(S18):本機帳不存在,evs 只來自版控帳。
3. 版控帳 `oldest` 是分流前的舊事件,暖機護欄(oldest > cutoff)放行,cnt 對本機類種類恆為 0,`==0`/`<N` 判成「成立,這條限制該撤」。
4. 同機器依 doctor 提示刪掉本機帳(「太大的可以直接刪,只影響本機統計」)也會翻一樣的判定,這句「只影響統計」不完整。
目前沒有生效的度量式 RULE,所以還沒傷到人;但 `_metric_gate_off` 與這條路徑都假設事件在版控帳讀得到。

## F2 doctor 的本機帳提醒漏掉「已被追蹤」這個最壞情形
severity: minor
blocking: 否
引句:「if not tracked and ign == 1:」
file: `scripts/lumos:1321`(新函式 _local_ledger_doctor_msgs,diff 內);升級路徑 `scripts/lumos:20812`、`scripts/lumos:21030`
1. 消費專案團員 pull 到新版 vendored `scripts/lumos`,但沒跑 `lumos update`(忽略規則只在 _vendor_toolchain → _init_additive_setup → _ensure_docs_gitignore 補)。
2. 他第一次 commit/doctor 就寫出 docs/.governance-local.jsonl,未被忽略。
3. 若此時有人 `git add -A` 把它提交進去,檔案變 tracked;`tracked` 為真,條件 `not tracked and ign == 1` 為假,doctor 不再提醒,而後每次例行操作都弄髒版控檔,正是這分支要消除的現象,且 doctor 沒有警示。(只有「未追蹤且未忽略」才會提醒。)
4. 補充:`_ensure_docs_gitignore` 只認 `root/"docs"`,standalone vault 佈局(`_vault_in` 的 d 即 vault root,ledger 在 vault.parent)不會被補,但屬舊有佈局限制,doctor 仍會因 check-ignore 回 1 而提醒。

## 整合鏡頭逐項結論(非 finding)
- 其他仍讀 `.governance-log.jsonl` 的地方逐處核對,全部讀的是不在名單上的閘:`scripts/lumos:1250` 與 `:10313`/`:11261`(design-loop rewrite/converged)、`:12482`(fix-check)、`:25705`(lint-new fail-open)、`:42482`/`:43458`(code-loop)、`:2341`(ledger 大小/成長率,讀檔尾,只看版控帳尺寸,分流後成長率下降不會誤報 fast)。無一讀名單內的 (gate,kind)。
- 其他直接 open 寫帳者:`scripts/lumos:42586` 與 `:43416`(code-loop 留痕、dispositions)本就該留版控,未分流正確。
- `_render_gov_nags`(`scripts/lumos:8161`)吃 cmd_gov 合併列,doctor-run/warned 兩本合讀,正確。
- hooks(pre-commit/pre-push/post-commit)、`.github/workflows/ci.yml`、skills、README、docs/*.md:沒有寫死舊行為的 grep 或讀法;僅 `skills/lumos-project-notes/reference.md:61` 已同步。
- usage-log:全 repo 只有寫入點,無讀者,凍結舊檔無影響。

## pitfalls manifest 逐條判定
- test_lumos.py:38466 E702:誤報。該行是舊程式(git blame 0e715a45c,不在本 diff)。
- scripts/lumos:1454(_gate_event 的 open):誤報。with 區塊,路徑改為二選一仍在 with 內。
- scripts/lumos:1531(_append_governance_log 的 open):誤報。with 區塊;兩本各自 try/except OSError 吞錯,與舊行為一致。
- scripts/lumos:21064(_ensure_docs_gitignore 的 open "ab"):誤報。with 區塊,OSError 回 []。

## 圖譜鏡頭
派工尾端沒有附固定席筆記(未收到 LUMOS-IMPACT 內容),無法逐條對照節點合約;程式內自述的合約「code-loop、fix-check、design-loop 不得進名單」經核對成立,並有 t_gov_split_pairs_drift 釘住。

## 已走過沒問題的範圍
_gov_routes_local 兩支寫入器共用判定與型別防呆;_append_governance_log 兩本分寫、各自吞錯;cmd_gov 兩本載入與 loaded 名稱;spec-gate 比例段兩本排序後者勝;_BOOKKEEPING_FILES 與 cochange 排除表新增本機帳;_ensure_docs_gitignore 對 CRLF/無尾換行/不存在檔的處理;update 路徑經 _vendor_toolchain 會補忽略;測試改兩本合讀的 helper。

整合面沒有讀者被分流後讀空,只剩兩處不致命的邊角:度量條件在缺本機帳的機器上會數成零,以及 doctor 對已被追蹤的本機帳不提醒。
