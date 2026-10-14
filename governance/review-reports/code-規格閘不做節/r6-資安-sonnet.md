severity: major

## Finding 1:改計劃檔名就能洗掉 major(ratchet 逃逸)

severity: major
blocking: 是 — 輕量審抓到 major 是要逼計劃改走完整設計審,改個檔名就讓它失效,高風險計劃不經完整設計審就能推上去。
引句:「帳上這個編號任何一筆抓到 major 以上的審查(caught/none),看的被略過那幾行跟現在一樣,就照擋」
- 根因:`_nogo_major_carried` 和 `_nogo_light_window` 都用 `_loop_id_for_plan(prel)`(檔名去掉 `_計劃`)當帳的鍵,所以舊檔名底下的 major 不會跟著計劃走。
- 攻擊步驟(編排者只用正常指令,沒手改帳):
  1. 計劃「甲」有不做清單,略過了「退款」。記一筆 `--severity major` 的輕量審,綁定好快照。推送前回 rc1,訊息含 ratchet。
  2. `git mv 甲_計劃.md 丙_計劃.md` 後提交,重跑 `lumos spec-gate Projects/丙_計劃`。不做清單的內容一字不改,被略過的那幾行跟 major 看的完全相同。
  3. 對 `--loop 丙` 記一筆 clean 的輕量審,綁定新快照、換一席通才。
- 實驗輸出(用 `test_lumos` 的 `_sg_push_setup`、`_ngl_review`、`_ngl_push` 組成,實驗腳本已刪):
  ```
  0 major: 1   Projects/甲_計劃.md:...帳上有一筆輕量審抓到 major(通才-sonnet...),它看的被略過那幾行就是現在這幾行(ratchet)...
  1 renamed no review: 1   Projects/丙_計劃.md:...帳上沒有這個編號的輕量審
  2 renamed + clean review: 0   [spec-gate 推送前] ✓ 丙_計劃:留痕裡的 1 支測試全綠(t_flip)
  ```
- 缺口:被略過那幾行的雜湊相同,舊 major 卻完全不被看見,等於把「換審查席直到審出 clean」的路打開。複製成新檔名也一樣。
- 修法方向:major 的比對改成「帳上任何編號、看的被略過那幾行跟現在相同」,或讓帳記計劃的內容身分。
- 佐證:``file: `scripts/lumos:9258` ``(`_nogo_major_carried`)、``file: `scripts/lumos:9245` ``(`_nogo_light_window`)、``file: `scripts/lumos:12777` ``(`_loop_id_for_plan`)。

## Finding 2:行內反引號與落單反引號讓危險詞整行不被看門掃到

severity: major
blocking: 是 — 危險詞放進反引號,門就判風險低,整個輕量審也不會被要求,高風險計劃可以不經任何設計審就推。這個盲點是舊有的,這輪沒補;但題目點名要查「行內反引號」,而且落單反引號比文件寫的「行內程式碼範例」寬得多。
引句:「vis = _strip_inline_markup(ln)[0]」
- 根因:`_door_keyword_hits` 掃的是剝掉行內標記後的文字。成對反引號裡的字看不見,落單反引號之後的整段也看不見(`_inline_hidden` 把未閉合反引號之後全部當作不可見)。
- 攻擊步驟:計劃有四行合格的已排除理由,正文寫下面幾種行,呼叫 `_door_judge`。
  ```
  plain          「實作 stripe 扣款」          -> high, 關鍵字「stripe」(金流)
  inline         「實作 `stripe 扣款` 串接」    -> low,  signals []
  lone_backtick  「` 實作 stripe 扣款」        -> low,  signals []
  lone_mid       「我們要 ` 然後 stripe 扣款」  -> low,  signals []
  ```
  只要在每一行危險描述前加一個 `` ` ``,就判風險低。
- 對不做清單的影響:不做清單裡的危險詞用同樣方式藏起來,就不進 `nogo_skipped`,連輕量審都不要求。
- 對照:HTML 註解、表格、標題、程式碼圍欄(含沒關的)裡的危險詞都有被抓到,都判 high。這幾處沒問題。
- 修法方向:關鍵字掃描改看原行(危險詞不論有沒有在反引號裡都算),或至少落單反引號不要吞掉後面的字。
- 佐證:``file: `scripts/lumos:8038` ``(`_door_keyword_hits` 內的 `_strip_inline_markup`)、``file: `scripts/lumos:375` ``(`_strip_inline_markup`)。

## Finding 3:改一個標點就讓 major 脫鉤

severity: minor
blocking: 否 — 這是設計刻意留的「照意見改了那幾行」出口,但沒驗改動有沒有回應 major 的意見,所以只算降級。
引句:「被略過的那幾行真的改了才重新來過。回說明或 None。」
- 攻擊步驟:major 審出來後,把 `- 不做退款` 改成 `- 不做退款。`,提交,重跑規格閘,再記一筆 clean 的輕量審。
- 實驗輸出:
  ```
  0: 1 True               (major 時擋下,訊息含 ratchet)
  1 cosmetic edit + fresh clean review: 0   ✓ 甲_計劃:留痕裡的 1 支測試全綠(t_flip)
  ```
- 行雜湊只去掉空白、不去標點,所以一個句號就讓指紋變掉,major 不再成立。威脅模型裡編排者本來就能自己記 clean 審,所以這點更多是天花板,不是新洞。
- 佐證:``file: `scripts/lumos:9263` ``(`_nogo_major_carried` 內的 `cur` 比對)。

## 沒打穿的項目

- 偽造 `nogo_rows_sha`、手改留痕或快照:要手改帳,屬已承認的天花板,沒另外追。
- 重跑規格閘洗 major:讀程式碼後,major 是看全帳而不是看窗口,規格閘留痕之後的重跑洗不掉(`t_prepush_nogo_light_major_survives_regate` 也釘著)。
- 其他 `GIT_*` 環境變數與 git 設定繞過入口清理:只讀了程式碼,沒做實驗。入口 `main()` 清了 replace、grafts、`GIT_DIFF_OPTS`、`GIT_EXTERNAL_DIFF`,`git diff --name-only` 沒用到索引,我沒找到走得通的其他變數。
- 連到的節點正文:已開 Issue 承認,沒重複報。

實驗暫存已刪:`T` 目錄下的 `ngr1`、`ngc1` 與各自的 `-snaps`,以及我的實驗資料夾。`gctl-run-*` 底下的 `ngr1` 時間是 03:3x,不是我建的,沒動。

最高等級 major,blocking 2 條。
