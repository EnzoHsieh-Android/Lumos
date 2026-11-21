severity: minor

## Finding 1
severity: minor
blocking: 否

「全程線性」的宣稱只對數字尾巴成立。席名裡夾換行字元時,`_SEAT_SPLIT_RE` 還是二次方。

- 輸入:席名是 `"-a"*N + "\nx"`,即很多個「連字號加字母」,再接一個換行。
- 行號:`scripts/lumos` 的 `_SEAT_SPLIT_RE = re.compile(r"^(.*?)-(?=[A-Za-z])(.*)$")`,由 `_seat_noise_name` 呼叫。
- 原因:`.` 不跨換行,`(.*)$` 每個連字號都要掃到換行才失敗。
- 帳上的列是 JSON,換行可以用跳脫寫進席名。
- 量測,修前 af2fb6 與修後 aff4a9 相同:
  - N=10000(約 20KB):0.62 秒。
  - N=20000(約 40KB):2.48 秒。
  - 倍數是 4 倍,確認是二次方,約 200KB 會到十幾秒。
- 修補只處理了十萬個數字的案例。該案例修前 43.86 秒,修後 0.0 秒。
- 影響範圍:只拖慢 `gov --stats`,不擋寫入,也不讓測試誤紅。在單人、依序操作的威脅模型下是低風險。
- 建議:regex 加 `re.S`,或改用 `name.find`,或在 `.strip()` 之後把控制字元收成空白。

引句:「全程線性,不用會回溯的尾端正規式(代碼審 r2 資源 1:十萬字元的席名原本要跑 40 秒)」

歸因:有證據的原有漏查。這條 regex 在修前就存在,兩版行為相同。

查證命令與結果:
```
python3.14 /tmp/lumos-seat-work/code-發現記出處席位/資源-sonnet/t.py
```
```
af2fb6 digits 43.86
af2fb6 newline-20k 0.62
af2fb6 newline-40k 2.48
aff4a9 digits 0.0
aff4a9 newline-20k 0.62
aff4a9 newline-40k 2.48
```

## 固定席與圖譜
這次沒附固定席節點,以下用 diff 自己列的改動面判斷。
- 計劃節點 `代碼審發現記出處席位_計劃.md`:只多一行審查紀錄,不影響程式行為。
- `Systems/loop-convergence-recording.md`:只補說明,不影響行為。
- 手冊三份的「目前 YYYY-MM-DD」:由 `t_finding_seat_docs_match_since` 機械核對,只認 SKILL.md、reference.md、`06-代碼審與推送.md` 三份。這一點沒另行驗證。

## 三問
1. **子程序與執行緒**:本 diff 沒有新增子程序、執行緒或計時器。`_gate_event_or_warn` 是既有的同步寫帳。逾時、Ctrl-C 與例外下沒有東西需要收。
2. **時間預算**:
   - `t_gov_stats_finding_seat` 整支只花 2.6 秒,距離 180 秒上限有 69 倍餘裕。
   - 其中「10 秒內跑完」的斷言只計 `gov --stats` 那一次呼叫,實際遠小於 10 秒,慢機器上誤紅的風險低。
   - `t_canary_record_finding_seat` 整支 47 個斷言約 39 秒,在上限內。
3. **記憶體與二次方**:
   - 數字尾巴已改線性,`rstrip` 加 `nfc` 在十萬字元下是 0.0 秒。
   - 必填判斷多掃帳上各列時間,是線性。
   - 殘留的只有 Finding 1 的換行二次方。

最嚴重等級 minor
