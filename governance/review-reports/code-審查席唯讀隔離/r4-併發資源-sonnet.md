severity: major

# 第 4 輪 併發與資源席(sonnet)

範圍:r3 修正差異。實驗都在 /tmp/lumos-seat-work/code-審查席唯讀隔離/r4c(臨時複本,以 node --experimental-strip-types 直接跑 register.ts 的 createGuard,配假的 Io)。

### F1 /clear 與進行中的派工交錯:keep 的席被當成「結束後登記」而不登記,審查席整席不受限
severity: major
blocking: 是 — 守衛失效(fail-open):審查席在 /clear 之後拿不到任何限制
引句:「if (r && typeof r.agentId === 'string' && (endGen.get(session) ?? 0) === gen) {」
引句:「endGen.set(session, (endGen.get(session) ?? 0) + 1)」
時序:會談 S1 派一席(spawn 已把 gen 讀成 0、`await next(e)` 還沒回)→ 使用者 /clear,onEnd 帶 keep=true 呼叫 end,`endGen` 變 1 → 子代理被引擎建好、next 回 agentId。走到上面那行比較 0 !== 1,seats 與 $.state 都不寫。這一席明明是計劃要「/clear 不刪、背景還活著」保護的那種,卻從沒登記。之後它的工具呼叫:lookup 查不到、pending 也已被 end 清掉,`if (!seat) return null` 放行,Write 寫 repo 也過。
最小重現(已跑):假 Io、spawn 掛住 next,spawn 進行中呼叫 `g.end('S1', true)`,再 resolve next({agentId:'A1'}),印出 `registered after clear: undefined state []`,`g.call('S2',{agentId:'A1',tool:'Write',file_path:'/repo/x'})` 回 null(放行)。腳本 /tmp/lumos-seat-work/code-審查席唯讀隔離/r4c/t.mts。
建議方向:keep=true 時不要遞增 endGen(結束世代只在真的刪席時才有意義);或 keep 另記。同時補一支先紅測試。

### F2 end() 等整條存回佇列,存回卡住時 session.end 掛鉤永不返回
severity: minor
blocking: 否 — 需要 $.state 讀寫本身卡住,且只影響結束流程與後續存回
引句:「await Promise.race([save(), io.sleep(SAVE_MS)])」
引句:「return save(session)」
時序:`saving = saving.then(...)` 是單一串鏈,任何一次 loadVersioned/saveSeats 不返回,之後所有 save 都排在它後面。spawn 只等 2 秒就放手,但 `end` 直接 `return save(session)`,onEnd 的 `await st.guard?.end(...)` 無上限,`session.end` 掛鉤也就不呼叫 next;同時之後新登記的席永遠寫不進 $.state(熱重載後會脫離白名單)。逾時那次背景存回沒被取消,下一次存回正是排在它後面,這是逾時設計的必然後果,但 end 沒套同一個上限。
最小重現(已跑):loadVersioned 回永不 resolve 的 Promise;`spawn` 2003ms 返回;`g.end('S1')` 6 秒後仍未返回。腳本 .../r4c/t2.mts。
建議方向:end 也對存回做 Promise.race 上限(同 SAVE_MS 或另一個),超時就放手。

### F3 /clear 不刪席,舊會談編號的登記永遠不會被清,記憶體與 $.state 只增不減
severity: minor
blocking: 否 — 每席資料很小,增長速度受 /clear 次數與派工量限制;計劃已承認「只增不減」
引句:「if (keep) return Promise.resolve()」
時序:/clear 後行程換新會談編號,舊編號不會再有 session.end;`seats`、`sessionOf`、`bySession` 以及 $.state 的 seats 裡屬於舊會談的項目沒有任何路徑回收(只有同編號的非 keep end 才刪)。長壽行程反覆 /clear 加派審查席就一路長;每次存回又整份重寫,成本隨之上升(計劃第 113 行同一件事)。另外 `endGen` 每個結束過的會談編號留一筆數字,也不回收。計劃的 REVISIT 只寫 2026-11-06 實測 /clear,沒綁增長上限的回頭條件。
建議方向:給對照表一個上限或以最後使用時間淘汰,並寫成 REVISIT。

### F4 三次撞版都失敗時靜默放棄,只剩記憶體有席;沒有退避
severity: minor
blocking: 否 — 依賴三次連續撞版,正常只有熱重載前後兩份實例才有競爭
引句:「if (await io.saveSeats(merged, version)) return」
時序:兩份實例(熱重載前後)輪流寫,三次迴圈每次 loadVersioned 後都被對方搶先 → 迴圈結束沒有任何 throw 或提示,`catch {}` 也不會觸發,這一席只在本實例記憶體裡。實例若再熱重載,該席從 $.state 找不到,席位脫離白名單。迴圈之間沒有 await 讓出,對手實例在同一事件迴圈外運作才真能搶到,實務多半一次內成功。end(drop) 同樣吃這個:撞滿三次時被刪的會談席仍留在 $.state(只是多佔位)。
建議方向:撞滿時至少 toast 一次;或最後一次改無條件寫。

### F5 逾時存回的背景計時器與熱重載後各實例佇列
severity: minor
blocking: 否 — 沒有懸而不決的未處理拒絕;只是殘餘 2 秒計時器與兩份各自的佇列
引句:「await Promise.race([save(), io.sleep(SAVE_MS)])」
說明:save 先贏時 `io.sleep(SAVE_MS)` 沒被取消,每次登記留一個 2 秒計時器(熱重載時引擎會連同環境取消,型別檔 clock.sleep 段;被取消若以 reject 呈現,Promise.race 已掛處理器,不會變成未處理拒絕)。熱重載後新舊兩份實例各有自己的 `saving` 佇列,互相只靠 ifVersion 協調;舊實例的記憶體 `seats` 在每次存回時會被重新合併進 $.state,若新實例已用 end 刪掉該會談的席,舊實例下一次任何存回會把它們寫回(復活)。⚠ 舊實例熱重載後是否還會收到掛鉤,型別檔只說「環境被取消」,我沒有證據它仍會跑,所以降為 minor。兩個會談同時登記則走同一個 `saving` 串鏈,依序合併,沒有遺失更新。

### 圖譜鏡頭(LUMOS-IMPACT)
受影響測試、共改夥伴、呼叫者三格皆空,沒有席筆記條目可逐條判。Systems/lumos-guard 的更動(79 支、「r2、r3 的修正各自逐條撤回驗過會翻紅」)我沒有機械驗,但 F1 顯示現有測試沒有覆蓋「/clear 與進行中派工交錯」,計劃 S7 的 `/clear` 條款(「/clear 結束的會談,它的席應照擋」)只涵蓋已登記的席,與 F1 的缺口不矛盾也沒擋到。計劃「存回卡住時派工照常回傳」只對 spawn 成立,end 不成立(F2)。

總結:最嚴重 major,blocking 1 條
