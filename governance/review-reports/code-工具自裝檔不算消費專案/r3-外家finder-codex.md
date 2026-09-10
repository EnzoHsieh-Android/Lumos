severity: major

完整讀完兩份 diff、前兩輪報告及 manifest；目前程式的 blob 與快照一致。以下重現採純函式或記憶體 I/O 打樁，未寫入檔案、未執行原測試套件。

### F19 零條豁免會把尚未修復的 major 問題當成 clean 放行
severity: major
blocking: 是 — 報告拒收守衛失效，未修問題可被計成零條
引句:「_vis_lv = re.sub(r"(?i)\b(?:clean|minor|major|blocker)\b\s*[:：]?\s*0(?![\d.])", "", _strip_inline_markup(ln)[0])」
file: `scripts/lumos:5232` 零值判斷只排除後接數字或小數點
file: `scripts/lumos:5832` canary record 使用此檢查決定是否拒收

1. `總結:最高 severity major 0/1 條已修復,blocking 共 1 條` 會被剝掉 `major 0`，雖然它表示一條問題尚未修復。
2. 實測 `report-normalize` 回 rc0、宣告只讀到 clean、reported 為 0；新增測試僅驗整數 0、1、10，沒有咬住這個邊界。
3. 最小重現如下，預期應拒收；目前最後一行翻紅。

```python
import runpy
m = runpy.run_path("scripts/lumos")
text = "severity: clean\n總結:最高 severity major 0/1 條已修復,blocking 共 1 條\n"
assert m["_report_normalize_issues"](text), "錯誤放行；reported=0"
```

### F20 純量轉清單會改壞既有含雙引號的連結
severity: major
blocking: 是 — 加入新項時會破壞原有圖譜連結
引句:「fm.insert(line_idx + 1, f"  - {fmt_list_item(sval)}")」
file: `scripts/lumos:10672` 原有值經過再次引號編碼
file: `scripts/lumos:10967` 寫後自驗只確認新增項存在

1. `related: '[[Systems/API "v2"]]'` 加入另一個連結時，原項被加入反斜線，而 `parse_frontmatter` 不會將它解碼回原值。
2. 實測原 target 可以解析到筆記，轉換後解析結果為 None，但新增項的寫後自驗仍通過。
3. 最小重現如下，預期原 target 不變；目前最後一行翻紅。

```python
import runpy
m = runpy.run_path("scripts/lumos")
old = '[[Systems/API "v2"]]'
fm = m["edit_fm_append"](
    ["related: '" + old + "'"], "related", "[[Systems/New]]")
value = m["parse_frontmatter"](fm)[0]["related"][0]
assert m["link_target"](value) == m["link_target"](old), repr(value)
```

### F21 F13 的單連結豁免仍會放行巢狀行內清單
severity: major
blocking: 是 — 應拒絕的行內清單仍會被寫成單一壞項
引句:「if (sval.startswith(("[", "{")) and not sval.startswith("[[")) or sval.count("[[") > 1:」
file: `scripts/lumos:10654` 只確認開頭是兩個左括號，沒有確認整個值是單一 wikilink

1. 合法 YAML 行內清單 `related: [[Systems/A], Systems/B]` 開頭為 `[[` 且只出現一次，因此被誤認為單一連結。
2. 實測 append 將整串寫成一個清單項，解析器也不報 lint；F13 要求的拒寫並未完整修到。
3. 最小重現如下，預期 ValueError；目前走到 AssertionError。

```python
import runpy
m = runpy.run_path("scripts/lumos")
try:
    m["edit_fm_append"](
        ["related: [[Systems/A], Systems/B]"],
        "related", "[[Systems/C]]")
except ValueError:
    pass
else:
    raise AssertionError("行內清單被當成單一連結放行")
```

### F22 符號連結路徑加入後仍不能用原寫法移除
severity: minor
blocking: 否 — 影響 about_code 的移除操作
引句:「target = (root / v).resolve()」
file: `scripts/lumos:10916` append 會將符號連結轉成實體路徑
file: `scripts/lumos:10995` remove 僅做字面正規化

1. repo 內有 `alias.py → src/a.py` 時，append `alias.py` 會存成 `src/a.py`，隨後 remove `alias.py` 回 rc2。
2. 已以真實符號連結驗證解析結果，再以記憶體筆記呼叫 remove 重現拒絕；F17 的「同一寫法可加可刪」仍不成立。

### F23 移除正規化路徑時會留下等價重複項
severity: minor
blocking: 否 — 回報移除成功後仍殘留同一支檔的標記
引句:「value = next((x for x in as_list(parse_frontmatter(lines[1:e])[0].get(key))」
file: `scripts/lumos:10996` 只挑第一個等價項，再交給字面比對刪除

1. about_code 依序含 `src/../src/a.ts`、`src/a.ts` 時，remove `src/a.ts` 只會移除第一筆。
2. 記憶體執行原始 `cmd_remove` 實得 rc0，寫回內容仍含 `src/a.ts`；正規化只用於選項，沒有用於刪除全部等價項及寫後驗證。

### F24 清單漂移測試會在合法消費專案製造假紅
severity: minor
blocking: 否 — 消費端自測失敗，但不直接改變產品執行結果
引句:「repo = Path(GRAPHCTL).resolve().parent.parent」
file: `scripts/test_lumos.py:9463` 安裝後此處取得的是消費專案根目錄

1. 消費專案在 `scripts/hooks/my_own.py` 放置自己的受版控程式後，這支測試會將它判成工具清單「少登記」。
2. 記憶體打樁及獨立席核對 runner 均得到 `3 passed, 1 failed`、零 skip、rc1；重現入口為 `python3 scripts/test_lumos.py -k vendored_file_list_matches_what_install_ships`。
3. 這重現了 `Issues/vendored測試套件在消費端假紅` 已記錄的事故類型：把來源 repo 專用驗證帶到消費端執行。

## 前兩輪修法驗收

F1:修到 — 精確檔名排除，專案自己的 hook／template 程式仍會命中。  
F2:修到 — lint 對齊與未對齊兩條路均先排除工具檔。  
F3:修到 — 刪除行傳入排除旗標，已驗證觸發正例及排除反例。  
F4:修到 — set 不再接受 about_code，無法壓扁既有清單。  
F5:修到 — 絕對路徑、越界、不存在及目錄均被拒絕。  
F6:修出新洞 — 入口已統一，但純量轉清單會破壞既有含雙引號連結，見 F20。  
F7:修到 — 舊 set 覆寫支線撤除，普通含冒號空白的值走清單格式化。  
F8:修到 — 事故筆記明寫只做排序、不建立波及連結。  
F9:修到 — 安裝及移除均共用目錄常數。  
F10:修到 — set 專用 helper 撤除，路徑檢查收在 append。  
F11:修到 — 相對目錄移至每層計算，未再逐檔重算。  
F12:修到 — 判別鍵存在時恢復掃描，工具鏈本體正例通過。  
F13:沒修到 — 巢狀行內清單仍能冒充單一連結，見 F21。  
F14:修到 — 純量及清單重複加入均不寫檔，訊息改為已存在。  
F15:修到 — 本機大小寫不敏感磁碟上，錯誤大小寫被拒絕並指出真實名稱。  
F16:修到 — 既有含 ../ 的路徑與正規路徑可去重且不寫檔。  
F17:沒修到 — 普通 ../ 已修，符號連結原寫法及等價重複項仍出錯，見 F22、F23。  
F18:修到 — 授權檔頭測試改用安裝端的目錄常數。

風險掃描清單：誤報 — `scripts/lumos:17660` 的 `open(...)` 位於 docstring，是事故說明文字，沒有開啟檔案 handle。

總結:最高 severity major,blocking 共 3 條