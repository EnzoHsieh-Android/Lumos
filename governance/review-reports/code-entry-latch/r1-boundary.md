# code r1 邊界輸入席

**B-1**|major|blocking:是(單靠既有隨機 fixture 就有 ~14% 機率翻紅的真 flaky test+產品行為違反 EL-15)
引句:「不丟則 auto-2026-08-23 整顆存活、誠實分支永不觸發,r2 D-5 實測」
`auto-2099-01-{_M1U[:2]}` 尾碼為兩字母(36/256=14.06%)時「ab」漏過濾網(非母 token/非數字/長度>1),tokens=2 → queried=True → EL-15 紅釘翻紅。25 連跑 3 次翻紅;monkeypatch _M1U="abcdef" 直接重現。

**B-2**|minor|blocking:否
引句:「濾純數字(「2026」命中 381/385=全庫召回)與長度 1 的 ASCII token」
單字濾網限定 isascii,單一常見漢字(「的」)未濾——暫用 vault 實測 100% 召回,同 2026 病徵。

抑噪:空後綴/全數字/全形/emoji/500字/純底線皆安全;--json dumps 非 ASCII 無虞;PYTHONIOENCODING=ascii 下會炸但 HEAD~1 同炸(既有前提非本 patch);B 的 .MD/資料夾缺席/空 notes/單檔 vault 皆正常;EL-4/EL-13 兩紅釘經改壞對應碼確實翻紅(還原淨空);rc 語意 HEAD vs HEAD~1 一致,monkeypatch 逼炸 advisory 後 rc/stdout/檔案落地與無例外時相同(fail-open 有效)。

severity: major
