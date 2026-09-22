severity: major

## F1 guards 有多個值時,擋下訊息會把解析不到的節點也列進歸因,誤導查證方向

severity: major
blocking: yes

`_guard_touches` 改成全看 `guards:` 欄位所有值後,`homes` 這個清單從頭到尾都沒有被「哪些解析成功」過濾過,連同解析失敗(節點不存在)的項目也一起被丟進最後印給人看的訊息裡:

引句:「homes = [str(x).strip() for x in as_list(gn.fields.get(GUARD_MARK_FIELD)) if str(x).strip()]」
引句:「why = f";你這次改到 {'、'.join(hits[:3])}(它掛在 {'、'.join(homes[:2])} 底下)"」

重現(用 /tmp 臨時 vault,唯讀跑 lumos --vault):
1. 建 `Systems/A.md`(type: system, about_code: `scripts/pay.py`)、`Projects/P.md`。
2. `lumos guard plan Systems/A 混合測試2 --plan Projects/P --phase P1 --due <三天前> --why 還沒做 --owner enzo`,得到一篇 `Verification/…` 守衛節點,`guards:` 只有一項 `Systems/A`。
3. 手改那篇守衛節點,把 `guards:` 補成兩項:
   ```
   guards:
     - Systems/A
     - Systems/Gone
   ```
   (`Systems/Gone.md` 不存在,模擬節點被刪除/改名之後 guards 連結沒跟著清)
4. 寫 `touched.txt` 內容為 `scripts/pay.py`(剛好命中 Systems/A 管的檔)。
5. 跑 `lumos doctor --ci --touched-from touched.txt`。

實際輸出(S15 段):
```
⚠ 有 1 條預告的合約已經逾期(不准延期,只能做完或棄置):
    • 混合測試2(負責人 enzo,最遲 2026-09-19);Verification/2026-09-22_混合測試2.md;你這次改到 scripts/pay.py(它掛在 Systems/A、Systems/Gone 底下)
```

`Systems/Gone` 從頭到尾沒被解析成功(`env.find` 在函式裡對它回傳的是 `hn is None`,直接進了 `missing` 清單,沒有進 `files`),但擋下訊息卻寫著「它掛在 Systems/A、Systems/Gone 底下」——把一個查無此節點的名字,講得像它也負責這條合約一樣。這不是風格問題:這一輪 patch 唯一新增的「它掛在哪一篇家節點底下」提示(commit 訊息第 5 點),存在的目的就是讓被擋的人知道去哪篇筆記查;現在這篇筆記根本不存在,照著訊息去查的人會撲空,回頭還得自己去翻 `guards:` 欄位原始碼才知道有一條連結早就斷了。

根因:收集 `missing` 是為了「files 全空」時的錯誤說明(`if not files: if missing: ...`),但 `homes`(顯示用)跟 `files`/`missing`(判定用)是兩份獨立算出來的清單,沒有互相過濾——只要**有任何一個** home 解析成功並貢獻了 hits,所有 home(包含解析失敗的)都會被印進歸因訊息。

## F2 同樣的斷連結,在「沒碰到」的分支會被完全吞掉,使用者連「有連結壞掉」都不知道

severity: minor
blocking: no

跟 F1 同一段程式碼,但走的是「沒 hit」那個分支:

引句:「            return False, f";找不到它守的功能節點 {'、'.join(missing)},算不出有沒有碰到"」

重現:同 F1 步驟 1–3,但第 4 步 `touched.txt` 改成完全不相干的檔(`scripts/unrelated.py`,Systems/A 管的 `scripts/pay.py` 沒被碰到)。實際跑出來:

```
⚠ 另有 1 條逾期的預告合約,但這次改動沒碰到它們(不擋這次推送):
    • 混合測試(負責人 enzo,最遲 2026-09-19);Verification/…
建議: 推送前的閘只擋你這次碰到的,CI 會擋全部;想看全部待完成的:lumos guard required
✓ 這次改動沒碰到任何逾期的預告合約(上面那 1 條還在,只是不擋這次推送)
```

沒有任何字樣提到 `Systems/Gone` 解析不到。因為 `Systems/A` 有 about_code 且貢獻了 `files`,`if not files:` 這個分支根本不會進去,`missing` 清單裡的 `Systems/Gone` 就這樣被丟掉,連「有一條 guards 壞了」這個事實都不會被印出來。

跟 `_guard_touches` 自己的 docstring 對照就看得出落差:

引句:「給了清單卻算不出這條跟哪些檔有關(家節點不見、或家節點沒寫 about_code),本機這一層放行」

這句話講的是「整條合約算不出來就要說清楚為什麼」,但現在是「半條算得出來、半條算不出來」時,算不出來的那半就無聲無息消失了——不擋是對的(方向安全),但沒有任何提示讓人回頭修 `Systems/Gone` 這個死連結,這條合約在本機這一層會一直帶著一個沒人發現的壞連結,直到有一天恰好觸發 F1 的情境才會被人看見(而且看見的是錯的節點名)。

跟 F1 是同一根因(`homes`/`missing` 沒有回填進顯示邏輯),分開列是因為使用者影響面不同:F1 是「擋下時訊息說謊」,F2 是「不擋時問題被吃掉」。

## F3 大小寫不分辨命中時,標出來的「哪一支檔同名」在同一批 touched 裡可能因雜湊亂序而不穩定

severity: minor
blocking: no

引句:「tlower = {x.lower(): x for x in tset}」

`_guard_touched_hits` 用一個 dict comprehension 把正規化過的 `touched` 檔案表按小寫建索引;如果同一次推送裡**兩支真的不同的檔**只差大小寫(大小寫敏感的檔案系統上這兩支檔可以同時存在、同時被改到),`tlower` 的 key 會撞在一起,只留下其中一支,而且留哪一支由 set 的走訪順序決定——Python 字串雜湊預設有隨機種子,同一份輸入、不同行程各跑一次可能選到不一樣的那支。

重現(跑 `_guard_touched_hits(["scripts/PAY.py"], {"scripts/Pay.py", "scripts/pay.py"})`,用不同 `PYTHONHASHSEED` 各跑一次):
```
PYTHONHASHSEED=1 → ['scripts/PAY.py(大小寫不同:scripts/Pay.py)']
PYTHONHASHSEED=2 → ['scripts/PAY.py(大小寫不同:scripts/pay.py)']
```
同一組輸入,seed 換一顆,訊息裡點名的「大小寫不同」對象就換了一支檔。

不影響擋不擋(這條路 `hits` 一定非空,判定結果一致),純粹是訊息裡「跟哪支檔同名」這句話不保證每次都指同一支檔,對「照訊息去對哪支檔」的排查場景會造成困惑。因為只影響訊息文字、不影響安全方向(仍然是擋,符合「寧可多擋」的設計),定 minor。

## 已驗過、沒發現問題的路徑(對照審查鏡頭逐項記錄)

- ① 正規化:`../`(不處理,但只影響字面比對,不影響安全方向)、絕對路徑 `/scripts/pay.py`(不會被砍掉開頭斜線,永遠比不上 git 吐出來的相對路徑;但寫入端 `_about_code_path`(`scripts/lumos:13478`)本來就擋絕對路徑,`grep` 全 vault 也確認現有 about_code 沒有任何一項以 `/` 開頭,實際觸發面極窄,不單獨列 finding)、Windows 反斜線(`_norm_code_path` 正確轉成 `/`)、只有 `.`(正規化後還是 `.`,但 `_about_code_path` 要求 about_code 必須是「這個 repo 裡真的存在的檔案」而非目錄,`.` 通不過 `target.is_file()`,寫入端就擋掉了)、只有 `/`(正規化成空字串,`_guard_touched_hits` 用 `if not f: continue` 跳過,不會誤判)、空字串(同上)、超長路徑(5000 字元,`_norm_code_path` 正常處理不崩潰)。
- ② 資料夾比對:`scripts` vs `scripts_backup/x.py`、`scripts` vs `myscripts/x.py`、`a/b` vs `a/bc.py` 三種都實測 `hits == []`,`x.startswith(f + "/")` 這個寫法本身就正確排除了「前綴字面相符但不是真子目錄」的誤判,沒有找到誤中的路徑。另外 `_about_code_path` 要求 about_code 只能是檔案不能是目錄,所以「家節點寫資料夾」這整條路徑在目前唯一的合法寫入管道(`lumos append`/`lumos new system --code`)下不會被觸發,只有手改節點檔繞過鐵則二時才用得到——不算 bug,列出來是因為跟②的鏡頭有關。
- ③ 忽略大小寫:單一 about_code 對單一 touched 檔案大小寫不同時,正確判定為命中並標記 `only_case`;真正的 bug(多支同名異大小寫檔同時存在時訊息不穩定)見上面 F3。
- ④ guards 全看:字串而非清單(`as_list` 正確包一層,不會逐字元拆開)、清單裡有空字串(被 `if str(x).strip()` 濾掉)、兩個值指到同一篇(重複算兩次但結果一致,無害)、兩篇都沒寫 about_code(進 `nocode` 分支,訊息正確列出兩篇)。「其中一篇不見而另一篇正常」這個組合就是 F1/F2,不是乾淨的。
- ⑤ 收尾訊息:讀 `scripts/lumos:2314-2357` 逐一核對六種組合(只碰到/只沒碰到/只快到期/碰到+沒碰到/碰到+快到期/沒碰到+快到期/三者皆有/三者皆空),新的 `elif not _gover and not _gsoon:` 只在「唯獨 `_gover_other` 非空」時觸發,其餘組合都已有對應的 `warn`/`warn_soft` 涵蓋、不會被新 `elif` 誤蓋掉,也不會出現「剛列完還有逾期又說沒有逾期」的自相矛盾。實測跑過「只有 _gover_other」與「_gover_other + 其他都空」兩種組合,輸出跟預期一致。
- ⑥ pre-push 暫存檔:讀過整支 `scripts/hooks/pre-push`,`_PP_TMP` 在第 99 行建立、`pp_touched_file` 在第 178 行才被呼叫(在 `_PP_TMP` 保證存在之後),`touched.txt` 之後沒有任何步驟用萬用字元掃過 `$_PP_TMP` 整層目錄(`$_sdir="$_PP_TMP/shards"` 是獨立子目錄,`sg-$RANDOM.log` 是不同檔名),不會被別的檢查誤讀或覆寫。`_PP_TMP` 建不出來的情況在第 100–103 行已經先擋下並 `exit 1`,發生在 `pp_touched_file` 被呼叫之前,所以 `pp_touched_file` 裡對 `_PP_TMP` 的防禦檢查永遠不會在「目錄真的建不出來」的情況下被跑到——是保守的死碼,不是漏洞。
