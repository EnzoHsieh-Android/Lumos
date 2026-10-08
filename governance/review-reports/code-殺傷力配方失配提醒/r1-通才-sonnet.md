severity: minor

# 通才-sonnet 第 1 輪:四支條款測試是否真的守住 S1–S7

做法:在 `kcc-r1-work-通才-sonnet/repo`(--shared clone,bd637de7)對 `scripts/lumos` 逐項突變(每次清 `__pycache__`、跑完還原),共約 60 個突變,跑對應測試看會不會翻紅。
突變腳本 `kcc-r1-work-通才-sonnet/mut.py`,輸出 `mut2.out` / `mut3.out`。基準:四支測試在未突變時全綠(21/20/49/17 條)。

結論:大部分條款子句真的守住了(詳見文末「確認守住」)。下面是改壞了測試照綠的 7 處,全是測試缺口(程式現況是對的),沒有 blocker/major。無零斷言、恆真斷言;唯一跑不到的分支是 F7。

## F1 S1「被判重擋下時應不印」用的是對得上的重複,即使把提醒搬到判重前也不會多印
severity: minor
blocking: 否
引句:「②被判重擋下 → 不印提醒(只有擋下那句)", dup.returncode == 2 and "提醒" not in dup.stderr」
佐證行:file: `scripts/lumos:13347-13362`(`_guard_kill_add_locked` 判重迴圈,提醒在其後 `_kill_add_warn(env, rel, recipe)`)
1. 測試的 dup 是拿「恰好一次」的配方(`LIMIT = 5`)再 kill-add 一次。就算提醒被誤放到判重前,這條配方 judge 結果是 ok,本來就不印,斷言恆成立。
2. 突變:在判重擋下的 `print(f"擋下:同一條合約、同檔、同一個舊字串的突變配方已經有了,"` 前插入 `_kill_add_warn(env, rel, recipe)`。跑 `-k t_guard_kill_add_warns_drifted_recipe` → `21 passed, 0 failed`(照綠)。
3. 該子句只有「判重擋下 + 原文失配」的組合才測得到;建議 dup 用 `--old "LIMIT = 42"` 之類的失配配方先寫一次(setup 時 kill-add 一次),再寫第二次,斷言不含「提醒」。

## F2 S5 對照表沒有 CRLF 格,換行正規化(文字模式讀檔)被拿掉測試照綠
severity: minor
blocking: 否
引句:「("非 UTF-8", dict(recipe_file="bad.py"」
佐證行:file: `scripts/lumos:13148`(`_kill_read_text` 的 `open(path, encoding="utf-8")` 註解寫「換行會正規化」);guard kill 對照:`scripts/lumos:13805`(同樣文字模式讀)
1. 計劃 S5 要求判斷函式跟 guard kill「一一對應」,程式特意註明跟 guard kill 同一種讀法(換行正規化)。但 cells 清單沒有任何 CRLF 檔、也沒有 `old` 跨行的格。
2. 突變:`open(path, encoding="utf-8")` → `open(path, encoding="utf-8", newline="")`。跑 `-k t_kill_recipe_check_matches_guard_kill` → `49 passed, 0 failed`。真實後果:CRLF 檔裡跨行的 `old`,guard kill(正規化後)命中 1 次,改壞後的判斷函式會判 hits(誤報)。
3. 建議加一格:`files={"crlf.py": b"LIMIT = 5\r\nX = 1\r\n"}`、`old="LIMIT = 5\nX = 1"`,預期 ok。

## F3 S6 短身分只測前綴、沒測「出現在中間」,前綴比對改成子字串包含測試照綠
severity: minor
blocking: 否
引句:「"對到零條", "0" * 12 if not rid(ra).startswith("0" * 12)」
佐證行:file: `scripts/lumos:13484`(`hit = sorted({i for i in ids if i.startswith(pre)})`)
1. 突變:`i.startswith(pre)` → `pre in i`。跑 `-k t_guard_kill_rm` → `17 passed, 0 failed`。
2. 「對到零條」格用的是全 0/全 1 的字串,而身分是 sha 十六進位,全 0 這種 12 字元幾乎不會出現在任何位置,所以子字串版本一樣回 2。真實後果:給一段落在別條身分中間的 8+ 字元,會移到錯的那條。
3. 建議加一格:取某條身分的 `[2:14]`(不是前綴、但是子字串),斷言 rc 2、筆記不變。

## F4 S6「原子寫入」沒有任何斷言守住,改成直接 write_text 測試照綠
severity: minor
blocking: 否
引句:「("②沒有留下暫存檔", not [x for x in p.parent.iterdir() if "tmp" in x.name]」
佐證行:file: `scripts/lumos:13495`(`atomic_write_verify(path, new_lines, "kill_recipes", _kill_rm_check(...))`)
1. 突變:把 `atomic_write_verify(...)` 換成 `path.write_text("\n".join(new_lines)+"\n", encoding="utf-8")`。跑 `-k t_guard_kill_rm` → `17 passed, 0 failed`。
2. 「沒有留下暫存檔」這條在直接寫入時當然也成立(根本沒建暫存檔),所以它不是原子性的證據。寫後自驗(`_kill_rm_check`)的守護也沒被測:沒有任何格子讓自驗失敗、確認筆記保持原樣。
3. 建議:spy `m.atomic_write_verify` 確認 kill-rm 有走它;或讓 check 回 False 的情境(例如 monkeypatch `_kill_rm_check`)斷言筆記不變、回 2。

## F5 doctor 設定檔讀不了時「記一筆 check-p2(節點空)」沒被測,拿掉測試照綠
severity: minor
blocking: 否
引句:「p2ev = [e for e in evs if e.get("gate") == "check-p2"]」
佐證行:file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md:128`(「這種情況也記一筆 `check-p2`(節點空)」);`scripts/lumos:2936`
1. `--ci` 的事件斷言只在 Mix/BadJ 那組(有配方失配)跑;S4 的「設定檔壞」那兩格只跑 `run(v, "doctor")`,沒帶 `--ci`。
2. 突變:拿掉 `_p2["cfg_err"]` 分支裡的 `gov_events.append({"gate": "check-p2", ...})`。跑 `-k t_doctor_kill_recipe_drift` → `20 passed, 0 failed`。
3. 這是計劃〈實作紀錄〉的行為而非 S3/S4 條文字面,所以只列 minor;建議在 ⑩ 兩格補跑 `--ci` 並斷言有一筆 `nodes == []` 的 check-p2。

## F6 S3 的「合約片段 前 30 字」截斷沒被測(合約文字只有 6 個字)
severity: minor
blocking: 否
引句:「合約片段帶 invariant 前 30 字", "合約片段:上限恆為5" in s」
佐證行:file: `scripts/lumos:13262-13263`(`inv[:30]`)
1. 突變:`inv[:30]` → `inv[:10]`。跑 `-k t_doctor_kill_recipe_drift` → `20 passed, 0 failed`。invariant 是「上限恆為5」共 6 字,截斷長度改多少都不影響斷言;斷言名稱說「前 30 字」但沒有任何輸入長過 30 字。
2. 建議用一條 40 字以上的 invariant,斷言印出的片段剛好是前 30 字、不含第 31 字。

## F7 kill-add 提醒的「判斷自己出錯」兜底分支沒有任何格子走得到
severity: minor
blocking: 否
引句:「cfg_case("⑭平台根找不到"」
佐證行:file: `scripts/lumos:13196-13198`(`_kill_add_warn` 的 `except Exception as ex: msg = f"判斷時出錯(...),沒驗原文"`)
1. 突變:`except Exception as ex:` → `except ZeroDivisionError as ex:`(等於拿掉兜底)。跑 `-k t_guard_kill_add_warns_drifted_recipe` → `21 passed, 0 failed`。⑩–⑭ 的各種設定問題都被 `_kill_cfg_load` 接走,不會進這個 except。
2. 程式註解說「不能比現在退步成崩潰不寫入」是這個分支的存在理由,卻沒有測試守它。建議 monkeypatch `m._kill_recipe_judge` 丟例外,斷言 rc0、寫入、stderr 恰一行含「沒驗原文」。(用 subprocess 版測不到,要在 in-proc 測。)

## 確認守住(突變後測試真的翻紅,供參考)
- S1:hits/undecodable/outside/malformed 各自靜默→紅;次數寫死 0→紅;提醒印 stdout 或印兩行→紅;提醒後不寫入→紅;修法字面拿掉 kill-rm→紅;noplat/cfg 靜默→紅。
- S2:只補 covers 時不換成既有那條→紅(⑧⑨b)。
- S3:verification/superseded/stale 各自被列→紅;各狀態(hits/missing/undecodable/outside/malformed/noplat/整欄解析不了)不列→紅;好壞同篇遇壞即停→紅;check-p2 不記或 hard=True→紅;P2 改 `warn`(硬 issue)→紅(靠硬 issue 數那條;rc 本身因基準 strict 已是 1 所以靠 issue 數才抓到,這個設計是對的)。
- S4:三種字面互換→紅;平台根找不到改逐條列→紅。
- S5:非 UTF-8、多次、0 次、絕對連結、絕對 file、解析到 repo 頂、`..` 夾住、連結迴圈、結尾斜線、平台根基準、不在提交裡/被忽略 的突變全紅。
- S6:最短長度、對到多條不同身分、移掉全部、重複只移一條、標記不拿/一律拿、不印內容/範本/covers、kill-rm 與 kill-add 各自不拿鎖、對到零條回 0 全紅。
- S7:三條字面都由真跑 guard kill 取得,字面變動會紅(未單獨突變 cmd_guard_kill;S7「程式不被碰到」靠 diff 而非測試)。
- 等價突變(不算缺口):子模組 `160000` 改判 file(`vendor/lib.py` 無論如何都是 None→missing)、K14(`keep` 為空時多寫 `[]` 不影響讀回)、kill-rm 筆記不存在回 0(非 S6 條文,但目前也沒測,僅備註)。

最高等級:minor
