severity: clean

範圍說明:這份差異(e8f17913..123aaf47)是「乙:條件式回頭條件」代碼審 r1 的修法差異,集中在 `scripts/lumos` 的
`_DriftProbeTree`/`_drift_probe_*`/`_notelines_*`/`_nodehome_name_status` 一帶與 `scripts/test_lumos.py` 的回歸測試,
另有三份圖譜筆記與一份考卷改寫檔(純資料)。以下依派工六類逐一檢查。

## 1. 不可信輸入流到危險操作(命令/路徑/模板注入、反序列化、eval 類)

已看,無 finding。重點查了三處:

- `ast.parse` 解析被推送的程式檔(`_drift_py_names`,對應 `_drift_probe_is_py`/`_DriftProbeTree._defines` 呼叫路徑):
  `ast.parse` 只建語法樹、不執行任何程式碼,不是 `eval`/`exec`/`compile(...,'exec')` 那類會跑進程式的路徑,推不出任意
  程式碼執行。它對超深巢狀輸入可能丟出 `RecursionError`(或更早的 C 堆疊問題)而未被 `except (SyntaxError, ValueError)`
  接住,但這是崩潰/資源耗盡類(DoS),不是「執行任意碼/資料外洩/繞過閘」,照派工說明歸給併發席,這裡不報。
  引句:「try:\n        tree = _ast.parse(txt)\n    except (SyntaxError, ValueError):」(r2-snapshot.patch 第 521-523 行)

- 條件值裡的路徑被拿去讀磁碟或組 git 參數(`_probe_norm_value`、`_DriftProbeTree.one`/`_read`):`file`/`symbol`/`test`
  條件的路徑段只做 `_posix_norm`+NFC 的字面正規化(不查檔案),真正要不要讀,一律先過 `path not in self.files: return False`
  這道白名單(`self.files` 來自 git ls-tree/ls-files,不含符號連結、子模組);符號連結另外在 `_drift_disk_list` 明白排除
  (`files = {p for p in allp if (base / p).is_file() and not (base / p).is_symlink()}`)。所以攻擊者在筆記裡寫
  `[when-file:../../etc/passwd]` 或帶 `..` 的 symbol 路徑,結果只會是「不在白名單裡 → False」,不會真的去讀 repo 外的檔。
  引句:「if path not in self.files:\n                return False」(r2-snapshot.patch 第 681-682 行)

- 工作目錄模式讀未追蹤檔(`_drift_disk_list`):新加的磁碟快照函式對符號連結明確排除、且只收
  `os.path.lexists` 為真的路徑,沒有解引用符號連結去讀 repo 外內容的路徑。
  引句:「files = {p for p in allp if (base / p).is_file() and not (base / p).is_symlink()}」(r2-snapshot.patch 第 560 行)

- 這份差異新增的全部 git 呼叫(`_ns_diff(root, "--text", base, tip)`、`_nodehome_git(root, "ls-files", "--others",
  "--exclude-standard", "-z")`)都是 argv list 呼叫(`subprocess.run(cmd + list(args), ...)`,非 `shell=True`),`base`/`tip`
  是先前已驗證過的提交 SHA(`_lens_full_sha` 只認 40 碼十六進位),不是這次推送內容裡直接抄出來的自由字串;逐一 grep
  這份 diff 沒有新增 `shell=True`/`os.system`/`eval(`/`exec(`/`pickle`/`yaml.load` 任一種。

## 2. 登入與權限:推送閘能不能被推送內容本身關掉或繞過

已看,無「這份差異新增」的 finding。`.lumos/config.json` 讀被推送頂端那個提交、推的人能在同一個提交把
`drift_check.gate` 改成 off 放過自己——這是既有已知行為,已經寫進 `Systems/存量漂移守衛.md` 的 RULE 行,帶了
`[since:2026-09-29][retire:...]`,是「代碼審 r1 資安席」上一輪已經記錄在案的缺口,不是這份修正差異新增或加劇的。
這份差異本身沒有動到閘開關讀取、`.lumos/config.json` 解析、或 `_gate_event_or_warn`/`_drift_report_must` 的擋放邏輯
(只改了 `_drift_report_must` 印的提示文字,擋/放的 rc 判定沒變)。
引句:「推的人可以在同一個提交把 drift_check.gate 改成 off 放過自己(代碼審 r1 資安席)」(r2-snapshot.patch 第 96 行,既有筆記行,非這次改動)

## 3. 密鑰與個資

已看,無 finding。新增/改動的列印路徑(`_drift_scan_print`、`_drift_report_must`)印的是筆記路徑、行號、截到 70 字的
筆記原文片段,跟修改前一致,不是程式檔內容本身;`_DriftProbeTree._read` 讀進來的程式檔內容只拿去做正則/AST 比對,
沒有任何新增的 print/log 把整份檔案內容或 git blob 印出來或寫進治理帳。

## 4. 加密與傳輸

已看,無 finding。這份差異不涉及任何網路呼叫、TLS、或加解密邏輯。

## 5. 執行邊界(hook/CI 執行不可信位置的檔;shell 插值;git 參數注入;讀 repo 外的檔)

已看,無 finding。

- shell 插值:diff 裡新增的 subprocess 呼叫全是 argv list 形式,沒有字串拼接成 shell 命令的地方。
- git 參數注入(以 `-` 開頭的值):新增的三處 git 呼叫(`_ns_diff(root, "--text", base, tip)`、`_drift_disk_list` 裡的
  `ls-files --others --exclude-standard -z`、`_notelines_range_cand` 裡帶 `--` 的 `_ns_diff`)參數不是從推送內容裡的
  自由字串直接接進來——`base`/`tip` 是驗證過的 SHA,`vault_rel` 前面已經有 `--` 隔開。`_DriftProbeTree.one`/`_read` 裡
  真正把「筆記裡寫的路徑」送進 git 的地方(`_nodehome_cat_blobs` 的 `f"{where}:{p}"`),`p` 一定先通過
  `path not in self.files: return False` 這道白名單,不會有以 `-` 開頭的任意字串被當成 git 參數。
  引句:「blobs = _nodehome_cat_blobs(self.root, [f\"{self.where}:{p}\" for p in todo], timeout=left)」(r2-snapshot.patch 第 626 行)
- 讀 repo 外的檔(符號連結、路徑穿越):見第 1 類的分析,`_drift_disk_list` 排除符號連結、`tree.files` 白名單擋掉
  `..`/絕對路徑類的條件值。
- hook/CI 執行不可信位置的檔:這份差異沒有新增任何「找到某個路徑就執行它」的邏輯(`ast.parse` 只是解析、不執行)。

## 6. 行動端

不適用,已看,無 finding。

## 總結

最高等級 clean,blocking 0 條。逐項檢查了 ast.parse 對推送程式檔的解析路徑、條件值路徑正規化後的白名單門檻
(`self.files`/`tree.files`)、工作目錄模式對符號連結與未追蹤檔的處理、以及這份差異新增的全部 git 子行程呼叫,
沒有找到可被利用的洞;唯一跟「推送閘能不能被自己內容關掉」相關的已知缺口是上一輪代碼審已記錄在案的既有問題,
這份差異沒有新增或加劇它。
