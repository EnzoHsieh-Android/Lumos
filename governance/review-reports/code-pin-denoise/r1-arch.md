# code-pin-denoise r1 架構對齊審查(arch-sonnet 席)

審查對象:`/tmp/code-pin-denoise-r1.patch`(= `governance/review-reports/code-pin-denoise/r1-snapshot.patch`,668 行、五支檔:`governance/eval/build_goldset.py`、`governance/eval/retrieval_eval.py`、`scripts/hooks/claude/impact-hook.py`、`scripts/lumos`、`scripts/test_lumos.py`;對應提交 `d0456b8`)。本席只判「跟既有做法一不一樣」,不找 bug、不評風格。

對照基準:rescued 桶(knob/排序/meta/輸出)、`_impact_knob` 轉正註解慣例(`LUMOS_IMPACT_BASENAME_MATCH`)、條件頂層鍵慣例(`query_gated`/`stack_questions`)、hook 讀鍵慣例、`must_ratchet` 寫法(`pin_noise_ratchet` 鏡像與否)、測試 fixture 慣例(`_about_impact_fixture` vs `_hardpin_fixture`)。

---

## 三問

### 問一:分層依賴——這份 diff 有沒有跨層直呼?

**沒有,對齊。** 既有分層是:`scripts/lumos` 是唯一真相源;`governance/eval/*.py` 與 `scripts/hooks/claude/impact-hook.py` 一律透過 subprocess 呼叫 `lumos impact --json` 再讀解析後的 dict,不 import `scripts/lumos` 內部函式(test_lumos.py 用 `SourceFileLoader`/`spec_from_file_location` 動態載入是測試層既有的例外,不算違規)。這份 diff 的三處改動都遵守這條邊界:
- `governance/eval/build_goldset.py:157-162`(`edit_pool`)——新增的 `_rk.get("lane", [])` 合併,仍是對 `lum_json(...)`(subprocess 包裝)回傳字典的鍵存取,沒有新增對 `scripts/lumos` 的直接呼叫。
- `governance/eval/retrieval_eval.py:130-140`(`edit_universe`)——同樣是對既有 `subprocess.run([... LUMOS ...])` 結果 `d.get("lane", [])` 的鍵讀取,呼叫路徑未變。
- `scripts/hooks/claude/impact-hook.py:365`(`lane = data.get("lane", [])`)——`data` 是 hook 收到的已解析 JSON,純鍵讀取,未新增對 `scripts/lumos` 的 import 或函式呼叫。

`t_eval_lane_buckets` 對 `bg.lum_json`(`scripts/test_lumos.py:21080`)的 monkeypatch,是測試替身覆寫,套用既有的「覆寫已載入模組屬性」慣例(`m.edit_universe = lambda case: canned`,`scripts/test_lumos.py:21037` 為既有先例),不是生產路徑的跨層呼叫。

### 問二:命名與錯誤處理——`pin_noise_ratchet` 真的是 `must_ratchet` 的鏡像嗎?

**部分對齊,兩處具體落差。** `pin_noise_ratchet`(`governance/eval/retrieval_eval.py:294-311`)自陳是 `must_ratchet`(`governance/eval/retrieval_eval.py:507-540`)的鏡像(方向相反),讀歷史/找基線/回 `(ok, msg)` 的骨架確實一致,但兩處細節沒有真的鏡射:

- 迴圈變數命名:`must_ratchet` 用 `row`(`governance/eval/retrieval_eval.py:524`),`pin_noise_ratchet` 用 `rec`(`governance/eval/retrieval_eval.py:299`),同一個角色(history 裡一筆紀錄)兩個名字。
- 守門條件的註解密度:`must_ratchet` 把「只拿 PASS 輪」與「換尺不比」拆成兩個 `if`、各自帶行內註解(`# ★只拿 PASS 輪當基線★`、`# ★換尺不比★`,`governance/eval/retrieval_eval.py:525-528`);`pin_noise_ratchet` 把同樣兩個條件併成一行 `if`,兩則註解都沒有跟過去(`governance/eval/retrieval_eval.py:299`)。
- 防呆邊界:`pin_noise_ratchet` 多包了 `isinstance(v, dict) and`(`governance/eval/retrieval_eval.py:301`),`must_ratchet` 同一位置(`v.get("must_in_out_count")`,`governance/eval/retrieval_eval.py:530`)沒有這層防呆——鏡像函式的錯誤處理邊界不一致,以後改一邊容易忘記另一邊。

### 問三:第二種做法——有沒有本來有唯一實作、這份 diff 卻另開一條路?

**有,且是本輪最主要的落差。** `split_buckets`(`governance/eval/retrieval_eval.py:162-169`)的 docstring 自己就把「同檔兩種 free 定義=接手的人要猜」點名為這份 diff 要修的架構問題,並自稱「★三桶分流的唯一實作★」。但同一支檔案裡的 `output_top3_must`(`governance/eval/retrieval_eval.py:280-291`)算「前 3 名排除 lane」時,沒有呼叫 `split_buckets` 取 `pins+free`,而是自己重寫一份等價的 `not x.get("lane")` 篩選(`governance/eval/retrieval_eval.py:289`)——目前資料不變式下兩者結果相同,但這正是 `split_buckets` docstring 想避免的「第二個定義」,只是換了個函式重犯。另外兩處也構成「另一種做法」,見下方清單 #7、#8。

---

## 不對齊清單

1. **【minor】meta 字典的條件鍵不對齊 rescued/truncated 慣例。** `meta` 裡 `pinned`/`truncated`/`rescued`/`safety_overflow` 是字面量一次組出、恆常在鍵(`scripts/lumos:14550-14551`),`lane`/`lane_truncated` 卻改成 `if lane_raw:` 才加鍵(`scripts/lumos:14552-14554`),同一個 meta dict 裡並存兩種「有沒有這個鍵」的慣例。
   引句:「meta["lane"] = len(lane_items)」

2. **【minor,⚠ 判準略有推論成分】`lane_truncated` 提示訊息的觸發條件脫離 `truncated` 慣例。** 既有 `meta.get("truncated")` 訊息是掛在桶的 `if` **外面**印(桶砍到空也照樣提示,`scripts/lumos:14575-14576`);新的 `lane_truncated` 訊息卻包在 `if lane_items:`/`if lane:` **裡面**印(`scripts/lumos:14577,14581-14582`;hook 端同款,`scripts/hooks/claude/impact-hook.py:366,370`)。連鎖後果:`LUMOS_IMPACT_LANE_N=0` 時 `meta["lane_truncated"]` 誠實記了被砍的條數,但因為 JSON 頂層 `lane` 鍵本身在 `lane_items` 為空時不會被寫出(`scripts/lumos:14557-14558`),這則訊息永遠印不出來。
   引句:「if meta.get("lane_truncated"):」

3. **【minor】`LUMOS_IMPACT_LANE_N` 轉正理由沒有跟著自己那行走。** `LUMOS_IMPACT_BASENAME_MATCH`(`scripts/lumos:13830`)、`LUMOS_IMPACT_RESCUE_N`(緊鄰 `scripts/lumos:14527` 上方的區塊註解)都是「轉正理由就寫在 knob 自己那一行/正上方」。`LUMOS_IMPACT_LANE_N` 的轉正數字(train 網格、held 噪音變化)卻寫進 `_hard_pin`(另一個 knob)定義前的大註解區塊(`scripts/lumos:14461-14465`),而 `_lane_n = int(_impact_knob("LUMOS_IMPACT_LANE_N", 3))` 自己那行(`scripts/lumos:14544`)完全沒有註解。
   引句:「候選臂 held 噪音 82→39(-52%)、out_top3_must」

4. **【minor】見問二——`pin_noise_ratchet` 迴圈變數命名與 `must_ratchet` 不一致。**
   引句:「if not rec.get("pass") or rec.get("goldset_rev") != rev:」

5. **【minor】見問二——`pin_noise_ratchet` 比 `must_ratchet` 多一層 `isinstance` 防呆,鏡像函式邊界不一致。**
   引句:「isinstance(v, dict) and v.get("pin_noise")」

6. **【major】`output_top3_must` 繞過 `split_buckets`,自己重寫等價的「排除 lane」篩選。** 見問三。`split_buckets`(`governance/eval/retrieval_eval.py:162-169`)明文自稱唯一實作,`output_top3_must`(`governance/eval/retrieval_eval.py:289`)卻另開一條路徑做同一件事。
   引句:「top = [x for x in res if not x.get("lane")][:3]」

7. **【major】測試載入 `build_goldset.py` 沒有沿用同檔已出現兩次的簡式寫法。** `scripts/test_lumos.py` 裡載入 `build_goldset.py`(一支正常 `.py` 檔)的既有寫法是 `importlib.util.spec_from_file_location(name, path)` 兩行帶過,不需要 `SourceFileLoader`(先例:`scripts/test_lumos.py:20793`〔`t_goldset_append`〕、`20872`〔`t_build_goldset_junk_filter`〕;`SourceFileLoader` 在這支檔案裡的既有用途是給沒有 `.py` 副檔名的 `scripts/lumos`/hook 用,見 `scripts/test_lumos.py:297` 的註解)。`t_eval_lane_buckets` 卻改成顯式 `import SourceFileLoader`、路徑字串重複寫兩遍(`scripts/test_lumos.py:21077-21078`)。
   引句:「loader=SourceFileLoader("bg", str(repo / "governance"」

8. **【major,⚠ 判準不確定——這是「同一段邏輯在同一個迴圈裡兩種寫法」而非對照既有 code,是否夠格算「第二種做法」見仁見智】main() 的 per-split 棘輪迴圈裡,決定 gate 名稱是否加 split 後綴的三元運算式,must-see 棘輪先賦值成 `_gname` 再用(`governance/eval/retrieval_eval.py:657-658`),緊接著幾行後的 pin_noise 棘輪同一段邏輯改成直接內聯寫進 dict key、不賦值(`governance/eval/retrieval_eval.py:664`)。同一個函式本體裡,同一件事兩種寫法並存。
   引句:「gates["固定席噪音不回漲(棘輪)" if _rat_split」

---

## 對齊良好、值得記一筆的部分

- `_hardpin_fixture`(`scripts/test_lumos.py:855-871`)與 `_about_impact_fixture`(`scripts/test_lumos.py:666-682`)骨架逐項相同(`g()`/`note()` 兩個內部 helper、`docs/z-knowledge` 目錄佈局、`git add -A && commit` 收尾),連 fixture 內建的本地 subprocess 呼叫 helper都同名 `lum`(`scripts/test_lumos.py:879-882` 對照 `scripts/test_lumos.py:701-704`)——這支新 fixture 是照著既有慣例寫的,不是另開一套。
- `lane_raw.sort(key=lambda r: (-r["score"], r.get("hop", 0), r["node"]))`(`scripts/lumos:14543`)明確標註「同 free/rescued 三鍵慣例」且確實照抄該 tie-break key,排序慣例沒有走樣。
- JSON 頂層條件鍵的加法本身(`if lane_items: out_obj["lane"] = lane_items`,`scripts/lumos:14557-14558`)跟 `query_gated`/`stack_questions` 的「`if X: out_obj["key"] = ...`」慣例同構,且程式碼自己註明了對照對象。

---

**不對齊共 8 條,其中 major 3 條。**
