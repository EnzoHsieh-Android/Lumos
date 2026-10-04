severity: major

## F1 列舉成員數與 Python 實際不符(Flag 組合值、單底線名稱、_ignore_),靜默給出錯的現值
severity: major
blocking: 是
引句:「成員=本體裡單一名稱的指派、名稱不是底線開頭;值要是常數或 auto(),」
佐證行:實測 Python 3.14 `len(list(E))`;`scripts/lumos` 的 `_count_enum`(patch 內同一段)
1. `class F(Flag): A=1; B=2; C=3; D=4`:Python 的成員是 A、B、D(C=3 是 A|B 的組合別名,不算成員)=3;`_count_enum` 的重複檢查只比常數值有沒有相同,C=3 不重複,算成 4。標籤寫 `=3` 的正確筆記被列成「數量對不上:寫 3、現在是 4」,`drift fix --kind count` 會把對的數字改成錯的。計劃〈S2〉宣稱別名一律判不了,Flag 組合別名卻漏過。
2. `class E(Enum): _priv = 1; X = 2`:Python 有 2 個成員(單底線開頭、非 `_x_` 形的名字是正常成員),工具因為 `tgt.id.startswith("_")` 數成 1。
3. `_ignore_ = ["tmp"]; tmp = 5; Z = 1`:Python 1 個成員(tmp 被忽略),工具數成 2。
最小重現:/tmp/count-r1-work/t1.py,輸出 `F 3 (4, None)`、`E2 2 (1, None)`、`E4 1 (2, None)`。

## F2 drift fix 標籤寫成 `X = 3`、`=03` 時只改句子、標籤不動,寫完才在驗證時擋,留下半改的筆記
severity: major
blocking: 是
引句:「return _COUNT_TAG_RE.sub(lambda t: re.sub(rf"={old}\s*\]$", f"={new}]", t.group(0)), line), None」
佐證行:`scripts/lumos` `_count_parse`(同 patch)接受 `X = 3 ]` 與 `=03`:`num.strip()` 後 `int`
1. 筆記 `有 5 種 [count:src/st.py::KINDS = 5]`,實際 2。`_count_parse` 把 `= 5` 解成 n=5,掃描列成對不上;`drift fix` 的 `_count_rewrite` 句子裡的 5 改成 2,但標籤替換用 `={old}\s*\]$`,`= 5` 中間有空白,比不到,標籤不變。
2. `_drift_fix_write` 已經把半改的內容寫進磁碟(檢查函式是 `lambda _f: True`),隨後 `_drift_fix_verify` 的 handled 看到標籤還是 5 ≠ 2,回「寫入後內容跟預期不同」,rc=2,不自動還原、沒記修復帳。結果:句子寫 2、標籤寫 5,scan 仍然報對不上。
3. `=05`(前導零)同樣:`int("05")=5` 判得出,替換正規式 `=5\]` 比不到 `=05]`。
最小重現:/tmp/count-r1-work/e2e2.py(輸出 `rc 2`、檔案內容 `有 2 種 [...KINDS = 5]`、`no ledger`);前導零見 e2e.py 的 leading zero 案例。
註:預先寫入前沒有模擬 `_count_rewrite` 的結果再解析一次,是這個洞能走到寫檔的原因。

## F3 drift fix 會改到句子裡不相干的數字(F3、r3 這類識別碼),也改行內程式碼裡同一個標籤
severity: minor
blocking: 否
引句:「hits = [m for m in re.finditer(rf"(?<![0-9.]){old}(?![0-9.])", line)」
1. `有三種(見 F3 說明) [count:src/st.py::KINDS=3]`,實際 2。「三」是中文數字不算,但 `F3` 的 3 前面是字母 F、後面是空白,通過 `(?<![0-9.])3(?![0-9.])`,成為唯一命中:改成 `有三種(見 F2 說明) [count:...=2]`,rc=0、記帳。把識別碼改壞,而且訊息說「標籤與句子」已一起改好。
2. `有 5 種 [count:...=5] 範例 \`[count:...=5]\``:行內程式碼裡的範例標籤被 `_COUNT_TAG_RE.sub` 一起改成 =2(`_count_lines` 認為只有 1 個標籤,sub 卻掃整行含行內程式碼)。
最小重現:/tmp/count-r1-work/e2e.py(chinese+F3、inline-code twin 兩案)。

## F4 標籤數字超過 4300 位,scan 整支崩潰
severity: minor
blocking: 否
引句:「return {"path": path, "name": name, "n": None if err else int(num.strip()), "err": err}」
1. 標籤 `[count:src/st.py::KINDS=` 加 5000 個 9:`re.fullmatch("[0-9]+")` 通過,`int()` 在 Python 3.11+ 超過字串轉整數上限丟 ValueError,沒有 try。`lumos drift scan` rc=1 帶 traceback,整個 scan 不給任何結果(其他種類的發現也看不到)。
最小重現:/tmp/count-r1-work/e2e.py 的 digits 案例(scan rc 1;doctor 靠外層容錯仍 rc 0)。

## F5 模組最上層定義之後被原地修改的集合,算出來的是定義當下的數
severity: minor
blocking: 否
引句:「elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == name and st.value:」
1. `X = {'a'}` 後接 `X |= {'b'}`、`X = ['a']` 後 `X.append('b')`、`X=[1,2]` 後 `X += [3]`:`_count_eval` 只看 Assign/AnnAssign/ClassDef,AugAssign 與方法呼叫完全不看,各回 1、1、2,執行期是 2、2、3,數字吻合時不報、不對時還會被 `drift fix` 改成錯的。〈天花板〉1 只講「組出來的集合判不了」,沒涵蓋被後續語句改過的字面值。
最小重現:/tmp/count-r1-work/t1.py,輸出 `"X = {'a'}\nX |= {'b'}" (1, None)`。

## 走過但沒有 finding 的輸入
- 解析:`X=3=4`(名稱成 `X=3`、找不到列問題)、`a.py::Cls::X`(path 成 `a.py::Cls`,不在樹上列問題)、全形冒號與非 ASCII 數字(`[0-9]+` 擋下,列寫錯)。
- 計數:`{1, True}`、`{1, 1.0, 2}`、`{None, None}`、`()`、`set()`(列問題)、`frozenset(set([1,2,2]))`、AnnAssign 都與 Python 一致;`-1` 負數常數被判成非常數、列問題,偏保守。`if` 底下的定義不被看見,與只認最上層一致。
- `text_of`:單參數回該檔、多參數只預讀回 None,`scan` 與 `fix` 的用法各自對;預算用完時 `_read` 回 False,列成「判不了(超過預算)」。
- 新舊互讀:`_DRIFT_KINDS` 多 count,表態檔讀側本來就按種類過濾;`_drift_check_core` 與推送閘不迭代 `_DRIFT_KINDS`,不受影響。
- 測試:`python3.14 scripts/test_lumos.py -k count_tag` 25 項全過;SETS 去重(3 對 2)、Color 的 auto() 與句子兩個舊數字的釘有效。缺口:沒有 Flag 組合別名、標籤含空白或前導零的 fix 測試(F1、F2 都沒被任何測試涵蓋)。`handled` 閉包忽略傳入的重新掃描結果、只檢查標籤數字等於事先算好的現值,不是真重算(F2 靠這個才被攔到)。

## 圖譜固定席判定
- `Systems/存量漂移守衛` 摘要的新 WHY 行:程式行為與它所寫相符,除了「列舉別名判不了」對 Flag 組合值不成立(見 F1);該行的 `[test:t_count_tag_scan]` 沒有 Flag 案例。
- `Systems/lumos-cli-read`(讀指令不寫治理帳):`cmd_drift_scan` 新增的 count 段只讀、不寫帳,`drift fix` 本來就寫修復帳,不影響。
- `Systems/測試假綠形態`(還原翻紅釘要有前置斷言):新測試的翻紅釘有說明,`t_count_tag_fix` ①②先查現場(標籤、帳),不假綠;但 F2 的半改輸入沒被任何測試涵蓋。

總結:最高等級 major
