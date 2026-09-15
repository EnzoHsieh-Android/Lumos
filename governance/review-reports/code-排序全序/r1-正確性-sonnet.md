severity: major

# 代碼審查:固定席排序改成全序(r1-code.patch)

審查材料:`governance/review-reports/code-排序全序/r1-code.patch`(142 行,scripts/lumos + scripts/test_lumos.py);`r1-snapshot.patch` 只在需要脈絡時翻閱,未逐行核對。

## 發現一:home_on=True 分支的既有優先序沒有被破壞

把末項從「只有家才拿節點名、其餘拿空字串」改成「一律拿節點名」之後,重新推導了一次 tuple 比較:第一項(事故 vs 非事故)、第二項(家 vs 非家)在所有列都不受影響,因為新舊寫法都沒動這兩項;第三項只在「家」列才有意義(`-r["score"]`,非家列固定 0.0),不會影響「家在非家之前」這件事,因為那已經在第二項就分出勝負。跑既有測試 `t_impact_pins_order_incident_home_rest`(事故最前、家在非家之前、家之間同分照篇名)全綠,也用亂數重排輸入跑新測試 `t_impact_pins_order_is_total` 確認打亂後排出來的結果不變。沒有找到反向錯。

引句:「-r["score"] if r.get("home") else 0.0, r["node"]))」

severity: clean
blocking: 否——理由:讀 tuple 比較語意 + 兩支既有/新增測試都綠,且用亂數重排輸入做過變異驗證,沒有證據顯示優先序被破壞。

## 發現二:「單一實作」不成立——`cmd_impact_diff` 還在用另一份手寫排序,兩份公式對同一種候選會排出相反順序

新函式的 docstring 自稱「改這裡就是改所有固定席的呈現順序,不要在別處再寫一份」,新測試也寫「排序有單一來源 _sort_pins(兩處各寫一份=會無聲漂移)」。但 `_sort_pins` 只有一個呼叫者(`cmd_impact`,即 `impact --file`)。`impact --diff` 的實作 `cmd_impact_diff` 裡還有一份完全獨立、手寫的固定席排序,這份 patch 完全沒有碰它:

`scripts/lumos:23629`-`scripts/lumos:23631`
```
pins = sorted([v for v in merged.values() if v["pinned"]],
              key=(lambda v: (v["kind"] != "incident", not v.get("home", False), -v["score"], v["node"]))
              if _home_on else (lambda v: (-v["score"], v["node"])))
```

而這份舊公式不是擺著沒用——`cmd_dispatch_lens`(`scripts/lumos:24607`,也就是推送前派工鏡頭 `lumos dispatch-lens` 背後真正在跑的東西)直接呼叫 `cmd_impact_diff` 拿 `results` 再取 `pinned` 那批,順序完全繼承這份舊公式。而測試 `t_impact_pins_order_incident_home_rest` 自己的說明寫著:「排錯的後果是實在的——派工鏡頭只把前幾篇貼內容,其餘只列名」,可見這條路徑的排序穩不穩定確實有人在乎。

兩份公式看起來像同一件事的兩種寫法,實際上對「固定但不是家」(例如帶合約的 direct/indirect)這批候選,同分斷法不一樣:`_sort_pins`(home_on=True 分支)非家列的第三項固定是 `0.0`,只靠節點名斷開,分數完全不參與;`cmd_impact_diff` 那份非家列的第三項是 `-v["score"]`(無條件),分數優先於節點名。用同一組資料實測兩份公式:

```
候選:A-低分(score=0.31)、Z-高分(score=0.95),都是 pinned=True、home=False、kind=direct
_sort_pins  排出:A-低分, Z-高分   ← 低分排前面,純字母序
cmd_impact_diff 舊公式 排出:Z-高分, A-低分   ← 高分排前面,分數優先
```

同一批邏輯上等價的候選,`impact --file` 跟 `impact --diff`/`dispatch-lens` 給出相反的順序。這不是這份 diff 造成的新 bug(`cmd_impact_diff` 那份公式本身在改動前後都沒變、也沒有原始問題描述的「同鍵完全同分」缺陷),但它證明「單一實作、別處不要再寫」這句話在合併後的程式碼裡是假的——未來只改 `_sort_pins` 的人會以為兩條路徑都跟著變,實際上 `--diff`/派工鏡頭那條完全不會動,這正是本次 bug 想根除的「無聲漂移」風險,只是換了個位置繼續存在。

引句:「★改這裡就是改所有固定席的呈現順序★,不要在別處再寫一份。」

severity: major
blocking: 否——理由:`cmd_impact_diff` 既有公式本身已經無條件帶節點名兜底,不會重現原始問題描述的「同鍵、順序看運氣」症狀,所以推這份 diff 不會讓現狀變差;但它讓「排序抽成單一實作」這個賣點不成立,且 `--file` 與 `--diff` 對同批候選給出不同順序,建議另開一輪把 `cmd_impact_diff` 也改成呼叫 `_sort_pins`(統一公式前得先跟人確認要用哪一版當基準)。

## 發現三:home_on=False 分支(旋鈕關掉、舊制)的修復完全沒有測試守著

`_sort_pins` 的 else 分支(`home_on=False`)也從「不帶節點名」改成「帶節點名」,理論上補的是同一種不穩定問題,但新測試 `t_impact_pins_order_is_total` 裡自己造的 `_order` 輔助函式把 `home_on` 寫死成 `True`:

引句:「return [r["node"] for r in m._sort_pins(list(rows), True)]」

實測:把 else 分支改回舊寫法(拿掉 `r["node"]`),`scripts/test_lumos.py -k impact_pins_order`、`-k impact_home_knob`、`-k about_stamp` 全部照樣綠燈(見下方變異測試表第 2 列)。這條分支只在 `LUMOS_IMPACT_HOME=0`(明確標注是回滾/離線對照用)時才會走到,不是預設路徑,但既然這份 diff 順手把它也改了,就該有一條測試守住,否則以後有人在這條分支動手腳不會被抓到。

severity: minor
blocking: 否——理由:這條分支不是預設路徑(旋鈕預設開),且改動方向本身沒有引入錯誤(從常數斷法換成節點名斷法只會讓它更穩定),只是缺測試覆蓋,不影響這份 diff 現在能不能推。

## 發現四:非家候選的同鍵斷法從「跟著上游(不保證,但至少嘗試按分數/深度)」變成「純字母序,分數完全不參與」

舊註解對「其餘」（固定但不是家的候選,例如帶合約的 direct/indirect)的承諾是「保持三軸原序」——引句:「固定席內 stable sort:事故永遠最前(std-r1 s1f10),其次家(旋鈕關掉時是 about 命中者),其餘保持三軸原序;」。修法拿掉了這句話背後的假設,把這批候選的第三項統一填成常數 `0.0`,實質效果是:這批候選現在完全不看分數,只看節點名字母序(見發現二裡 A-低分/Z-高分 的實測)。

這不算重新引入原始 bug(現在至少是「確定的」字母序,不是「看運氣」),而且原本的「三軸原序」承諾本身在合入這批候選之前就已經不可靠(根因分析自己也承認上游順序不穩),所以稱不上是這份 diff 造成的退步。但這是一個沒有被寫進 commit message、沒有測試斷言、也沒有在 docstring 交代的行為選擇:「固定但不是家」這批候選以後排序跟它們的相關分數（`score`)完全無關。如果之後有人依賴這批候選「大致照分數排」的直覺去讀 `impact --file` 的輸出,會被字母序誤導。

severity: minor
blocking: 否——理由:比起修復前的「順序不確定」是淨改善,不是新 bug;只是這個行為選擇沒有被記錄或測試,建議在 `_sort_pins` docstring 或計劃筆記補一句「非家候選同分只看篇名、不看分數」,並考慮日後是否要讓非家候選也照分數排序後再用節點名斷同分。

## 變異測試

清 `__pycache__`、複製 `scripts/lumos`+`scripts/test_lumos.py` 到 `/tmp/r1-review/` 改,repo 內檔案全程未動。

| 植入什麼 | 跑哪支 | 輸出是什麼 |
|---|---|---|
| home_on=True 分支末項改回舊寫法 `-r["score"] if r.get("home") else 0, r["node"] if r.get("home") else ""` | `python3 test_lumos.py -k t_impact_pins_order`(於 `/tmp/r1-review`) | `t_impact_pins_order_is_total` 翻紅:「★餵順序不同的同一批固定席,排出來要一樣★ 原序排出:['Systems/P00.md','Systems/P01.md','Systems/P02.md'] 打亂後排出:['Systems/P05.md','Systems/P06.md','Systems/P04.md']」;8 passed, 1 failed |
| 只還原 home_on=False 分支,拿掉 `r["node"]`(True 分支維持修好後的樣子) | `python3 test_lumos.py -k impact_pins_order` / `-k impact_home_knob` / `-k about_stamp`(於 `/tmp/r1-review`) | 全部通過,無翻紅——證實這條分支的修復目前沒有測試在守 |
| (非破壞性,不算變異)用同一組候選分別餵 `_sort_pins` 與手動重建的 `cmd_impact_diff` 排序公式 | 直接呼叫兩份實作比對輸出 | 兩者順序相反:`_sort_pins` 給 `A-低分, Z-高分`;`cmd_impact_diff` 公式給 `Z-高分, A-低分` |

修復後(未變異)的原版程式碼,`python3 scripts/test_lumos.py -k t_impact_pins_order` 於 repo 內跑出 9 passed, 0 failed。

## 未獨立驗證的宣稱

作者宣稱「同分那 7 筆修好後三次跑出相同順序」與「整條補標流程連跑三次完全一致」在邏輯上是這次改動(把末項換成無條件節點名、構成真全序)的必然推論——只要輸入資料本身(kind/home/score/node)不變,全序排序的結果不可能因輸入的排列不同而不同,這點已經用亂數重排輸入的方式做過等價驗證。「未標數因此從 240 變 242」是評測語料/裁定結果的數字,屬於 `r1-snapshot.patch` 裡的題庫與人工裁定,沒有重跑完整評測驗證(且題目要求不要寫進 `governance/eval/retrieval-eval-history.jsonl`,重跑一次完整 goldset 評測的成本與這份審查的範圍不成比例),沒有找到理由懷疑它,但也沒有独立覆核。

## 總結

全篇最高等級是「重大」,共 1 條;其餘 3 條中 1 條「乾淨」(排除疑慮)、2 條「輕微」;阻塞條數為 0 條——沒有一條需要擋下這次推送,但發現二點出的「單一實作」宣稱與實情不符,建議另開一輪處理 `cmd_impact_diff` 那份沒被統一的排序公式。
