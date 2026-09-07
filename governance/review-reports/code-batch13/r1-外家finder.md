# code-batch13 r1 — 外家finder

severity: major
<!-- 正規化:席位原本宣告 severity: high,而這個 repo 的詞彙只有 clean|minor|major|blocker。
     它自己沒宣告 blocker,就近對成 major。它的第 1 條(pid 重用)另有兩席獨立判 blocker,
     輪的最高嚴重度以那兩席為準,不因為這份對成 major 而降級。 -->

1. 活著但不屬於本次鎖的 PID，會讓 wrapper 永久誤判「另一份正在跑」

- severity: high
- blocking: 是
- file:line: `governance/daily-governance.sh:47`
- 引句:「`if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then`」

PID 可能被重用，或 pid 檔本來就寫了另一個活著的行程。程式只檢查 PID 是否存活，沒有核對行程身分或鎖齡；之後每次排程都會退出，而且健康檔不再更新。

怎麼重現：

```bash
oldpid=$PPID
if [ -n "$oldpid" ] && kill -0 "$oldpid" 2>/dev/null; then
  printf '另一份 daily-governance 正在跑(pid %s),本次退出——不搶寫紀錄\n' "$oldpid"
fi
```

實際輸出：

```text
另一份 daily-governance 正在跑(pid 43436),本次退出——不搶寫紀錄
```

這裡的 `43436` 是仍活著、但不是 daily-governance 的父行程。只要它長期存活，wrapper 就不會接管。

2. 健康檔時間格式錯誤且 `total=0` 時，看門狗靜默判成正常

- severity: high
- blocking: 是
- file:line: `governance/wrapper-watchdog.sh:82`
- 引句:「`if [ -n "$age" ] && [ "$age" -gt "$STALE_SEC" ]; then`」

時間解析失敗會令 `age=""`。控制流沒有把這種情況判為 unreadable，而是繼續檢查 `total`；若 `total=0`，便落到 `now_state="ok|$today"`，不輸出告警。

怎麼重現：

```bash
fin=not-a-time
total=0
age="$(python3 -c '
import datetime,sys
d=datetime.datetime.fromisoformat(sys.argv[1].replace("Z","+00:00"))
print(int((datetime.datetime.now(datetime.timezone.utc)-d).total_seconds()))
' "$fin" 2>/dev/null || echo '')"

if [ -n "$age" ] && [ "$age" -gt 129600 ]; then
  now_state=stale
elif [ "$total" != 0 ]; then
  now_state=failed
else
  now_state=ok
fi
printf 'fin=%s age=<%s> total=%s now_state=%s\n' \
  "$fin" "$age" "$total" "$now_state"
```

實際輸出：

```text
fin=not-a-time age=<> total=0 now_state=ok
```

3. 五步成功但健康檔寫入失敗時，整支仍回傳成功

- severity: major
- blocking: 是
- file:line: `governance/daily-governance.sh:133`
- 引句:「`提醒:健康狀態檔寫不進去($HEALTH)——看門狗會把這次當成沒跑完`」

`write_health` 失敗只印提醒，沒有改變 `total`。五步皆成功時，磁碟不可寫、tmp 衝突或 `mv` 失敗仍回傳 0。排程端會認為成功；看門狗只能等舊健康紀錄超過 36 小時後才發現。

怎麼重現：

```bash
main() {
  local total=0
  write_health() { return 1; }
  ts() { printf T; }
  local HEALTH=/unwritable/health

  write_health ||
    echo "[$(ts)] 提醒:健康狀態檔寫不進去($HEALTH)——看門狗會把這次當成沒跑完" >&2
  echo 完成
  return "$total"
}
main
echo "shell_rc=$?"
```

實際輸出：

```text
[T] 提醒:健康狀態檔寫不進去(/unwritable/health)——看門狗會把這次當成沒跑完
完成
shell_rc=0
```

其餘已核對：

- 全成功時，`for` 最後的 `[ 0 -ne 0 ]` 結束碼確實是 `1`，但它沒有改壞 `total`；後續 `write_health`、`echo` 之後明確 `return "$total"`，因此這點找不到 bug。

```text
loop_status=1 total=0
after_write_status=0 return_value=0
```

- 兩支腳本 `bash -n` 均通過：

```text
bash_n_rc=0
```

- 本輪無法完成要求的完整五步故障矩陣、實體鎖競態、半寫健康檔及 tmp 名稱碰撞：唯讀沙盒連 `/tmp` 都禁止建立。

```text
mktemp: mkdtemp failed on /tmp/finder13.qHDov1: Operation not permitted
```

因此上面只列出能以不落檔的原樣控制流實驗重現者，沒有替未實跑項目湊 finding。
