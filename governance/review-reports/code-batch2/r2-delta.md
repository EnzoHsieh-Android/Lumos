### d-f1 fallback 重引入跨輪借 tier(判定輪沒記 tier 時借別輪的)——換了觸發條件的同型病
severity: major
引句:「or next((r.get("tier") for r in rounds if r.get("tier")), None)」
佐證:file: `scripts/lumos:5062`
說明:席位實跑:r2 判定輪無 tier 被套 r1 standard 編制。應回退「沒有編制表可以對」而非借用;分支零 pin。

### d-f2 doctor 與 lint-check 兩套 root 解析同題不同答案;lint-check 找不到 root 靜默 rc0=有問題偽裝乾淨
severity: major
引句:「_lf = _lint_load_and_validate(_vault_repo_root(env))」
佐證:file: `scripts/lumos:11004`
佐證:file: `scripts/lumos:10031`
說明:席位實跑:同 repo 壞宣告,doctor 抓到、lint-check 從無關 cwd 跑=「找不到 git repo」後 rc0。另 [F] 區塊註解仍寫 _repo_root_from_env(代碼已換)=文件漂移。

### d-f3 code-boom 釘零區辨力:except 探針全程未觸發,rc 相等純因旁支本就不影響 rc
severity: major
引句:「以壞 dispatch 逼不動,改 monkeypatch 層級」
佐證:file: `scripts/lumos:5023`
說明:壞 dispatch 被內部 except 吞掉不外拋;釘與其聲稱要測的降級路徑無實際關聯。

### d-f4 __seqN 釘仍假:快照檔名 r1-dispatch 對 rid=__seq0 的 glob 永不匹配,拔 guard 依舊 8 綠
severity: major
引句:「快照在場,突變驗證:拔跳過→印出翻紅」
佐證:file: `scripts/lumos:10126`
說明:席位真拔 guard 全綠;fixture 快照要命名 __seq0-dispatch.json 才有區辨力。

## 查過乾淨
ext-f2/ext-f1 兩釘有效;健康 fixture 席位表精確非灌水;位置斷言與真實順序一致;改名純機械;告示/INDEX 同步無風險。
