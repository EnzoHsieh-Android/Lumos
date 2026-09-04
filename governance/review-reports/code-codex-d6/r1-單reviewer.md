# code-codex-d6 r1 單reviewer 報告

審查材料:`governance/review-reports/code-codex-d6/r1-snapshot.patch`(逐 hunk 全讀,U10)。
角色:外部第三方 code reviewer,唯讀,不知編排者結論。

---

## Findings

### F1
severity: major
blocking: 是
file: `scripts/lumos:11358-11359`(對應 r1-snapshot.patch 內 `_install_codex_agent` 函式,新增區塊第 4-5 行)
引句:「d.mkdir(parents=True, exist_ok=True)」

`_install_codex_agent` 對 `CODEX_HOME/agents` 目錄直接呼叫 `d.mkdir(parents=True, exist_ok=True)`,沒有先判斷該路徑是不是「已存在但是檔案不是目錄」。Python 的 `Path.mkdir(exist_ok=True)` 只在目標**已是目錄**時吞掉 `FileExistsError`;目標若是一個普通檔案,仍會拋出未捕捉例外。而 `_sync_global_hooks`(呼叫端,同一支 diff 新增第 4 步)與其呼叫端 `cmd_install`(`scripts/lumos:10343` `_states[_h] = _sync_global_hooks(_src_repo, _h)`)都沒有包 try/except——這正是同一函式上方第 11307 行 `~/.codex 是檔案,mkdir 會炸穿整支 install` 這條教訓要避免的那類 bug,但只修了 `~/.codex` 本身這一層,沒有延伸到新增的 `agents` 子目錄。

最小重現(已實際跑過,對 r1-snapshot.patch 版本的程式碼):建一個假 HOME,`~/.codex` 是目錄但 `~/.codex/agents` 是一個**普通檔案**,呼叫 `_sync_global_hooks(repo,'codex')`:
```
Traceback (most recent call last):
  File "scripts/lumos", line 11337, in _sync_global_hooks
    st = _install_codex_agent()
  File "scripts/lumos", line 11359, in _install_codex_agent
    d.mkdir(parents=True, exist_ok=True)
FileExistsError: [Errno 17] File exists: '.../.codex/agents'
```
`returncode=1`,`lumos install` 直接以未捕捉例外中斷,不會走到後面「PATH 檢查」等剩餘步驟,使用者看到的是原始 Python traceback,不是專案一貫的「⚠ 講清楚原因+下一步」風格訊息。

備註(透明揭露,不影響本條判定):目前工作樹(未 commit)已經有一版修法,在 `d.mkdir` 前加了 `if d.exists() and not d.is_dir()` 判斷並回傳新狀態 `skipped-not-dir`,commit 內註解明寫「code-codex-d6 r1 外家 #1」——與本條獨立重現的問題一致,可視為交叉驗證,但**這個修法不在被審的 r1-snapshot.patch 內**,凍結材料本身仍有此洞。

---

### F2
severity: minor
blocking: 否
file: `scripts/test_lumos.py`(r1-snapshot.patch 內 `t_codex_d6_agent_toml` 新增區塊,倒數第 2-3 行)
引句:「os.environ['PATH']='/nonexistent';m._sync_global_hooks(repo,'codex')」

測試最後一段:
```python
home2 = Path(tempfile.mkdtemp(prefix="gctl-d6b-"))
_codex_run(home2, "import os;os.environ['PATH']='/nonexistent';m._sync_global_hooks(repo,'codex')")
check("d6: 無 ~/.codex → 不建 agents", not (home2 / ".codex").exists(), "")
```
把 `PATH` 設成 `/nonexistent` 這行對這個斷言完全不起作用——讀了 `scripts/lumos` 內 `_codex_present` 的實作與其自己的 docstring:「★單一判準=Codex 家目錄(~/.codex 或 $CODEX_HOME)在不在★,不看 PATH」(`scripts/lumos:11282`)。真正讓斷言成立的原因只是 `home2` 這個全新 tempdir 本來就沒有 `.codex` 子目錄,跟 PATH 設成什麼無關——刪掉那行 `os.environ['PATH']=...` 斷言結果完全不變。

這行是從既有測試 `t_codex_sync_global_tristate`(`scripts/test_lumos.py:24893`)原樣複製過來的舊寫法(該處在更早的 commit 就有這個 idiom,docstring 甚至寫「PATH 無 codex → absent」),但既然 `_codex_present` 的判準文件已經明講不看 PATH,新測試沿用這個誤導性設定沒有鑑別力——沒有測到「PATH 找不到 codex」這件事,只是又測了一次「沒有 ~/.codex 目錄」。不影響測試本身的正確性(它仍然合法覆蓋了 `_sync_global_hooks` 的 absent 早退路徑,不建 agents 目錄),純粹是斷言意圖與實際覆蓋不符,容易誤導之後維護者以為程式碼會查 PATH。

---

### F3
severity: minor
blocking: 否
file: `scripts/lumos:11330-11340`(r1-snapshot.patch `_sync_global_hooks` 新增第 4 步的位置)
引句:「if harness == "codex":                 # ④ 自訂審查席 TOML(d6)」

`_sync_global_hooks` 內,①copy hook 檔 ②撤除殘留檔 ③跑合併器 ④(新增)裝 codex agent TOML,四步依序執行;但 ③ 若 `merge-failed`(`r.returncode != 0`)會在到達 ④ 之前就 `return "merge-failed"`(既有邏輯,行 11334-11335),所以 hooks.json 損毀時,**hook `.py` 檔案已經 copy 完成、但 `lumos_reviewer.toml` 不會被寫入**——兩個子狀態不對稱,而且沒有在任何 docstring 或 `_sync_msg` 的 `merge-failed` 分支訊息(`scripts/lumos:11393`)裡提到「連審查席 TOML 也還沒裝」。

具體場景:使用者的 `~/.codex/hooks.json` 因外部原因壞掉 → 跑 `lumos install` → 印出 `merge-failed` 警告(訊息只講「檔已 copy 但…註冊沒更新——修好 JSON 再跑 lumos install --force」)→ 使用者去修 JSON,但如果他誤以為訊息已完整涵蓋所有沒做完的事、遲遲不重跑 `--force`,審查席 TOML 就會一直缺著且沒有任何獨立提示。此路徑可自癒(照訊息指示重跑 `--force` 後,④ 就會補上),不會造成資料損壞,所以只評 minor、不建議擋。

---

## 正面驗證(逐項回答審查鏡頭 1 提出的具體疑問)

- **TOML 語法**:用 `tomllib.loads()` 實際解析 `_CODEX_AGENT_TOML` 完整字串(含 `_CODEX_AGENT_MARK` 開頭註解行、`developer_instructions` 內的反引號、「」全形引號、`|`)——**解析成功**,四個欄位(`name`/`description`/`developer_instructions`/`sandbox_mode`)值正確,`developer_instructions` 長度 238 字元。內容裡沒有出現會提前截斷三引號字串的 `"""` 序列。
- **開頭是註解行是否合法**:TOML 允許任意位置放 `#` 開頭註解,不需要前面接空行——解析結果確認合法,severity: clean。
- **`f.read_text(errors="replace")`**:`_install_codex_agent`/`_remove_codex_agent` 兩處都用 `encoding="utf-8", errors="replace"`,對非 UTF-8 二進位垃圾只會把壞位元組換成替代字元、不會丟例外(不會撞上 `UnicodeDecodeError`);壞內容因為不含 `_CODEX_AGENT_MARK` 會被判成 `skipped-foreign`,不會誤刪誤蓋。severity: clean。
- **teardown 對空的 `agents` 目錄要不要 `rmdir`**:目前不 rmdir。判斷為合理預設——`_remove_codex_agent` 只保證刪自己寫的那個帶標記檔案,不對整個 `agents/` 目錄的所有權作假設(使用者或 codex 本身之後仍可能在該目錄放別的 agent TOML),沒有具體壞場景,不作為 finding。
- **測試永真斷言**:除 F2 指出的 PATH 那一行外,`t_codex_d6_agent_toml` 其餘五個 `check` 都是有鑑別力的(已重跑整支測試驗證,6/6 綠;把 `_install_codex_agent` 的覆寫保護、`_remove_codex_agent` 的標記判斷任一還原都會讓對應斷言翻紅)。

---

## 本案特定鏡頭(審查鏡頭 4)

- **skill 文字宣稱是否與計劃筆記 d6 實作紀錄一致**:對照 `docs/lumos-toolchain-knowledge/Projects/Codex完全支援_計劃.md` 第 166/234/235 行——「0.153.2 實測自訂 agent 選得中(agent_type=lumos_reviewer)」「TOML 的 sandbox_mode 沒擋住寫檔」「0.144.1 全域版忽略此檔(無害)」三項都對得上 skill 三處改動的文字與 code 內 docstring。severity: clean。
- **`_sync_msg` 的 codex `ok` 訊息 wording 改動**(信任綁 hooks.json 命令列、內容變更不用重審)對照計劃筆記第 163 行「信任綁的是設定檔裡那一條命令列…只換 hook 檔內容不用重審」——一致。severity: clean。

---

## 圖譜鏡頭(LUMOS-IMPACT: Lumos/main..HEAD)固定席逐條判

以下 8 個「直接/間接相依」節點皆因 `scripts/lumos`、`scripts/test_lumos.py` 是巨型共用檔(牽連檔列表)而被列入,不代表功能真的重疊——逐一核對其 INVARIANT 描述的機制與本次改動的程式碼路徑後,判定如下:

1. **lumos-cli-lifecycle.md**(re-inject 只覆蓋 sentinel 間 body):不影響。本次改動完全不碰 CLAUDE.md re-inject/sentinel 邏輯,新增函式是 Codex agent TOML 的安裝/移除,跟 sentinel 注入是不同機制。
2. **slim-uninstall-一行卸載.md**(6 條 INVARIANT,四步驟互不阻擋/skill 備份/CLAUDE.md 還原/`.cmd` shim 對稱/manifest 清理):不影響。這些 INVARIANT 描述的是 `cmd_uninstall` 內 bin/skill 目錄/`~/.lumos-slim`/CLAUDE.md sentinel 四步,新增的 `_remove_codex_agent()` 呼叫點在 `_teardown_global_hooks`(`cmd_teardown` 的「①全域 hook 清理」步驟),是完全不同的函式與呼叫路徑;且 `_remove_codex_agent` 內部把 `OSError` 吞掉回傳 `False`,不會拋例外去打斷任何其他步驟。
3. **bound-tests-gate.md**(code-loop check 對綁定測試真跑):不影響。本次沒有動 gate 邏輯本身,只是新增一支被綁定的測試 `t_codex_d6_agent_toml`。
4. **canary-audit.md**(record/second 落盤即讀回):不影響,未觸碰 canary 相關程式碼。
5. **guard-kill.md**(rc 優先序/JSON 純度):不影響,未觸碰 guard kill 程式碼。
6. **slim-get-一行安裝.md**(`.ps1` ASCII/無 BOM、禁用 `$Args`):不影響,未觸碰任何 `.ps1` 檔案。
7. **slim-install-安裝器.md**(7 條,CLAUDE.md 注入原地取代/冪等/備份、manifest 寫入、目標守衛、Windows shim 偵測):不影響,原因同 #1/#2——這些都是 slim 一行安裝(`lumos-slim`)獨立的安裝器邏輯,與本次改動的 `_sync_global_hooks`/`_install_codex_agent` 是不同的程式碼路徑。
8. **測試假綠形態.md**(bug 修復的翻紅釘需要「現場成立」前置斷言):本次新增測試都是新功能覆蓋(非既有 bug 修復回歸測試),但檢查其斷言結構本身具備鑑別力(已用實跑+反向推理確認,見上「正面驗證」段),不構成該 INVARIANT 描述的假綠形態,唯 F2 指出一行斷言前置條件（PATH）沒有鑑別力,已獨立列為 finding。

超出上限只列名的節點(design-loop.md、lumos-cli-read.md 等 12 個)未見與本次改動的程式碼路徑(Codex agent TOML 安裝/移除、hook 同步/拆除四步驟、三份 skill 文字)有任何字面或邏輯交集,不逐條展開。

---

## Pitfalls manifest

0 條——與題面所述一致,未發現需要另外補登的新 pitfall 類別(本次新增的 mkdir 崩潰屬於「本次改動自身的正確性 bug」,已列 F1,不是可泛化的通用 pitfall)。

---

## 總結

max severity: **major**(F1)
blocking 條數: **1**(F1;F2/F3 為 minor 且 blocking: 否)
