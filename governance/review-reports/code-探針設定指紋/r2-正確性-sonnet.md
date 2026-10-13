severity: major

## 1. 兩層例外保護與型別測試互相掩護,任一層拿掉測試照綠(假綠)
severity: major
blocking: 是
引句:「            ok = "env_fp" in got」
file: `scripts/test_lumos.py:42291`

1. 壞型別測試只斷言回傳 dict 有 `env_fp` 這個鍵。`env_fp` 是 None(退成取不到)也算過,所以測試分不出修補要的兩種結果:欄位「當空的」(指紋照算)和「整個退成 null」。
2. 單獨拿掉任何一層,測試都不紅,我在 /tmp 複本上各驗了一次:
   - 拿掉 `env_fingerprint` 的 try/except:`python3.14 scripts/test_lumos.py -k probe_env` 回 `22 passed, 0 failed`。原因是五個壞型別輸入全被 `_env_list` 擋掉,沒有任何測試輸入會走到外層保護。
   - 把 `_env_list` 改成 `return v or []`:同樣 `22 passed, 0 failed`。`plugins=5` 在迴圈裡丟 TypeError,被外層吞掉,回 `env_fp: None`,斷言照過。
3. 能真的走到外層保護的輸入,測試裡一個都沒有。例如 `skills=["\ud800"]`(lone surrogate)會在 `.encode("utf-8")` 丟 UnicodeEncodeError。
4. 最小重現(不拿掉修補,只證明保護層沒被測到):
   - `env_fingerprint([json.dumps({"type":"system","subtype":"init","skills":["\ud800"]})])`
   - 回 `{'env_fp': None, 'env_missing': '取指紋失敗:UnicodeEncodeError'}`
   - 這條路徑 0 個測試覆蓋。
5. 「當空的」也沒被斷言。`skills={"a":1}` 的指紋和 `skills=[]` 完全相同(我跑出 True)。清單欄位改成 dict 時,指紋對該欄位變成瞎的,沒有任何測試或 `env_missing` 記錄。
6. 歸因:有證據的修復回歸。修補自帶的新測試就是假綠。查證命令與結果見上。

## 2. 外層保護把一行無關的深層巢狀 JSON 升級成「整場指紋 null」
severity: minor
blocking: 否
引句:「        except ValueError:」
file: `scripts/scenario_probe.py:355`

1. `_env_scan` 只抓 ValueError。`json.loads` 遇到深層巢狀行會丟 RecursionError,不是 ValueError。
2. 修補前:這個例外往外丟,整場被記成儀器例外。這正是修補要避免的後果。
3. 修補後:被外層保護吞掉,但 init 本來是好的也一起丟掉。重現:`env_fingerprint([init_line, '{"a":' + '['*200000 + ']'*200000 + '}'])`,回 `{'env_fp': None, 'env_missing': '取指紋失敗:RecursionError'}`。
4. `run_one` 自己的結果迴圈用 `except Exception`,同一行不會讓判分失敗,只有指紋被拖累。
5. 歸因:有證據的原有漏查。查證命令與結果見上。
6. 機率很低,所以標 minor。把 `except ValueError` 改成 `except Exception` 就能修。

## 3. env_mixed 的語意:單獨一場取不到就算混用 ⚠
severity: minor
blocking: 否
引句:「        if len(summary["env_fps"]) > 1:」
file: `scripts/scenario_probe.py:1223`

1. `env_fp_counts` 把 None 記成 `"null"` 這個鍵,和真指紋同級。
2. 重現:`summarize_results` 輸入 `[{env_fp:a}, {env_fp:None}]`,得 `env_fps={'e94b…':1,'null':1}`,`history_record` 的 `env_mixed` 是 True。
3. 環境其實沒變,只是某一場沒 init(例如被截斷前沒輸出,但沒被判成儀器例外)。`env_mixed` 因此報「環境混用」,語意被稀釋。
4. 這是設計取捨,不是 bug。判不準,標 ⚠,歸因:未判定。

## 4. 同一批內 tools 欄位可能逐題不同,env_mixed 可能每週假報 ⚠
severity: minor
blocking: 否
引句:「        cmd += ["--disallowedTools", "Agent"]」
file: `scripts/scenario_probe.py:1108`

1. `run_one` 對 `allow_agent: true` 的題(例:`governance/scenarios/absence.jsonl:5`)給不同的 `--allowedTools` 與 `--disallowedTools`。
2. 指紋包含 `init.tools`。若 Claude Code 的 init 事件會反映這兩個旗標(我沒有實際呼叫 `claude -p`,無法證實),同一次週抽就會出現兩個指紋,`env_mixed` 每週都是 True,辨識度歸零。
3. 假造的兩份 init(`tools` 差一項)重現出 `env_mixed: True`。這只證明程式邏輯,不證明真實 init 有此行為。
4. 缺證據,severity 降一級。作者應用一份真實輸出確認,或把 `tools` 改成不看被旗標調整的項目。歸因:未判定。

## 5. SessionStart 掛鉤「只算 init 之前」的前提只被假造資料驗證 ⚠
severity: minor
blocking: 否
引句:「        elif ev.get("subtype") == "hook_started" and ev.get("hook_event") == "SessionStart" and init is None:」
file: `scripts/scenario_probe.py:360`

1. 計劃的〈實測〉只寫「另有一筆 SessionStart 的 hook_started」,沒寫它在 init 之前還是之後。
2. 測試 fixture `_probe_init_lines` 把 hook 放在 init 前面,是作者假設的順序,不是實測事實。
3. 若實際順序是 init 先出,`session_start_hooks` 永遠是空陣列。指紋對掛鉤變化完全無感,而且不報錯。
4. 這個風險也符合修前的設計(修前不分前後),所以修補只是把賭注押在未驗證的順序上。
5. 缺證據,不升級。作者要補一份真實 stream-json 開頭的順序證據。歸因:未判定。

## 事件順序與相鄰路徑檢查
1. 事件順序:init 之後的 SessionStart 不計(compact 測試成立)。重複掛鉤用 set 去重,`fp_dup` 測試在拿掉 set 時會翻紅(兩筆同名 hook 排序後不同)。
2. 這兩條測試的殺傷力我確認過邏輯,未做 mutation。
3. 相鄰呼叫者:
   - `summarize_results` 的總結行格式沒變,`governance/autonomous-loop.sh` 不受影響。
   - 我在 repo 內沒找到消融腳本使用 `env_fps`、`env_fp` 的地方。
   - `run_one` 的兩個提早返回與 `run_one_codex` 的 None 結果都帶 `env_fp` 鍵,`env_fp_counts` 用 `.get` 讀,舊結果缺鍵也安全。

## 三問
1. 原問題的修復效果:
   - 型別壞掉、重複掛鉤、init 後掛鉤這三類,實際輸入走過後行為正確。
   - 但外層保護本身沒有測試證據(見 finding 1)。
2. 修補處的相鄰路徑:正常、錯誤、相鄰呼叫路徑都仍成立。
3. 同一案例修前與修後:
   - `skills=["\ud800"]`:修前丟 UnicodeEncodeError、整場記成儀器例外;修後回 `env_fp: None`。
   - 深層巢狀行:同樣修前丟例外,修後 null。
   - `plugins=5`、`skills=True` 這類壞型別:修前可能丟 TypeError 或 AttributeError,修後指紋照算。

總結:最高等級 major
