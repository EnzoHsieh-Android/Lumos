severity: minor

整合與知識同步鏡頭,第 3 輪。我讀了完整修補差異、跑了 `-k finding_seat`(65 passed,0 failed),也用小腳本直接呼叫 `_seat_noise_name` 與 `_finding_seat_required_block`。派工詞指定的 `-k seat_noise` 選中 0 個測試,視為失敗,我改跑 `finding_seat` 取代。固定席節點沒附(鏡頭計算超時),所以圖譜判定只能逐項說明,不是逐條節點判。

## Finding 1:系統筆記同一行自相矛盾,計劃筆記兩處仍寫「壞時間擋下」
severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:224`
引句:「帳上有時間讀不動的列時判不了生效前後,不放行。席名去空白、NFC 後比同輪帳上的」
失敗場景:
- 這一行同時留著兩句話。第一句是上面的引句,說壞時間列「不放行」。第二句是修補新增的「本筆時間早於生效日就直接不必填,帳上有壞時間的列也不擋」。
- 三個月後的人照第一句會以為壞時間列一律擋,實際程式是 `_finding_seat_required_block` 先看 `rec_k < since` 就 `return None`。
- 同一個矛盾還在 `docs/lumos-toolchain-knowledge/Projects/代碼審發現記出處席位_計劃.md:52`(「帳上有一筆時間讀不動或沒帶時區,照那條先例判「壞資料」擋下、不放行」)。
- 該計劃第 131 行依據表(「壞時間不放行」)也一樣,但同檔第 103 行〈回退〉的措辭已經是新行為。
- 修補只改了 reference 與系統筆記的後半句,沒改這幾處。

兩版查證:
- 修前 `af2fb6f85` 的行為確實是壞時間列一律擋,所以修前這些句子是對的。
- 修後 `aff4a913c` 行為變了,舊句沒刪。
- 查證命令:`grep -n '時間讀不動' docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`,兩版都有命中,修後不該再有那句。

歸因:有證據的修復回歸。語意改了,但同一行內的舊句和計劃兩處沒跟著改。

## Finding 2:帳上時間全壞加環境變數覆寫時,推遲必填不提醒也不留事件
severity: minor
blocking: 否
file: `scripts/lumos:19612`
引句:「first = min(good) if good else (rec_k if not keys else None)」
失敗場景:
- 帳上只有壞時間的列(例如 `[{"ts":"garbage"}]`),`LUMOS_FINDING_SEAT_SINCE` 推到未來,本筆時間早於生效日。
- 此時 `first=None`,`first is not None and first >= const` 不成立,所以不印提醒、不留 `finding-seat-since-overridden` 事件,靜默放行。
- 修補要補的正是 r1 資安點「殘留的覆寫不能靜默推遲必填」。
- 實測:常數設 2020、覆寫設 2999,rows 為 `[{"ts":"garbage"}]` 時回傳 None 且沒有提醒。rows 為 `[{"ts":"2025-01-01T00:00:00+08:00"}]` 或空帳時有提醒。
- 這需要壞列加殘留覆寫兩個條件同時成立,而且只在載體席要放行時才出現,所以只給 minor。

兩版查證:
- 修前壞時間列直接 rc2 擋下,走不到這條路徑。
- 修後 `first=None` 靜默放行。
- 查證命令:用上面的小腳本,環境變數 `LUMOS_FINDING_SEAT_SINCE=2999-01-01`,把 `_FINDING_SEAT_SINCE` 設成 `2020-01-01T00:00:00+08:00`,再傳 `[{"ts":"garbage"}]` 給 `_finding_seat_required_block`。

歸因:有證據的修復回歸。「壞時間不擋」的新分支留下這個漏口。

## 其他已核對、無發現
- **擋下事件(G1)**:`finding-seat-missing`、`finding-seat-unknown`、`finding-seat-badts` 都在擋下處直接呼叫 `_gate_event_or_warn(..., hard=True)`,迴圈名與席名過 `_esc_clean`。推遲提醒是 `warned` 事件。新旗標沒有再包一層自寫函式,跟鄰居 `refuted-set-missing` 一致。
- **席名分列(G3)**:實測 `正確性-2-sonnet`、`外家codex-5-mini`、`外家codex-6-mini`、`外家finder-2-codex`、`gemini-2` 原樣保留。`架構對齊r2-sonnet`、`鏡頭2-sonnet`、`正確性r2-sonnet` 去掉輪次。`" 空白席-sonnet "` 併成 `空白席-sonnet`。`外家finder2-codex` 會併到 `外家finder-codex`,修前的規則也是如此,reference 已寫明「鏡頭編號跟輪次分不出來」。
- **文件對程式(G5)**:`--help` 寫明要跟 `--loop`、`--round`、`--findings-set` 一起給,SKILL.md 第 6 步指令與 reference 範本行尾 `\` 接續一致,`t_finding_seat_docs_match_since` 綠。06 命令速查的「目前 2026-11-22」等於常數。
- **範例是否漏改**:全 repo grep `refuted-set`,代碼審載體範本與範例只出現在 SKILL.md 與 reference.md,都已帶 `--finding-seat`。05 設計審手冊是設計審,不必填。

## 圖譜鏡頭(固定席未附)
- `Systems/loop-convergence-recording` 與 `Projects/代碼審發現記出處席位_計劃` 受影響,有同步,但見 Finding 1 的舊句殘留。
- `Systems/canary-audit` 的 d4 否決跨期統計,reference 的結尾一條已說明不涵蓋這一欄。這輪沒有新動。
- 注意:`Projects/記帳與迴圈工具小修_計劃` S27 寫的「兩條」提示已在 reference 註明是當時範圍,不影響。

## 三問
1. 原問題修復效果:事件包裝改回直呼、席名線性化、壞時間列在本筆早於生效日時不擋、覆寫留事件,這些都有測試與直接呼叫證據。唯一漏口是 Finding 2。
2. 相鄰路徑:本筆不早於生效日加壞列仍 rc2 擋下,首筆早於生效日不必填,空帳看本筆,三條都維持。
3. 新發現的同一案例修前修後:Finding 1 修前句子正確、修後過期。Finding 2 修前 rc2 擋下、修後靜默放行。

最嚴重等級 minor
