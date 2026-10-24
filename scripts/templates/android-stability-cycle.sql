-- SPDX-FileCopyrightText: 2026 Enzo Hsieh
-- SPDX-License-Identifier: MIT
--
-- 記憶體與穩定性收集:N 輪量測期間那一份追蹤檔算一列數字,給收集腳本(android-stability-collect.sh)寫進 stability.json 的 cycle_trace
--   peak_anon_swap_kb  App 的匿名常駐記憶體加 swap 的最大值(KB);swap 取樣比較稀,每個 mem.rss.anon 取樣點配它之前最近一次的 swap
--                      (swap 先排成「這一筆到下一筆」的區間再配,不對每個取樣點各跑一次子查詢:真實追蹤檔從 73.8 秒降到 0.26 秒,代碼審 r1 資源席,
--                      區間配對仍隨取樣數平方成長,只是常數小很多,預設 600 秒錄製約 2400 個取樣點影響不到,代碼審 r2 資源席)
--   frozen_frames      超過 700ms 的幀數:有幀時間線(Android 12 以上)用 actual_frame_timeline_slice,沒有時用主執行緒名稱以 Choreographer#doFrame 開頭的區段
--   max_main_block_ms  主執行緒最上層區段裡最長的那個(毫秒),只回報
--   frames             算凍結幀時用的那一種來源一共幾幀;是 0 表示沒錄到畫面,判定會列成跳過
-- 量不到的欄位輸出 -1(重跑腳本比對 expect 時寫得出來,trace_processor 的空值會印成 [NULL])
-- 用法:把 __PROCESS__ 換成 App 的行程名(套件名,只收英數字、底線與點),交給 trace_processor 跑,
--   複製進收據的 queries.sql 時上面加一行 -- [Qn] session=<名> trace=<artifact id> requires=- expect=cycle:frozen_frames=<值>
--   第一欄是字串 cycle:重跑腳本拿第一欄當鍵
-- 只用標準 SQLite 語法與 process、thread、thread_track、slice、process_counter_track、counter、actual_frame_timeline_slice 七張表
--   (測試用 Python 內建的 sqlite3 照 Perfetto 文件建同名的表跑同一支檔)
-- 規則單源 Projects/Android記憶體與穩定性驗收_計劃
-- 註解一律不以分號結尾:收據的重跑腳本拿第一個以分號結尾的行當查詢結尾
WITH
app AS (SELECT upid, pid FROM process WHERE name = '__PROCESS__'),
anon AS (
  SELECT c.ts, c.value FROM counter c JOIN process_counter_track t ON c.track_id = t.id
  WHERE t.name = 'mem.rss.anon' AND t.upid IN (SELECT upid FROM app)
),
swp AS (
  SELECT c.ts, c.value FROM counter c JOIN process_counter_track t ON c.track_id = t.id
  WHERE t.name = 'mem.swap' AND t.upid IN (SELECT upid FROM app)
),
swp_span AS (SELECT ts, LEAD(ts) OVER (ORDER BY ts) AS next_ts, value FROM swp),
peak AS (
  SELECT MAX(a.value + COALESCE(s.value, 0)) AS v FROM anon a
  LEFT JOIN swp_span s ON a.ts >= s.ts AND (s.next_ts IS NULL OR a.ts < s.next_ts)
),
main_track AS (
  SELECT tt.id AS track_id FROM thread_track tt JOIN thread th ON tt.utid = th.utid JOIN app ON th.upid = app.upid
  WHERE th.tid = app.pid
),
timeline AS (SELECT dur FROM actual_frame_timeline_slice WHERE upid IN (SELECT upid FROM app)),
doframe AS (SELECT dur FROM slice WHERE track_id IN (SELECT track_id FROM main_track) AND name LIKE 'Choreographer#doFrame%'),
frames AS (
  SELECT dur FROM timeline
  UNION ALL
  SELECT dur FROM doframe WHERE NOT EXISTS (SELECT 1 FROM timeline)
)
SELECT
  'cycle' AS key,
  COALESCE((SELECT CAST(v / 1024 AS INT) FROM peak), -1) AS peak_anon_swap_kb,
  (SELECT COUNT(*) FROM frames WHERE dur > 700000000) AS frozen_frames,
  COALESCE((SELECT MAX(dur) / 1000000 FROM slice WHERE track_id IN (SELECT track_id FROM main_track) AND depth = 0), -1) AS max_main_block_ms,
  (SELECT COUNT(*) FROM frames) AS frames;
