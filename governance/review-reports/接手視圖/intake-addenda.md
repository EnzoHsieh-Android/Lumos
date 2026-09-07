# intake 補遺 — 接手視圖(不進帳;各輪 intake 記帳後凍結,事後的補述放這裡)

> 為什麼有這份:2026-09-07 我在記帳之後回頭改了 r1 / r2 的 intake(補折法、補憑證),處置閘的「留痕」關當場 FAIL——intake 的 sha256 進了帳,事後改=帳面對不上。所以 r1 / r2 intake 還原成記帳當下的原文,後來的補述全搬到這裡。

## r1 補遺(原 intake 記帳後追加的內容)
- **#4、#5 從 accepted 改折**:記帳後問閘 FAIL——code 迴圈內席位標 major 的一律折、不得附理由放行(Enzo 2026-08-25 裁)。
  - #4 折法:加 `_HANDOFF_TICK_RE`——筆記慣例把路徑包在反引號裡,反引號內不限字元;前綴表與 lens 正則有漂移守衛測試;fixture 加 `scripts/資料 處理.py`(空白+中文,未追蹤)。殘餘:裸寫的非 ASCII 路徑仍漏,寫進計劃天花板。
  - #5 折法(第一版):不搬 hook(範圍刀),折成 `t_handoff_hook_import_is_pure`(乾淨 tmp 當 cwd/HOME 匯入一次,不得印字、不得留檔)。後續 r2–r4 三次加固見各輪。
- 帳:r1 `CANARY-43b1f043`(accepted 4,5 那版,留在帳上不撤)。「合併後再補記」的念頭被 hook 推來的 [[Issues/canary-record未落盤事件]] 打掉:延後記帳=可能永遠沒記;記完 tail 讀回核對。
- #4/#5 折入後 `t_handoff_view` 47 條全綠;翻紅釘第三輪(拆反引號抽取→2 條紅;hook 頂層塞 print→純淨測試紅、且 handoff 的 JSON 輸出被污染)。

## r2 補遺
- 帳:r2 `CANARY-4052ffa7`(severity major、findings 1、folded 5)。r2 報告沒有「引句:」行(驗收輪格式我沒要求),quote-check 回「抽不到引句」——驗不了不等於通過;r3 起派工詞明寫每條要附引句。

## r3 補遺
- 帳:r3 `CANARY-b731b08d`(記時忘了帶 `--intake`,r3-intake 沒進帳、所以能改;內容當時已完整)。

## r4 補遺
- 折入後:`t_handoff_view` + `t_handoff_hook_import_is_pure` 共 48 條全綠;翻紅釘第六輪七種全紅(stat / path.exists / pathlib stat / access / subprocess / O_WRONLY 開自己 / 讀 sys.executable)。
- 實作時踩到兩層遞迴:政策檢查裡的 realpath 自己呼叫 lstat(已包)→無限遞迴;稽核鉤子檢查 open 事件時也呼叫 realpath→hook 祖先目錄的 lstat 全被記成違規。用「檢查深度」計數器放行檢查中的呼叫。
- 帳:r4 `CANARY-f3290a3e`(blocker、findings 1、folded 8)。處置閘:處置集合 ✓,留痕 ✗(就是上面 r1/r2 intake 事後被改那件),還原後重問。
