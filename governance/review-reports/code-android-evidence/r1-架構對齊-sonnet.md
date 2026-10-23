severity: minor

審查範圍:`r1-snapshot.patch` 裡的 `scripts/lumos`、`scripts/test_lumos.py`、兩支新 skill 檔與兩處指令表。圖譜筆記只掃過一眼,沒逐條對。

## 1 在函式內重複 `import re`
severity: minor
blocking: 否
引句:「    import re
    if not isinstance(t, dict):」

`_macrobench_threshold_item_err` 在函式內 `import re`。`scripts/lumos:59` 已經在模組層 `import re`,檔案裡其他函式也直接用 `re`,例如 `scripts/lumos:13977`。同一檔的鄰居 `_macrobench_config`(`scripts/lumos:39378`)只在函式內 import 檔案裡沒有的 `json`。這個 import 多餘,但不影響結構。

## 2 `_mb_thr_root` 的 docstring 與回傳值不符
severity: minor
blocking: 否
引句:「暫存專案:一份結果檔 + 門檻檔,沒有基準檔。回 (root, 跑 --json 的結果 dict, 文字輸出)。」

docstring 寫回傳三個值,實際回 `root, r, d, _mb_run(root)` 四個值。測試裡也有人用 `_` 吃掉不要的欄位。鄰居 `_mb_run` 的 docstring 與回傳是對得上的,所以這點算不一致。

## 3 skill 隨附 `rerun.sh` 範本與 Python 內嵌腳本
severity: minor
blocking: 否
引句:「收據目錄裡放這支,原樣照抄、不用改。跑前把 `$SKILL_ROOT/references/perfetto/bin` 放進 PATH」

⚠ 專案裡沒有既有做法可對照。`skills/` 底下所有檔案都是 `.md`,`find skills -type f ! -name '*.md'` 沒有結果,其他 skill 也沒有可執行腳本。這次的處理是把腳本寫成 `reference.md` 裡的文字範本,由 agent 抄進消費專案的收據目錄,所以 skill 本身仍只有 `.md`,結構上沒有第二種做法。這份腳本大約 40 行,內嵌 `python3 -` heredoc,是專案原本沒有的產物形態,但它屬於消費專案的輸出,不是 skill 的程式。我不硬判,建議編排者確認這算不算新慣例。

## 三問

**1. 分層與依賴方向:對齊。**
- 新碼放在 `scripts/lumos` 的 macrobench 區塊,緊接 `_macrobench_print_diff` 之後,命名都是 `_macrobench_*`。
- 呼叫鏈是 `_macrobench_mode` 呼叫 `_macrobench_thresholds`,再呼叫 `_macrobench_check_thresholds`,最後呼叫 `_macrobench_print_thresholds`。這跟既有的 `_macrobench_config`、`_macrobench_compare`、`_macrobench_print` 是同一個分工:讀設定、判斷、印出。
- 驗證用的 `_secev_num` 是同檔既有函式(`scripts/lumos:8554`),`_macrobench_config_fields` 在 `scripts/lumos:39363` 也同樣用它,沒有跨層直呼。
- `source` 欄在 `_macrobench_collect` 裡寫入。比對函式不讀這個欄位,舊基準沒有它也能比,沒有改動依賴方向。
- 兩支新 skill 檔只借用現有的 `lumos macrobench` 指令。

**2. 命名與錯誤處理:對齊。**
- 錯誤處理:壞的設定檔回 rc 2,並用 `print(f"擋下:...", file=sys.stderr)` 輸出,跟 `_macrobench_mode` 原本處理設定檔錯誤的寫法一樣。
- 這次門檻檔錯誤與設定檔錯誤共用同一行 `擋下:{err or terr}`,輸出格式不變。
- 回傳形式:`(結果, None)` 或 `(None, 錯誤訊息)`,跟 `_macrobench_config` 相同。
- 輸出:「只提醒,不擋推送」的語氣、方括號標籤 `[沒達驗收門檻]`、`[沒判]` 跟既有的 `[變慢]`、`[換了裝置,沒比]` 同款。
- 常數用 `MACROBENCH_` 前綴,與 `MACROBENCH_PERCENTILES` 相同。
- 測試用 `t_macrobench_*`、`check(...)`、`gctl-` 開頭的暫存目錄前綴和 `_mb_run` helper,跟 `scripts/test_lumos.py:17732` 一帶一致。
- 不一致只有上面第 1、2 條。

**3. 第二種做法:大致沒有,一處 ⚠。**
- 讀門檻檔的方式(`.lumos/*.json`、`json.loads`、型別驗證)與 `_macrobench_config` 同一種做法,沒有另一種設定檔讀法。
- 門檻是結構化 JSON 加 `max`/`min`。`_secev_k6_thresholds`(`scripts/lumos:9242`)是用正規式解析字串,屬於資安證據閘,不同領域。macrobench 原本沒有絕對門檻的判定,所以這不算第二種做法。
- `_compose_metrics_mode` 沒有門檻概念,沒有可對照的既有函式被重做。新的絕對門檻判定沒有借用 `_macrobench_worse` 的相對容差,但語意不同,我認為合理。
- skill 結構:`SKILL.md` 加 `reference.md` 的組合跟 `lumos-code-loop` 一樣。YAML 的 description 沒加引號,這點與 `lumos-pitfalls-gapfill` 相同,且其中只有全形冒號,沒有問題。
- 唯一的 ⚠ 是上面第 3 條的 `rerun.sh` 範本。

不對齊共 3 條,其中 major 0 條
