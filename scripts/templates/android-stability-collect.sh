#!/bin/sh
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# lumos 記憶體與穩定性收集:在主機端排順序、用 adb 收記憶體與穩定性資料,寫成 .lumos/artifacts/android/<run-id>/stability.json;
# 不判過不過(判定在 lumos macrobench --stability)。單一來源在工具鏈 scripts/templates/,消費專案照抄;規則單源 Projects/Android記憶體與穩定性驗收_計劃。
# 用法:在專案根目錄跑 sh scripts/templates/android-stability-collect.sh [run-id]
# 外部工具:ADB(預設 adb)、TP(trace_processor)、JAVA_HEAP_DUMP(skill 的 java_heap_dump,宣告了測試資料才用)
# 測試縮短用:LUMOS_STABILITY_SETTLE(等 App 起來、等日誌跟上,預設 2 秒)、LUMOS_STABILITY_STOP_TIMEOUT(等錄製停下,預設 30 秒)、
#   LUMOS_STABILITY_LONG_TIMEOUT(驅動、原生掃描、快照與查詢的上限,預設 1800 秒)
# 回傳碼:結果檔寫出來回 0(哪一段沒收到寫在那個來源的 status);設定讀不了、必要工具找不到、run-id 不合法或用過、
#   產物沒被 git 忽略、mapping 檔不在、被中斷都回 2 並印「擋下:」,不寫結果檔
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null || { echo "擋下:收集腳本要 python3 3.11 以上(用了 -P)" >&2; exit 2; }
# -P:不把目前目錄放進模組搜尋路徑(在放了外來 .py 的目錄執行也不會載入它);拿掉 PYTHONPATH,殘留的路徑也不載入;
# 不用 -I,-I 會連 PYTHONUTF8 一起忽略(代碼審 r1 架構對齊席、r2 資安席)
exec env -u PYTHONPATH PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -P - "$HERE" "$(pwd)" "${1:-}" <<'PY'
import json, os, re, shutil, signal, subprocess, sys, tempfile, time
here, root, run_id = sys.argv[1], sys.argv[2], sys.argv[3] or time.strftime("stability-%Y%m%d-%H%M%S")
ADB, TP, JHD = os.environ.get("ADB", "adb"), os.environ.get("TP", "trace_processor"), os.environ.get("JAVA_HEAP_DUMP", "java_heap_dump")
T_SHORT = 120   # 秒:一般 adb 呼叫
T_LONG = float(os.environ.get("LUMOS_STABILITY_LONG_TIMEOUT", "1800"))   # 秒:驅動、原生掃描與快照查詢的上限(測試縮短用)
SETTLE = float(os.environ.get("LUMOS_STABILITY_SETTLE", "2"))   # 等 App 起來、等日誌串流跟上的秒數(測試縮短用)
STOP_WAIT = float(os.environ.get("LUMOS_STABILITY_STOP_TIMEOUT", "30"))   # 送 TERM 後等錄製結束的秒數,等完還在就補 KILL
REAP = 10   # 秒:整組殺掉之後等管線關掉的上限
GROUPS = []   # 正在跑的子程序(每個都自成程序群組):被中斷時整組收掉
ARTIFACTS = ("stability.json", "logcat.txt", "logcat.raw", "cycle.pftrace", "record.pbtxt", "heap-before.pftrace", "heap-after.pftrace")
EXIT_TYPES = {3: "low_memory", 4: "crash", 5: "native_crash", 6: "anr"}


def die(msg):
    print(f"擋下:{msg}", file=sys.stderr)
    sys.exit(2)


INTERRUPTS = (signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT)   # 轉成例外、走 cleanup 的訊號(Ctrl-C 是 KeyboardInterrupt,另外接)


class Terminated(Exception):
    """收到 SIGTERM、SIGHUP 或 SIGQUIT:轉成例外,讓 finally 收掉裝置上的錄製與主機上的子程序(Python 預設收到 SIGTERM 直接結束、finally 不會跑)。"""


def stop_listening():
    """收到第一個中斷就把所有中斷都設成忽略,再往下走收尾:兩個訊號幾乎同時到時,第二個不能打斷收尾(代碼審 r4 資源席)。"""
    for s in INTERRUPTS + (signal.SIGINT,):
        signal.signal(s, signal.SIG_IGN)


def on_term(signum, frame):
    stop_listening()
    raise Terminated()


def on_int(signum, frame):
    stop_listening()
    raise KeyboardInterrupt()


def kill_group(p):
    """整組殺掉;跟 lumos 的 _kill_proc_group 同一套(拿不到它,因為這是獨立的 python):沒有 killpg 時退回只殺這一個。"""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (OSError, AttributeError):
        try:
            p.kill()
        except OSError:
            pass


def run(cmd, timeout=T_SHORT, **kw):
    """回 (回傳碼, 標準輸出, 標準錯誤);逾時或執行不了回 (None, '', 原因)。每個子程序都自成一個程序群組,
    逾時或被中斷時整組殺掉:驅動是 sh -c、java_heap_dump 是 shell 腳本,底下的程序會握著輸出管線,
    只殺最外層的話要等到它們自己結束才回得來(代碼審 r2 資源席);殺完再等管線關掉也有上限。"""
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace",
                             start_new_session=True, **kw)
    except OSError as e:
        return None, "", f"執行不了({e.strerror})"
    GROUPS.append(p)
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        kill_group(p)
        reap(p)
        return None, "", f"逾時({timeout} 秒)"
    except BaseException:   # SIGTERM 或 Ctrl-C 打斷等待:先收掉子程序(整組)再往上丟,不然下面的 finally 會先把它從待收清單拿掉
        kill_group(p)
        raise
    finally:
        GROUPS.remove(p)


def reap(p):
    """整組殺掉之後收屍:管線 REAP 秒內還沒關(底下有程序另開了自己的群組)就不等了。"""
    try:
        p.communicate(timeout=REAP)
    except subprocess.TimeoutExpired:
        for f in (p.stdout, p.stderr):
            f.close()


def adb(*args, timeout=T_SHORT):
    return run([ADB, *args], timeout=timeout)


def shell(cmd, timeout=T_SHORT):
    return adb("shell", cmd, timeout=timeout)


def load_config():
    lumos = os.path.join(here, "..", "lumos")
    rc, out, err = run([sys.executable, lumos, "macrobench", "--repo", root, "--check-config"])
    if rc != 0:
        die((err or out).strip().removeprefix("擋下:") or "lumos macrobench --check-config 沒過")
    try:
        cfg = json.load(open(os.path.join(root, ".lumos", "macrobench.json"), encoding="utf-8-sig"))
    except Exception as e:
        die(f".lumos/macrobench.json 讀不了:{e}")
    st = cfg.get("stability")
    if not isinstance(st, dict):
        die(".lumos/macrobench.json 沒有 stability 段")
    return st


def prune_old_snapshots():
    """只刪這個專案產物目錄底下超過 7 天的 heap-*.pftrace(快照可能含個資,保存規則見計劃)。"""
    base = os.path.join(root, ".lumos", "artifacts", "android")
    cutoff = time.time() - 7 * 86400
    if not os.path.isdir(base):
        return
    if os.path.islink(base):   # 產物目錄是捷徑時不刪(會刪到捷徑指去的別處)
        return
    for d in os.listdir(base):
        p = os.path.join(base, d)
        if os.path.islink(p) or not os.path.isdir(p):
            continue
        for f in os.listdir(p):
            fp = os.path.join(p, f)
            if re.fullmatch(r"heap-.*\.pftrace", f) and not os.path.islink(fp) and os.path.isfile(fp) and os.path.getmtime(fp) < cutoff:
                os.unlink(fp)


def parse_exit_info(text, pkg):
    """dumpsys activity exit-info <套件>。回 (status, 紀錄清單或原因):只有全域標頭沒有套件區段是零筆。"""
    if not re.search(r"^\s*ACTIVITY MANAGER PROCESS EXIT INFO", text, re.I | re.M):
        return "failed", "輸出沒有全域標頭(格式變了或指令失敗)"
    recs, cur, in_pkg = [], None, False
    for line in text.splitlines():
        m = re.match(r"\s*package:\s*(\S+)", line)
        if m:
            in_pkg = m.group(1) == pkg
            continue
        if not in_pkg:
            continue
        if re.match(r"\s*ApplicationExitInfo #\d+:", line):
            cur = {}
            recs.append(cur)
            continue
        if cur is None:
            continue
        for k, v in re.findall(r"(timestamp|pid|reason|description)=(\d{4}-\d\d-\d\d [\d:.]+|\S+)", line):
            cur.setdefault(k, v)
        d = re.search(r"description=(.*?)(?: state=| trace=|$)", line)
        if d:
            cur["description"] = d.group(1).strip()
    return "ok", [r for r in recs if "pid" in r and "timestamp" in r]


def classify(r):
    reason = int(r.get("reason", "-1")) if str(r.get("reason", "")).lstrip("-").isdigit() else -1
    if reason in EXIT_TYPES:
        return EXIT_TYPES[reason]
    return "memory_limiter" if "MemoryLimiter" in r.get("description", "") else "other"


def exit_diff(before, after):
    seen = {(r["pid"], r["timestamp"]) for r in before}
    return [{"type": classify(r), "reason": int(r["reason"]) if r.get("reason", "").isdigit() else None,
             "pid": int(r["pid"]) if r["pid"].isdigit() else r["pid"], "timestamp": r["timestamp"],
             "desc": r.get("description", "")} for r in after if (r["pid"], r["timestamp"]) not in seen]


def read_exits(pkg):
    rc, out, err = shell(f"dumpsys activity exit-info {pkg}")
    if rc != 0:
        return "failed", f"dumpsys activity exit-info 失敗:{err.strip() or rc}"
    return parse_exit_info(out, pkg)


def unreachable(pid):
    rc, out, err = shell(f"dumpsys -t 300 meminfo --unreachable {pid}", timeout=T_LONG)
    m = re.search(r"(\d+)\s+bytes in\s+(\d+)\s+unreachable allocation", out)
    if rc != 0 or not m:
        # 不帶標準輸出:總量那行之後是每塊沒人指著的配置的十六進位傾印,是 App 的原生記憶體內容(代碼審 r3 資安席);
        # 標準錯誤的最後一行(adb 離線、逾時)照留,才看得出為什麼讀不到(r4 正確性席)
        why = err.strip().splitlines()[-1][:120] if err.strip() else ""
        return None, f"dumpsys meminfo --unreachable 讀不到總量那行(回傳碼 {rc}{':' + why if why else ''});標準輸出可能含 App 記憶體內容,不留"
    return {"bytes": int(m.group(1)), "allocations": int(m.group(2))}, None   # 只留總量,丟掉每塊開頭內容


def native_heap_kb(pkg):
    rc, out, _ = shell(f"dumpsys meminfo {pkg}")
    m = re.search(r"^\s*Native Heap:\s+(\d+)", out, re.M)
    return int(m.group(1)) if rc == 0 and m else None


def pidof(pkg):
    rc, out, _ = shell(f"pidof {pkg}")
    v = out.strip().split()
    return int(v[0]) if rc == 0 and v and v[0].isdigit() else None


def driver(cmd, n, serial):
    env = dict(os.environ, CYCLES=str(n))
    if serial:
        env["ANDROID_SERIAL"] = serial
    rc, out, err = run(["sh", "-c", cmd.replace("{{CYCLES}}", str(n))], timeout=T_LONG, env=env)
    text = out + err
    if rc != 0:
        return {"rc": rc, "ok": False, "why": f"驅動回 {rc}:{text.strip()[-200:]}"}
    # 輸出出現任何 INSTRUMENTATION_ 開頭的行就是 UI Automator:要有 INSTRUMENTATION_CODE: -1 且沒有 FAILURES!!!
    # (INSTRUMENTATION_FAILED、INSTRUMENTATION_ABORTED 這類啟動失敗回傳碼照樣可能是 0;代碼審 r1 正確性席)
    if re.search(r"^INSTRUMENTATION_", text, re.M) and ("INSTRUMENTATION_CODE: -1" not in text or "FAILURES!!!" in text):
        return {"rc": rc, "ok": False, "why": "UI Automator 驅動沒有成功結束(沒有 INSTRUMENTATION_CODE: -1、或有 FAILURES!!!、INSTRUMENTATION_FAILED)"}
    return {"rc": rc, "ok": True}


def load_mapping(path):
    """R8 的 mapping.txt:混淆後的類別名 → 原名。"""
    m = {}
    if not path:
        return m
    if not os.path.isfile(os.path.join(root, path)):
        die(f"stability.mapping 指的檔不存在:{path}")
    for line in open(os.path.join(root, path), encoding="utf-8", errors="replace"):
        g = re.match(r"(\S+) -> (\S+):$", line.rstrip())
        if g:
            m[g.group(2)] = g.group(1)
    return m


def heap_counts(trace, pkg, mapping):
    q = open(os.path.join(here, "android-heap-classes.sql"), encoding="utf-8").read().replace("__PROCESS__", pkg)
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(q)
    try:
        rc, out, err = run([TP, trace, "-q", f.name], timeout=T_LONG)
    finally:
        os.unlink(f.name)
    if rc != 0:
        return None, f"trace_processor 算不了快照:{err.strip()[-200:] or rc}"
    counts = {}
    for line in out.splitlines()[1:]:
        cells = [c.strip('"') for c in line.split(",")]
        if len(cells) >= 2 and cells[-1].isdigit():
            name = deobfuscate(",".join(cells[:-1]), mapping)
            counts[name] = counts.get(name, 0) + int(cells[-1])
    if not counts:   # 回傳碼 0 但一列都沒有:快照是空的、或套件名對不上快照裡的行程(代碼審 r1 邊界、正確性席)
        return None, "快照查詢一個類別都沒讀到(快照是空的、或套件名對不上)"
    return counts, None


def deobfuscate(name, mapping):
    """類別名照 R8 mapping 還原:陣列後綴照留,類別物件 java.lang.Class<混淆名> 尖括號裡的名字也還原。"""
    m = re.fullmatch(r"java\.lang\.Class<(.*)>", name)
    if m:
        return f"java.lang.Class<{deobfuscate(m.group(1), mapping)}>"
    base, arr = re.fullmatch(r"(.*?)((?:\[\])*)", name).groups()
    return mapping.get(base, base) + arr


def snapshot(pkg, out_dir, tag, mapping):
    path = os.path.join(out_dir, f"heap-{tag}.pftrace")
    rc, _, err = run([JHD, "-n", pkg, "-o", path], timeout=T_LONG)
    if rc != 0 or not os.path.isfile(path):
        return None, f"java_heap_dump 錄不到快照:{err.strip()[-200:] or rc}"
    return heap_counts(path, pkg, mapping)


def cycle_numbers(trace, pkg):
    q = open(os.path.join(here, "android-stability-cycle.sql"), encoding="utf-8").read().replace("__PROCESS__", pkg)
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(q)
    try:
        rc, out, err = run([TP, trace, "-q", f.name], timeout=T_LONG)
    finally:
        os.unlink(f.name)
    rows = [line for line in out.splitlines() if line.startswith('"cycle"')]
    if rc != 0 or not rows:
        return None, f"trace_processor 算不了追蹤檔:{err.strip()[-200:] or rc}"
    v = [c.strip('"') for c in rows[0].split(",")]
    keys = ("peak_anon_swap_kb", "frozen_frames", "max_main_block_ms", "frames")
    return {k: (float(x) if "." in x else int(x)) for k, x in zip(keys, v[1:])}, None


def start_record(pkg, run_dir, max_s, state):
    cfg = open(os.path.join(here, "android-stability-record.pbtxt"), encoding="utf-8").read()
    cfg = cfg.replace("__PROCESS__", pkg).replace("__DURATION_MS__", str(int(max_s * 1000)))
    local = os.path.join(run_dir, "record.pbtxt")
    open(local, "w", encoding="utf-8").write(cfg)
    # 設定放 /data/misc/perfetto-configs/:放 /data/local/tmp 時 perfetto 讀不到(2026-10-24 SM-X710 實機 errno 13)
    remote_cfg, remote_trace = f"/data/misc/perfetto-configs/lumos-stability-{run_id}.pbtxt", f"/data/misc/perfetto-traces/lumos-stability-{run_id}.pftrace"
    state["rec"] = (None, remote_cfg, remote_trace)   # 推設定之前先登記:錄製開起來、pid 還沒回來時被中斷,cleanup 照樣收得到(代碼審 r3 正確性席、資源席)
    adb("push", local, remote_cfg)
    rc, out, err = shell(f"perfetto --background --txt -c {remote_cfg} -o {remote_trace}")
    pid = out.strip().split()[-1] if out.strip() else ""
    if rc == 0 and pid.isdigit():
        return pid, remote_cfg, remote_trace
    shell(f"pkill -TERM -f {remote_trace}")   # 回傳碼不是 0 也可能已經開起來了(adb 傳輸失敗、逾時;代碼審 r4 資源席)
    shell(f"rm -f {remote_cfg} {remote_trace}")   # 開不起來也要收掉推上去的設定檔
    return None, f"perfetto 開不了錄製:{(err or out).strip()[-200:]}", None


def perfetto_alive(pid, tries=3):
    """用 ps 看背景錄製還在不在:裝置不准 shell 對 perfetto 送 kill -0(回 Permission denied),kill -TERM 照樣有效(2026-10-24 SM-X710 實機)。
    回 True / False / None:不在裝置上 grep,ps 失敗與「沒找到」才分得開(代碼審 r3 正確性席);ps 偶發失敗就再問,連問 tries 次都失敗才回 None(不知道)。"""
    for i in range(tries):
        rc, out, _ = shell("ps -A -o PID,NAME")
        if rc == 0:
            return any(line.split()[:1] == [pid] for line in out.splitlines())
        if i + 1 < tries:
            time.sleep(1)
    return None


def stop_record(rec, run_dir):
    pid, remote_cfg, remote_trace = rec
    try:
        alive = perfetto_alive(pid)   # None(連問三次都不知道)照樣送 TERM、等它停,但追蹤檔不採用(見下)
        shell(f"kill -TERM {pid}")
        deadline = time.time() + STOP_WAIT
        while perfetto_alive(pid) is not False and time.time() < deadline:
            time.sleep(1)
        if perfetto_alive(pid) is not False:   # 等完還在(或一直問不到):補 KILL,這份追蹤檔沒寫完,不能拿來算
            shell(f"kill -KILL {pid}")
            return None, f"錄製收到 TERM 等了 {STOP_WAIT:g} 秒還停不下來(或問不到它還在不在),已補 KILL"
        if alive is None:   # 判不出錄製是不是一直跑到量測結束:可能是到上限就停了的半份,寧可不採用(代碼審 r4 正確性席)
            return None, "問不到錄製在量測結束時還在不在(ps 連問三次都失敗),追蹤檔可能只錄到一半,不採用"
        if alive is False:
            return None, "錄製在 N 輪跑完前就到了上限(stability.max_record_s)"
        local = os.path.join(run_dir, "cycle.pftrace")
        rc = adb("pull", remote_trace, local)[0]
        return (local, None) if rc == 0 and os.path.isfile(local) else (None, "拉不回追蹤檔")
    finally:
        shell(f"rm -f {remote_cfg} {remote_trace}")


def declared_classes():
    """門檻檔裡 check 是 instances 的那幾個類別:即使前後沒增減也要存進結果檔。"""
    try:
        raw = json.load(open(os.path.join(root, ".lumos", "macrobench-thresholds.json"), encoding="utf-8-sig"))
        return {t["class"] for t in raw.get("thresholds", []) if isinstance(t, dict) and t.get("check") == "instances" and isinstance(t.get("class"), str)}
    except (OSError, ValueError, AttributeError):
        return set()


def abort_record(rec):
    """中途出例外或被中斷時收掉裝置上的錄製與暫存檔。rec 是 (pid, 設定檔, 追蹤檔);pid 還沒回來時照追蹤檔名找錄製停掉。
    回 True(裝置有回應)/ False(停或刪有一個沒成,錄製與暫存可能還在)。"""
    if not rec or rec[2] is None:   # (None, 原因, None):沒開成,start_record 已經收過了
        return True
    a = shell(f"kill -TERM {rec[0]}" if rec[0] else f"pkill -TERM -f {rec[2]}")[0]
    b = shell(f"rm -f {rec[1]} {rec[2]}")[0]
    return a is not None and b == 0   # kill 找不到程序也算有回應(回傳碼非 0 但不是逾時)


def src(value, why, status_if_none="failed"):
    return {"status": "ok", **value} if why is None else {"status": status_if_none, "reason": why}


def preflight(st):
    """動裝置之前的檢查:run-id、工具、產物目錄有沒有被 git 忽略。回 (是否錄快照, run 目錄)。"""
    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id) or set(run_id) <= {"."}:
        die(f"run-id 只收英數字、點、底線與連字號,也不能只有點(它會用在裝置上的路徑):{run_id!r}")
    for tool in (ADB, TP):
        if not shutil.which(tool):
            die(f"找不到 {tool};用環境變數 ADB=、TP= 指定")
    test_data = bool((st.get("test_data") or {}).get("value"))
    if test_data and not shutil.which(JHD):
        die(f"宣告了測試資料要錄快照,但找不到 {JHD};用 JAVA_HEAP_DUMP= 指定")
    run_dir = os.path.join(root, ".lumos", "artifacts", "android", run_id)
    if os.path.exists(os.path.join(run_dir, "stability.json")):   # 沿用舊目錄的話,這次中斷時舊結果檔會被當成這次的(代碼審 r2 正確性席)
        die(f"run-id {run_id} 已經有結果檔了;換一個 run-id(不給就用日期時間)")
    g_rc, _, g_err = run(["git", "-C", root, "rev-parse", "--is-inside-work-tree"])
    if g_rc not in (0, None) and "not a git repository" not in g_err:   # git 自己壞了(safe.directory 等)不能當成不是 repo(代碼審 r4 資安席)
        die(f"git 判不了這裡是不是 repo:{g_err.strip()[-200:]};先修好 git 再跑(產物不准進版控,判不了就不跑)")
    in_git = g_rc == 0
    # 快照、日誌與結果檔不准進版控(代碼審 r1 資安席);每種會寫出的檔名都問一次,.gitignore 只寫 *.json 時快照照樣會進版控(r2 資安席)
    loose = [n for n in ARTIFACTS if in_git and run(["git", "-C", root, "check-ignore", "-q", os.path.join(run_dir, n)])[0] != 0]
    if loose:
        die(f".lumos/artifacts/ 底下這些檔沒被 git 忽略:{'、'.join(loose)};先在 .gitignore 加一行 .lumos/artifacts/ 再跑(快照與日誌可能含使用者資料)")
    return test_data, run_dir


def device_info(st):
    res = {"scenario": st["scenario"], "warmup": st["warmup"], "cycles": st["cycles"], "category": st.get("category", "app")}
    res["device_model"] = shell("getprop ro.product.model")[1].strip()
    sdk = shell("getprop ro.build.version.sdk")[1].strip()
    res["android_sdk"] = int(sdk) if sdk.isdigit() else None
    m = re.search(r"MemTotal:\s+(\d+)\s*kB", shell("cat /proc/meminfo")[1])
    res["total_mem_mb"] = int(m.group(1)) // 1024 if m else -1
    return res


def start_logcat(st, pid, t0, run_dir, state):
    """只在宣告了 strictmode 時開日誌串流,只收這個 pid、量測開始之後的;串流與暫存檔路徑登記在 state。回 (Popen 或 None, 暫存檔路徑)。"""
    if not st.get("strictmode") or not pid:
        return None, None
    raw = state["raw"] = os.path.join(run_dir, "logcat.raw")   # 開檔之前先登記,開到一半被中斷也刪得到
    with open(raw, "w", encoding="utf-8") as logf:
        lc = state["lc"] = subprocess.Popen([ADB, "logcat", f"--pid={pid}", "-T", t0, "-v", "brief"], stdout=logf, stderr=subprocess.STDOUT)
    return lc, raw


def stop_logcat(lc):
    """收掉日誌串流;回它是不是早就自己斷了。"""
    if lc is None:
        return False
    time.sleep(SETTLE)   # 讓日誌串流跟上量測結束前的最後幾行;等完再看它是不是早就自己斷了
    died = lc.poll() is not None
    lc.terminate()
    try:
        lc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        lc.kill()
    return died


def drop_raw(raw):
    """刪掉原始日誌串流(日誌常含帳號、權杖、網址):每條路都要刪,包括串流斷了與被中斷(代碼審 r2 五席)。"""
    if raw and os.path.lexists(raw):
        os.unlink(raw)


def strictmode_result(st, started, died, raw, run_dir):
    """只留違規那幾行落地,原始串流不管成不成都刪掉。"""
    try:
        if not st.get("strictmode"):
            return {"status": "unsupported", "reason": "設定沒宣告 strictmode"}
        if not started or died:
            return {"status": "failed", "reason": "日誌串流沒開成或中途斷了"}
        lines = [x for x in open(raw, encoding="utf-8", errors="replace") if "StrictMode policy violation" in x]
    finally:
        drop_raw(raw)
    with open(os.path.join(run_dir, "logcat.txt"), "w", encoding="utf-8") as f:
        f.writelines(lines)
    return {"status": "ok", "violations": [
        {"type": (re.search(r"strictmode\.(\w+Violation)", x) or re.search(r"(\w+Violation)", x) or [None, "unknown"])[1]} for x in lines]}


def heap_result(test_data, before, after, why, mapping):
    if before is None or after is None:
        return src({}, why, "unsupported" if not test_data else "failed")
    declared = declared_classes()
    declared |= {f"java.lang.Class<{c}>" for c in declared}   # 宣告類別沒有實例時,靠它的類別物件證明載入過
    keep = {c for c in set(before) | set(after) if before.get(c) != after.get(c) or c in declared}
    return {"status": "ok", "before": {c: before[c] for c in keep if c in before}, "after": {c: after[c] for c in keep if c in after},
            "classes_seen": {"before": len(before), "after": len(after)}, "class_names": "mapping" if mapping else "raw"}


def measure(st, test_data, run_dir, mapping, state):
    """裝置上的整段流程;state 收著被中斷時要收掉的錄製與日誌串流。"""
    pkg, n, w, serial = st["package"], st["cycles"], st["warmup"], st.get("adb_serial")
    res = device_info(st)
    shell(f"am force-stop {pkg}")   # 從乾淨的行程開始:不停的話上一次留下的物件會算進這一次(2026-10-24 實驗室連跑兩次時抓到)
    ex_status, ex_before = read_exits(pkg)   # 停完才讀,停 App 自己產生的那筆結束紀錄不會被當成測試期間的
    shell(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
    time.sleep(SETTLE)
    pids = [pidof(pkg)]
    d_warm = driver(st["driver"], w, serial)
    pids.append(pidof(pkg))
    u_before, u_why = unreachable(pids[-1]) if pids[-1] else (None, "App 沒在跑")   # 先掃再錄快照:錄快照時的配置不算進掃描
    nh_before = native_heap_kb(pkg)
    h_before, h_why = snapshot(pkg, run_dir, "before", mapping) if test_data else (None, "沒宣告測試資料(stability.test_data),不錄快照")
    t0 = shell("date '+%m-%d %H:%M:%S.000'")[1].strip()
    state["rec"] = start_record(pkg, run_dir, st.get("max_record_s", 600), state)
    _, raw = start_logcat(st, pids[-1], t0, run_dir, state)
    d_cyc = driver(st["driver"], n, serial)
    # 停完才從 state 拿掉:等日誌跟上、等錄製停下的那幾秒被中斷時,cleanup 還找得到它們(代碼審 r2 正確性席、資源席)
    died = stop_logcat(state.get("lc"))
    state.pop("lc", None)
    rec = state["rec"]
    trace, t_why = stop_record(rec, run_dir) if rec[0] else (None, rec[1])
    del state["rec"]
    pids.append(pidof(pkg))
    u_after, u_why2 = unreachable(pids[-1]) if pids[-1] else (None, "App 沒在跑")
    nh_after = native_heap_kb(pkg)
    h_after, h_why2 = snapshot(pkg, run_dir, "after", mapping) if test_data else (None, h_why)
    ex_status2, ex_after = read_exits(pkg)
    drv_ok = d_warm["ok"] and d_cyc["ok"]
    res["driver"] = {"status": "ok" if drv_ok else "failed", "warmup": d_warm, "cycles": d_cyc,
                     **({} if drv_ok else {"reason": d_warm.get("why") or d_cyc.get("why")})}
    res["pids"] = src({"values": pids}, None if all(pids) else "有一次讀不到 pid(App 不在了)")
    res["unreachable"] = src({"before": u_before, "after": u_after}, u_why or u_why2)
    res["native_heap_kb"] = src({"before": nh_before, "after": nh_after}, None if nh_before is not None and nh_after is not None else "讀不到 Native Heap")
    res["heap"] = heap_result(test_data, h_before, h_after, h_why or h_why2, mapping)
    nums, c_why = cycle_numbers(trace, pkg) if trace else (None, t_why)
    res["cycle_trace"] = src(nums or {}, c_why)
    if ex_status == "ok" and ex_status2 == "ok":
        res["exits"] = {"status": "ok", "new": exit_diff(ex_before, ex_after)}
    else:
        res["exits"] = {"status": "failed", "reason": ex_before if ex_status != "ok" else ex_after}
    res["strictmode"] = strictmode_result(st, raw is not None, died, raw, run_dir)
    return res


def cleanup(state):
    """被 SIGTERM、SIGHUP、Ctrl-C 或例外中斷時:收掉驅動整組子程序、日誌串流,停掉裝置上的錄製並刪暫存。
    先擋掉後面再來的中斷、先刪原始日誌(本機、一下就好),再做可能卡 120 秒的裝置呼叫:連按兩次 Ctrl-C 也不留日誌(代碼審 r3 正確性席、資源席)。"""
    stop_listening()
    drop_raw(state.get("raw"))
    print("收集被中斷,收尾中(停裝置錄製、刪暫存;裝置沒回應時最久約 4 分鐘,這段時間按 Ctrl-C 沒有用)…", file=sys.stderr)
    for p in list(GROUPS):
        kill_group(p)
    lc = state.get("lc")
    if lc is not None:
        lc.kill()
    rec = state.get("rec")
    return abort_record(rec) if rec else True


def main():
    for s in INTERRUPTS:   # SIGHUP:關掉終端機分頁、ssh 斷線;子程序各自成組收不到,要靠這裡收(代碼審 r3 資源席、資安席)
        signal.signal(s, on_term)
    signal.signal(signal.SIGINT, on_int)
    st = load_config()
    if st.get("adb_serial"):
        os.environ["ANDROID_SERIAL"] = st["adb_serial"]
    test_data, run_dir = preflight(st)
    os.makedirs(run_dir, exist_ok=True)
    prune_old_snapshots()
    mapping = load_mapping(st.get("mapping"))
    state = {}
    try:
        res = measure(st, test_data, run_dir, mapping, state)
    except (Terminated, KeyboardInterrupt):
        device_ok = cleanup(state)
        dev = ("裝置上的錄製已停、暫存已刪" if device_ok else
               "裝置沒回應,錄製與暫存可能還在(接上後 adb shell ls /data/misc/perfetto-traces/ 看過再刪)")   # 照實寫(代碼審 r4 資安席)
        print(f"擋下:收集被中斷,沒寫結果檔;{dev};原始日誌已刪,{run_dir} 裡已經錄到的快照與追蹤檔留著(可能含使用者資料,用完自己刪)",
              file=sys.stderr)
        sys.exit(2)
    except BaseException:
        cleanup(state)
        raise
    out = os.path.join(run_dir, "stability.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(out)

main()
PY
