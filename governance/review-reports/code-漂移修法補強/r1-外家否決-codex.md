severity: major

## F1 消費專案按檔名跳過，會漏查使用者已改寫的檔案

severity: major

blocking: 是

引句:「+        parsed = _delguard_parse_diff(r.stdout, gr_rel, frozenset() if _is_toolchain_repo(root) else _VENDORED_ALL)」

file: `scripts/lumos:29549`  
file: `scripts/lumos:17779`

1. 非工具鏈 repo 無條件把整份 `_VENDORED_ALL` 當跳過集合，完全不看 `.lumos/vendored.json` 指紋。使用者改寫過 `scripts/hooks/pre-push` 等同名檔後，內容已不是安裝版，仍會整支排除。
2. 現有 `_vendored_state` 明確把「指紋不符或 manifest 不存在」定義成不跳過；本改動繞過這個既有判準。因此筆記仍引用被刪符號時，delguard 不會抽到 token，也不會提醒，只留下 `vendored-skip=` 假裝是工具檔。
3. 已用唯讀的純解析重現：

```text
輸入: scripts/hooks/pre-push 刪除 UserOwnedDeployGuard
帶 _VENDORED_ALL:
{'tokens': [], 'vault_diffs': {}, 'vendored_skipped': ['scripts/hooks/pre-push']}

不帶跳過集合:
{'tokens': ['UserOwnedDeployGuard'], 'vault_diffs': {}, 'vendored_skipped': []}
```

4. 計劃雖把「使用者改過工具檔仍漏看」列為誠實界線，但這正是本席指定要否決的消費專案漏查使用者檔案情境；揭露與日後回訪不會讓目前的守衛結果變正確。

## F2 c4 丟掉卷證目錄的原始 Unicode 拼法

severity: major

blocking: 是

引句:「+        d = nfc(parts[2]) if len(parts) >= 4 and parts[:2] == ["governance", "review-reports"] else ""」

file: `scripts/lumos:27952`  
file: `scripts/lumos:27960`  
file: `scripts/lumos:28011`

1. `_drift_c4_existing` 建的是 `{NFC 名: 原名}`，但後續從未取回 value；同提交與計劃名兩路都把 NFC key 當成要顯示的真目錄名。
2. 目錄使用分解 Unicode 時，證據頁會印出另一串碼位；兩個 NFC 等價但實際不同的 Git 目錄還會在 dict 中合併成一個。這違反 S1「目錄名照原樣、全部列出」，使用者可能把不等於 Git 真實路徑的字串寫入驗證前提。
3. 已用唯讀函式重現：

```text
original= 'Café'
result= ['Café']
equal= False
```

應把 NFC 只當比對鍵，輸出時保留原名；若存在正規化碰撞，不能靜默去重。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：F2 破壞 c4 證據頁列出真實卷證目錄的行為；c1 共用訊息與 c3 理由本身未見另洞。
- `Systems/bound-tests-gate`：未改合約測試的解析、執行或退出碼判定，不影響其合約。
- `Systems/guard-kill`：只改 settle 缺句訊息，未動 kill 七態、退出碼優先序或 JSON 純度。
- `Systems/授權與歸屬`：未改 `_VENDORED_ALL` 成員及授權檔處理，不影響兩條授權合約。
- `Systems/測試假綠形態`：新增測試只覆蓋未改寫的 vendored 檔與 NFC 目錄，沒有走到 F1、F2 的失敗分支，故未能防住這兩項回歸。
- `Systems/lumos-cli-read`：未改 search 的 stale／superseded 濾網，不影響其合約。
- `Systems/lumos-cli-lifecycle`：未改 reinject 區塊替換，不影響 sentinel 外內容 byte-equal 合約。
- `Systems/design-loop`：未改處置閘或 spec 材料判定，不影響其合約。

最高等級:major