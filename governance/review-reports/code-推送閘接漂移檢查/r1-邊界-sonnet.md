severity: clean

## 極端輸入實測(全部在 git clone --shared 的臨時目錄,直譯器 3.14)

沒有 finding。逐項跑過、都沒破:

1. 沒有圖譜資料夾的消費專案:drift check --diff 舊..新,回 0,印「這個專案沒有圖譜,跳過」。
2. 沒有 .lumos/config.json:走預設 warn。
3. config 壞掉:壞 JSON、非 UTF-8、BOM 開頭、config 是 list、drift_check.gate 是 list、gate 寫 BLOCK 大寫。全部回 0,都退回預設 warn。其中 JSON 壞掉、BOM、gate 寫錯值會印提醒。想設 block 的專案寫錯時會被靜默降成 warn,但這有印警語,屬設計內。
4. LUMOS_SKIP_DRIFT_CHECK 寫 0、true、"1 "(尾巴帶空白):都不略過,照擋(rc 1)。這符合「只認 1」的說法。
5. 範圍端點:
   - 起點全零(新分支)。
   - 起點是本機找不到的亂 sha。
   - 終點是 annotated tag 物件。
   - 反向範圍(遠端比本地新)。
   - 終點在本機找不到。
   前四種回 0 或正確的 1;最後一種回 2,掛鉤放行。
6. 筆記內容亂入:NUL 位元組、非 UTF-8 筆記、frontmatter 的 guards/plan_refs/status 型別亂、20 萬字元單行、CRLF、含代理對字元、檔名帶空白與引號、懸空 symlink。warn 模式下全部 rc 0、沒有 Traceback。
7. 一次推多個 ref 的成本:每次 drift check 約 1 秒(小專案),序列跑。工具鏈本身 HEAD~50..HEAD 約 1.4 秒。單次最壞 60 秒的預算是工具內建。若干十個 ref 的最壞總時間是相加,但拿不出具體失敗場景,不標。
8. 掛鉤與 CI 呼叫端:
   - ref 名不可能含空白(git 不允許),`read -r` 切四欄安全。
   - 刪除 ref(全零 local sha)在迴圈前段就 continue。
   - 引號齊全。
   - CI 該步只在 push 事件跑,fork PR 與 schedule 不會進來;push 事件本來就只綁 main,所以 before 為空的補零分支在 CI 上是死碼,無害。
   - CI 的 `rc=$?` 出現在 `||` 群組內,取到的是 drift 的回傳碼,正確。
   - CI 的 checkout 是 fetch-depth 0,不會遇到淺層 clone。
9. 既有測試 t_prepush_and_ci_wire_drift_check 在臨時 clone 跑:12 passed, 0 failed。

## 已知、不算 finding 的設計
- Python 未捕捉例外的回傳碼是 1,掛鉤會把它當「擋」。我用上面各種亂入輸入都沒逼出 Traceback,拿不出可重現的場景,所以不標。同一慣例也存在於 note-shape 那步。
- CI 的 drift 步靠 note-shape 步 fetch 好主線;若日後有人刪掉那步,drift 會靜默退化成空樹範圍。程式註解已寫明這個依賴。

## 圖譜鏡頭逐條判定
邊界席的範圍內,這份 diff 沒有動到鏡頭列出節點宣稱的行為。掛鉤只多一段呼叫,合約行(上線標記 `# lumos drift check`、rc1 才擋)在實測中維持;上線標記行仍在,判為不影響。

最高等級:clean
