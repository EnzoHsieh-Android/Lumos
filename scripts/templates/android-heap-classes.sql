-- SPDX-FileCopyrightText: 2026 Enzo Hsieh
-- SPDX-License-Identifier: MIT
--
-- 記憶體與穩定性收集:一份 Java 快照(Perfetto java_hprof,由 skill 的 java_heap_dump 錄)裡,每個類別還有人指著的實例數
--   只算 reachable 的物件(等於回收之後的樣子);同名類別出現在不同 classloader 時加總成一列
--   收集腳本對暖機後與 N 輪後兩份快照各跑一次,增減由 lumos macrobench 的 java_growth 判
-- 用法:把 __PROCESS__ 換成 App 的行程名(套件名,只收英數字、底線與點),交給 trace_processor 跑,
--   複製進收據的 queries.sql 時上面加一行 -- [Qn] session=<名> trace=<artifact id> requires=- expect=-
--   expect 寫 -(只記錄、不比對):快照 7 天後會被刪,寫了 expect 重跑會誤報成比對不符
--   第一欄是類別名:重跑腳本拿第一欄當鍵
-- 只用標準 SQLite 語法與 process、heap_graph_object、heap_graph_class 三張表(測試用 Python 內建的 sqlite3 建同名的表跑)
-- 規則單源 Projects/Android記憶體與穩定性驗收_計劃
-- 註解一律不以分號結尾:收據的重跑腳本拿第一個以分號結尾的行當查詢結尾
SELECT c.name AS class, COUNT(*) AS instances
FROM heap_graph_object o
JOIN heap_graph_class c ON o.type_id = c.id
JOIN process p ON o.upid = p.upid
WHERE p.name = '__PROCESS__' AND o.reachable
GROUP BY c.name
ORDER BY c.name;
