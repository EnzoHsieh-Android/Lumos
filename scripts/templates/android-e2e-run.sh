#!/bin/sh
# SPDX-FileCopyrightText: 2026 Enzo Hsieh
# SPDX-License-Identifier: MIT
# lumos Android 端到端驗收:在主機端依序建 APK、裝上、跑 Maestro flow、截圖比對、記憶體與穩定性、效能,
# 每一步寫進 .lumos/artifacts/android/<run-id>/steps.json,最後交給 lumos android-e2e judge 判與寫查證紀錄。
# 不判過不過(判定在 lumos)。單一來源在工具鏈 scripts/templates/,消費專案照抄;規則單源 Projects/Android端到端驗收_計劃。
# 用法:在專案根目錄跑 sh scripts/templates/android-e2e-run.sh [--preflight] [挑法] [run-id]
#   --preflight:只做開跑前檢查(工作目錄、裝置、工具、產物目錄有沒有被忽略、裝置鎖),不碰 App
#   挑法(開發中按功能跑:不要求工作目錄乾淨、不寫整套的紀錄;開跑時與跑完都乾淨、HEAD 沒換時,
#   按情境的結果寫進這一版紀錄的 feature_runs。不給就整套跑、寫整套的紀錄):
#     --changed               看這次改到的檔,挑 e2e.features 對得到的功能
#     --feature <功能>[,…]    這些功能的全部使用情境
#     --case <功能.情境>[,…]   只跑這些使用情境
#     --no-perf / --no-memory  這次不跑效能或記憶體與穩定性(只能配上面三種挑法;整套跑一定全部跑)
#   每次跑完都記進本機總表 .lumos/artifacts/android/history.jsonl(lumos android-e2e history 看)
# 外部工具:ADB(預設 adb)、MAESTRO(預設 maestro);開了記憶體與穩定性時另要 TP(預設 trace_processor),
#   宣告了測試資料時再要 JAVA_HEAP_DUMP(預設 java_heap_dump),跟收集腳本同兩個環境變數;設定在 .lumos/macrobench.json 的 e2e 段
#   (記憶體的收集腳本預設是同目錄的 android-stability-collect.sh,測試用 LUMOS_E2E_COLLECT= 換成假的;換了就只記總表、不寫查證紀錄)
# 測試縮短與替換用:LUMOS_E2E_LONG_TIMEOUT(建置、flow、收集與效能的上限,預設 3600 秒)、
#   LUMOS_E2E_LOCK_DIR(裝置鎖的目錄,預設 ~/.cache/lumos/android-e2e-lock)、
#   LUMOS_E2E_STOP_GRACE(中斷時先送 TERM、等子程序自己收尾的秒數,寬限結束後一律對整組補 KILL,預設 60 秒;收集腳本在裝置沒回應時收尾可能要好幾分鐘)
# 回傳碼:跟 lumos android-e2e judge 一樣(0 寫了紀錄且通過、1 寫了紀錄但沒通過、2 沒寫);開跑前檢查沒過回 2 並印「擋下:」
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null || { echo "擋下:驗收腳本要 python3 3.11 以上(用了 -P)" >&2; exit 2; }
# -P 與拿掉 PYTHONPATH 的理由同收集腳本 android-stability-collect.sh
exec env -u PYTHONPATH PYTHONUTF8=1 PYTHONIOENCODING=utf-8 python3 -P - "$HERE" "$(pwd)" "$@" <<'PY'
import glob, hashlib, json, os, re, shutil, signal, subprocess, sys, time
here, root = sys.argv[1], sys.argv[2]
argv = sys.argv[3:]
PREFLIGHT = "--preflight" in argv
PICK, FLAGS, rest, BAD, _i = {"--feature": [], "--case": []}, set(), [], [], 0
while _i < len(argv):   # --feature a,b / --feature=a,b;值缺了記成空字串,交給 lumos select 擋
    a = argv[_i]
    key = next((k for k in PICK if a == k or a.startswith(k + "=")), None)
    if key:
        if a == key:
            _i += 1
            a = argv[_i] if _i < len(argv) else ""
        else:
            a = a.split("=", 1)[1]
        PICK[key] += [b.strip() for b in a.split(",")] or [""]
    elif a in ("--changed", "--no-perf", "--no-memory"):
        FLAGS.add(a)
    elif a.startswith("-") and a != "--preflight":   # 打錯的旗標不准當成 run-id(會不帶挑法整套跑)
        BAD.append(a)
    elif a != "--preflight":
        rest.append(a)
    _i += 1
SELECTIVE = bool(PICK["--feature"] or PICK["--case"] or "--changed" in FLAGS)
COLLECT = os.environ.get("LUMOS_E2E_COLLECT") or os.path.join(here, "android-stability-collect.sh")
SEL = None   # 按功能跑時,lumos android-e2e select 挑出來的東西(flows、visual、macrobench、stability)
run_id = rest[0] if rest else time.strftime("e2e-%Y%m%d-%H%M%S")
ADB, MAESTRO = os.environ.get("ADB", "adb"), os.environ.get("MAESTRO", "maestro")
TP, JHD = os.environ.get("TP", "trace_processor"), os.environ.get("JAVA_HEAP_DUMP", "java_heap_dump")
LUMOS = os.path.join(here, "..", "lumos")
T_SHORT = 120
T_LONG = float(os.environ.get("LUMOS_E2E_LONG_TIMEOUT", "3600"))
GRACE = float(os.environ.get("LUMOS_E2E_STOP_GRACE", "60"))
LOCK_DIR = os.environ.get("LUMOS_E2E_LOCK_DIR") or os.path.join(os.path.expanduser("~"), ".cache", "lumos", "android-e2e-lock")
GROUPS = []
INTERRUPTS = (signal.SIGTERM, signal.SIGHUP, signal.SIGQUIT)


def say(msg):
    """印到錯誤輸出;終端被關(EIO)或管線斷了(EPIPE)時不讓例外打斷收尾。"""
    try:
        print(msg, file=sys.stderr, flush=True)
    except (OSError, ValueError):
        try:   # 錯誤輸出已經斷了:換成 /dev/null,結束時清緩衝區才不會失敗、回傳碼變 120
            sys.stderr = open(os.devnull, "w")
        except OSError:
            pass


def die(msg):
    say(f"擋下:{msg}")
    sys.exit(2)


class Terminated(Exception):
    """收到 SIGTERM、SIGHUP 或 SIGQUIT:轉成例外,讓收尾寫下「中斷」再交給 judge(同收集腳本)。"""


def stop_listening():
    for s in INTERRUPTS + (signal.SIGINT,):
        signal.signal(s, signal.SIG_IGN)


def on_term(signum, frame):
    stop_listening()
    raise Terminated()


def on_int(signum, frame):
    stop_listening()
    raise KeyboardInterrupt()


def signal_group(p, sig):
    try:
        os.killpg(p.pid, sig)
    except (OSError, AttributeError):
        try:
            p.send_signal(sig)
        except OSError:
            pass


def kill_group(p):
    """整組收掉:先送 TERM、等最多 GRACE 秒讓它自己收尾(收集腳本靠 TERM 停裝置上的錄製、toolkit 靠 trap 清鎖與展示模式),
    寬限結束(或領頭先退了)一律對整組補 KILL,同組裡不理 TERM 的成員也收掉。收集腳本的子程序各自成組,
    它們得靠收集腳本自己收,所以不能一開始就 KILL。"""
    if p.poll() is None:
        signal_group(p, signal.SIGTERM)
        try:
            p.wait(timeout=GRACE)
        except subprocess.TimeoutExpired:
            pass
        except BaseException:   # 寬限中又被中斷(例如逾時路徑上還沒擋掉訊號):先補 KILL 再往上丟,不留孤兒
            signal_group(p, signal.SIGKILL)
            raise
    signal_group(p, signal.SIGKILL)   # 領頭已經退了也補一次:同組裡不理 TERM 的成員要靠這一下收掉


def run(cmd, timeout=T_SHORT, out=None, err=None, **kw):
    """回 (回傳碼, 標準輸出, 標準錯誤);out/err 給了檔案路徑就寫進檔(回傳的字串是空的)。
    逾時或執行不了回 (None, '', 原因)。每個子程序自成一個程序群組,逾時或被中斷時整組殺掉。"""
    fo = open(out, "w", encoding="utf-8") if out else subprocess.PIPE
    fe = open(err, "w", encoding="utf-8") if err else subprocess.PIPE
    try:
        try:
            p = subprocess.Popen(cmd, stdout=fo, stderr=fe, text=True, errors="replace", start_new_session=True, **kw)
        except OSError as e:
            return None, "", f"執行不了({e.strerror})"
        GROUPS.append(p)
        try:
            so, se = p.communicate(timeout=timeout)
            return p.returncode, so or "", se or ""
        except subprocess.TimeoutExpired:
            kill_group(p)
            try:
                p.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            return None, "", f"逾時({timeout} 秒)"
        except BaseException:
            kill_group(p)
            raise
        finally:
            GROUPS.remove(p)
    finally:
        for f in (fo, fe):
            if f is not subprocess.PIPE:
                f.close()


def adb(serial, *args, timeout=T_SHORT):
    return run([ADB, "-s", serial, *args], timeout=timeout)


def lumos(*args, **kw):
    return run([sys.executable, LUMOS, *args], **kw)


def load_config():
    rc, out, err = lumos("macrobench", "--repo", root, "--check-config")
    if rc != 0:
        die((err or out).strip().removeprefix("擋下:") or "lumos macrobench --check-config 沒過")
    try:
        cfg = json.load(open(os.path.join(root, ".lumos", "macrobench.json"), encoding="utf-8-sig"))
    except Exception as e:
        die(f".lumos/macrobench.json 讀不了:{e}")
    if not isinstance(cfg.get("e2e"), dict):
        die(".lumos/macrobench.json 沒有 e2e 段;照 lumos-android-evidence skill 的 E2E 驗收一節寫好再跑")
    return cfg


def pick_serial(e2e):
    s = e2e.get("adb_serial") or os.environ.get("ANDROID_SERIAL")
    if not s:
        rc, out, err = run([ADB, "devices"])
        devs = [ln.split("\t")[0] for ln in out.splitlines()[1:] if ln.strip().endswith("\tdevice")]
        if rc != 0 or len(devs) != 1:
            die(f"判不出要用哪台裝置(adb devices 看到 {len(devs)} 台可用);在 e2e 段寫 adb_serial 或設 ANDROID_SERIAL")
        s = devs[0]
    if not re.fullmatch(r"[A-Za-z0-9._:-]+", s) or set(s) <= {"."}:   # 序號會拼進鎖的路徑:不收斜線這類字元
        die(f"裝置序號只收英數字、點、冒號、底線與連字號:{s!r}")
    return s


def pid_alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def lock_path(serial):
    return os.path.join(LOCK_DIR, re.sub(r"[^A-Za-z0-9._-]", "_", serial))


def lock_holder(serial):
    """鎖裡記的程序編號還活著就回它,否則回 None(鎖不在、或記的程序已經不在了)。"""
    try:
        pid = int(open(lock_path(serial), encoding="utf-8").read().strip() or "0")
    except (OSError, ValueError):
        return None
    return pid if pid > 0 and pid != os.getpid() and pid_alive(pid) else None


def take_lock(serial):
    """裝置鎖放在工作目錄外,兩個工作樹對同一台裝置也擋得住;寫程序編號,記的程序已經不在就清掉接手。"""
    os.makedirs(LOCK_DIR, exist_ok=True)
    p = lock_path(serial)
    for _ in range(2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            holder = lock_holder(serial)
            if holder:
                die(f"裝置 {serial} 有另一次驗收在跑(程序 {holder});等它跑完再開")
            say(f"清掉上次留下的裝置鎖({p}:記的程序已經不在了)")
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return p
    die(f"裝置鎖 {p} 搶不到")


def drop_lock(p):
    try:
        if open(p, encoding="utf-8").read().strip() == str(os.getpid()):
            os.unlink(p)
    except OSError:
        pass


def clear_toolkit_lock(serial):
    """toolkit 的 .maestro/.lock-<序號>:確認沒有 visual-check.sh 程序在跑才清(它只在正常結束時自己刪)。"""
    lk = os.path.join(root, ".maestro", f".lock-{serial}")
    if os.path.islink(lk):
        die(f"{lk} 是符號連結,不是 toolkit 建的鎖;看過再手動處理")
    if not os.path.isdir(lk):
        return
    rc, out, _ = run(["pgrep", "-f", "visual-check.sh"])
    if rc == 0 and out.strip():
        die(f"有 visual-check.sh 正在跑({lk} 在用);等它跑完再開")
    shutil.rmtree(lk)
    say(f"清掉上次留下的 toolkit 鎖 {lk}")


def gradle_modules():
    """settings.gradle(.kts) 裡 include 的模組 → 路徑(:a:b → a/b)。"""
    mods = []
    for name in ("settings.gradle.kts", "settings.gradle"):
        try:
            text = open(os.path.join(root, name), encoding="utf-8").read()
        except OSError:
            continue
        for line in text.splitlines():
            if re.match(r"\s*include\b", line):
                mods += [m.strip(":").replace(":", "/") for m in re.findall(r"[\"'](:[^\"']+)[\"']", line)]
    return mods


def select():
    """按功能跑:叫 lumos android-e2e select 挑(--changed 的分岔點、對照表檢查都在那邊),挑不到就擋。"""
    args = ["android-e2e", "select", "--repo", root]
    for k, vs in PICK.items():
        for v in vs:
            args += [k, v]
    args += sorted(FLAGS)
    rc, out, err = lumos(*args)
    if rc != 0:
        die((err or out).strip().removeprefix("擋下:") or "lumos android-e2e select 沒挑到")
    try:
        return json.loads(out)
    except ValueError:
        die(f"lumos android-e2e select 的輸出讀不懂:{out[:200]!r}")


def tests_to_run(cfg):
    """這次要跑的效能測試方法;macrobench_cmd 沒帶 {{TEST}} 時是 [None](整條指令跑一次)。"""
    e2e = cfg["e2e"]
    if not e2e.get("macrobench"):
        return []
    if SEL is not None:
        return SEL["macrobench"]
    if "{{TEST}}" not in e2e["macrobench_cmd"]:
        return [None]
    feats = e2e.get("features") or {}
    return list(dict.fromkeys(t for f in feats.values() for c in f["cases"].values() for t in c.get("macrobench", [])))


def stab_to_run(cfg):
    """這次要跑的記憶體情境:整套跑是 [None](stability 段本身)加上 stability_scenarios 每個情境;按功能跑是挑到的情境名。"""
    if not cfg["e2e"].get("stability"):
        return []
    return SEL["stability"] if SEL is not None else [None, *(cfg.get("stability_scenarios") or {})]


def flows_to_run(cfg):
    return SEL["flows"] if SEL is not None else cfg["e2e"]["flows"]


def screens_to_run(cfg):
    return SEL["visual"] if SEL is not None else (cfg["e2e"].get("visual") or [])


def preflight(cfg, serial, run_dir):
    """動 App 之前的檢查:run-id、工具、工作目錄、產物目錄、裝置、截圖素材、裝置鎖。"""
    e2e = cfg["e2e"]
    if run_id.lower() == "history.jsonl":   # 本機總表 .lumos/artifacts/android/history.jsonl 跟 run 目錄在同一層(macOS 預設不分大小寫)
        die("run-id 不能叫 history.jsonl(那是本機檢測總表的檔名,不分大小寫)")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id) or set(run_id) <= {"."}:
        die(f"run-id 只收英數字、點、底線與連字號,也不能只有點:{run_id!r}")
    for tool in (ADB, MAESTRO):
        if not shutil.which(tool):
            die(f"找不到 {tool};用環境變數 ADB=、MAESTRO= 指定")
    if stab_to_run(cfg):   # 收集腳本自己也查,但要等建置、安裝、UI、截圖都跑完才輪到它,缺工具就白跑一趟
        st = cfg.get("stability") or {}
        # 下一行跟收集腳本判「要不要錄快照」那一行逐字相同(測試抽出兩邊那一行比相等)
        test_data = bool((st.get("test_data") or {}).get("value"))
        need = [("trace_processor", "TP", TP)]
        if test_data:
            need.append(("java_heap_dump", "JAVA_HEAP_DUMP", JHD))
        for name, var, tool in need:
            if not shutil.which(tool):
                die(f"找不到 {name}(記憶體與穩定性要用,找的是 {tool});用環境變數 {var}= 指定")
    if not SELECTIVE:   # 按功能跑不寫整套的紀錄,開發中本來就有沒提交的改動,不要求工作目錄乾淨
        rc, out, err = lumos("android-e2e", "judge", "--repo", root, "--precheck")
        if rc != 0:
            die((err or out).strip().removeprefix("擋下:") or "工作目錄不能開跑")
    taken = [d for d in [run_dir] + [f"{run_dir}.{s}" for s in stab_to_run(cfg) if s] if os.path.exists(d)]
    if taken:   # 包括「另一次的 run-id.情境」記憶體目錄:撞到要等建置、UI 跑完才在收集腳本被擋
        die(f"run-id {run_id} 已經跑過或被佔用了({'、'.join(os.path.relpath(d, root) for d in taken)} 已存在);換一個 run-id(不給就用日期時間)")
    for rel in ("steps.json", "ui/x.xml", "visual/x/x.png", "logs/x.out", "macrobench/x.json"):
        if run(["git", "-C", root, "check-ignore", "-q", os.path.join(run_dir, rel)])[0] != 0:
            die(".lumos/artifacts/ 沒被 git 忽略;先在 .gitignore 加一行 .lumos/artifacts/ 再跑(截圖與報告可能含使用者資料)")
    if adb(serial, "get-state")[1].strip() != "device":
        die(f"裝置 {serial} 沒連上(adb get-state 不是 device)")
    win = adb(serial, "shell", "dumpsys window")[1]
    pw = adb(serial, "shell", "dumpsys power")[1]
    if "isKeyguardShowing=true" in win or "mShowingLockscreen=true" in win or ("mWakefulness=" in pw and "mWakefulness=Awake" not in pw):
        die(f"裝置 {serial} 鎖著或螢幕沒亮;解鎖、讓螢幕亮著再跑")
    for v in screens_to_run(cfg):
        for f in (".maestro/visual-check.sh", f".maestro/{v}.yaml", f".maestro/baseline/{v}.png"):
            if not os.path.exists(os.path.join(root, f)):
                die(f"截圖要用的 {f} 不在;照 toolkit 的 README 裝好、錄好基準圖再跑")
    apps = [d.strip().rstrip("/") for d in e2e["app_dirs"]]
    loose = [m for m in gradle_modules() if not any(m == d or m.startswith(d + "/") for d in apps)]
    if loose:
        say(f"提醒:settings.gradle 列了這些模組,卻不在 app_dirs:{'、'.join(loose)}(改了它們不會要求重驗)")
    holder = lock_holder(serial)
    if holder:
        die(f"裝置 {serial} 有另一次驗收在跑(程序 {holder});等它跑完再開")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def installed_sha(serial, pkg):
    rc, out, _ = adb(serial, "shell", f"pm path {pkg}")
    paths = [ln.split(":", 1)[1].strip() for ln in out.splitlines() if ln.startswith("package:") and ln.strip().endswith("base.apk")]
    if rc != 0 or not paths:
        return None
    rc, out, _ = adb(serial, "shell", f"sha256sum {paths[0]}")
    tok = out.split()
    return tok[0] if rc == 0 and tok and re.fullmatch(r"[0-9a-f]{64}", tok[0]) else None


def now():
    import datetime
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


class Steps:
    """steps.json:每一步記回傳碼、時間、輸出存在哪、報告路徑;每記一步就整份原子寫回(被殺也留得下已經跑完的)。"""

    def __init__(self, run_dir, head, serial):
        self.run_dir = run_dir
        self.data = {"schema": 1, "run_id": run_id, "start_head": head, "started": now(), "ended": None,
                     "interrupted": False, "device": {"serial": serial}, "apk": {}, "steps": []}
        if SEL is not None:
            self.data["selection"] = SEL   # judge 看到這欄就不寫整套的紀錄(只跑了一部分)
        # 有沒有沒提交的改動:跟開跑前檢查同一套規則(簿記檔不算),所以問 lumos,不自己列
        self.data["dirty"] = lumos("android-e2e", "judge", "--repo", root, "--precheck")[0] != 0
        os.makedirs(os.path.join(run_dir, "logs"), exist_ok=True)
        self.save()

    def save(self):
        p = os.path.join(self.run_dir, "steps.json")
        tmp = p + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, p)

    def step(self, block, cmd, name=None, attempt=1, report=None, timeout=T_LONG, env=None):
        tag = "-".join(x for x in (block, name, str(attempt)) if x)
        out, err = (os.path.join(self.run_dir, "logs", f"{tag}.{k}") for k in ("out", "err"))
        rec = {"block": block, "name": name, "attempt": attempt, "started": now(), "stdout": out, "stderr": err, "report": report}
        rc, _, why = run(cmd, timeout=timeout, out=out, err=err, cwd=root, env=env)
        if rc is None:
            with open(err, "a", encoding="utf-8") as f:
                f.write(f"\n{why}\n")
        rec.update(rc=rc, ended=now())
        self.data["steps"].append(rec)
        self.save()
        return rc


def collect_results(cfg, since, dest):
    """效能:把這次開始後才寫出的 *-benchmarkData.json 複製進 run 目錄(保留相對路徑,不同模組同名不互蓋)。"""
    n = 0
    for d in cfg.get("results_dirs") or []:
        base = os.path.join(root, d)
        for f in glob.glob(os.path.join(base, "**", "*-benchmarkData.json"), recursive=True):
            if os.path.getmtime(f) >= since:
                to = os.path.join(dest, os.path.relpath(f, root))
                os.makedirs(os.path.dirname(to), exist_ok=True)
                shutil.copy2(f, to)
                n += 1
    return n


def threshold_arg(th):
    """傳給 toolkit 的門檻寫成一般小數(toolkit 只收 ^[0-9]+(\\.[0-9]+)?$,不收科學記號)。"""
    return ("%.6f" % th).rstrip("0").rstrip(".")


def accept(cfg, serial, st):
    e2e, pkg, rd = cfg["e2e"], cfg["e2e"]["package"], st.run_dir
    env = dict(os.environ, ANDROID_SERIAL=serial)
    st.step("build", ["sh", "-c", e2e["build"]])
    apk = os.path.join(root, e2e["apk"])
    st.data["apk"]["built_sha256"] = sha256_file(apk) if os.path.isfile(apk) else None
    st.step("install", [ADB, "-s", serial, "install", "-r", apk], timeout=T_SHORT * 5)
    st.data["apk"]["installed_sha256_before"] = installed_sha(serial, pkg)
    dev = st.data["device"]
    dev["model"] = adb(serial, "shell", "getprop ro.product.model")[1].strip()
    dev["release"] = adb(serial, "shell", "getprop ro.build.version.release")[1].strip()
    st.save()
    os.makedirs(os.path.join(rd, "ui"), exist_ok=True)
    for f in flows_to_run(cfg):
        # flow 的「名」:跟 lumos 的 _e2e_flow_name 同一套規則(相對路徑去副檔名、/ 換 __);兩邊要一起改
        name = re.sub(r"\.[^./]*$", "", f.strip().rstrip("/").removeprefix("./")).replace("/", "__")
        for attempt in (1, 2):
            rep = os.path.join(rd, "ui", f"{name}.try{attempt}.xml")
            rc = st.step("ui", [MAESTRO, "--udid", serial, "test", "--format", "junit", "--output", rep, f],
                         name=name, attempt=attempt, report=rep)
            if rc == 0:
                break
    th = threshold_arg(e2e.get("visual_threshold", 99.5))
    for v in screens_to_run(cfg):
        evid = os.path.join(rd, "visual", v)
        st.step("visual", ["sh", ".maestro/visual-check.sh", v, evid], name=v,
                env=dict(env, THRESHOLD=th, MAESTRO_DEVICE=serial))
    if stab_to_run(cfg) and os.environ.get("LUMOS_E2E_COLLECT"):   # 這次真的要收記憶體、又換了收集腳本(測試用替身):judge 看到就不寫查證紀錄
        st.data["collector_override"] = COLLECT
    for scn in stab_to_run(cfg):   # None=stability 段本身(整套);有名字=stability_scenarios 的情境,收在 <run-id>.<情境> 目錄
        sid = run_id if scn is None else f"{run_id}.{scn}"
        # stability 段本身:拿掉 shell 裡殘留的 LUMOS_STABILITY_SCENARIO,不然收集腳本會改用那個情境、結果卻記成段本身
        senv = {k: v for k, v in env.items() if k != "LUMOS_STABILITY_SCENARIO"} if scn is None else dict(env, LUMOS_STABILITY_SCENARIO=scn)
        if st.step("stability", ["sh", COLLECT, sid], name=scn, env=senv) is None:   # 逾時或跑不起來:裝置多半掉了,剩下的情境不再一個個等滿上限(沒跑到的判成沒判完)
            say(f"記憶體情境 {scn or 'stability 段本身'} 逾時或跑不起來,剩下的情境與效能這次都不跑")
            st.data["device_stuck"] = True
            break
        st.step("stability_judge", [sys.executable, LUMOS, "macrobench", "--repo", root, "--json", "--stability",
                                    os.path.join(root, ".lumos", "artifacts", "android", sid, "stability.json")],
                name=scn, timeout=T_SHORT * 5)
    st.data["apk"]["installed_sha256_after"] = installed_sha(serial, pkg)
    st.save()
    tests = [] if st.data.get("device_stuck") else tests_to_run(cfg)   # 記憶體那段已經卡住:裝置多半掉了,效能不再對著它等一輪上限
    if tests:   # 排最後:Macrobenchmark 的 Gradle 指令常會自己裝上、跑完再移除測試用的 App
        mdir = os.path.join(rd, "macrobench")
        os.makedirs(mdir, exist_ok=True)
        for i, t in enumerate(tests):   # 一個測試方法跑一次;{{TEST}} 換成方法名(名字在 lumos 設定檢查已驗過,這裡再驗一次)
            # 下一行跟 lumos 的 E2E_BENCH_NAME_RE 同一條規則(測試抽出兩邊比相等);不收 $:原樣換進 sh -c,會被當變數展開
            if t is not None and not re.fullmatch(r"[A-Za-z0-9_.][A-Za-z0-9_.#]*", t):
                die(f"效能測試方法名只收英數字、點、底線與 #,開頭不能是 #:{t!r}")
            cmd = e2e["macrobench_cmd"] if t is None else e2e["macrobench_cmd"].replace("{{TEST}}", t)
            t0 = time.time()
            if st.step("macrobench", ["sh", "-c", cmd], name=t, env=env) is None:   # 逾時或跑不起來:剩下的方法不再一個個等滿上限
                say(f"效能測試 {t or '(整條效能指令)'} 逾時或跑不起來,剩下的效能方法這次不跑")
                break
            # 每跑完一個方法就收:Macrobenchmark 的結果檔名常每個模組固定,下一個方法會蓋掉;收進各自的子目錄(判定會往下層找)
            collect_results(cfg, t0, os.path.join(mdir, str(i)))
        st.step("macrobench_judge", [sys.executable, LUMOS, "macrobench", "--repo", root, "--json", "--results-dir", mdir],
                timeout=T_SHORT * 5)


def judge(run_dir):
    try:
        p = subprocess.run([sys.executable, LUMOS, "android-e2e", "judge", run_dir, "--repo", root, "--history"]
                           + (["--no-record"] if SELECTIVE else []), timeout=T_SHORT * 5)
    except subprocess.TimeoutExpired:
        say(f"擋下:lumos android-e2e judge 逾時({T_SHORT * 5} 秒);結果在 {run_dir},可以自己再跑一次 judge")
        return 2
    return p.returncode


def main():
    for s in INTERRUPTS:
        signal.signal(s, on_term)
    signal.signal(signal.SIGINT, on_int)
    global SEL
    if BAD:
        die(f"不認得的參數:{' '.join(BAD)}(認得 --preflight、--changed、--feature、--case、--no-perf、--no-memory)")
    if len(rest) > 1:   # 例:--feature login home —— 第二個字會被當成 run-id、後面的被丟掉
        die(f"多出來的參數:{' '.join(rest[1:])}(run-id 只能給一個;多個功能或情境用逗號連起來,例 --feature login,home)")
    if not SELECTIVE and FLAGS & {"--no-perf", "--no-memory"}:
        die("--no-perf、--no-memory 只能配 --changed、--feature 或 --case;整套跑一定全部跑(推送前要留整套的紀錄)")
    cfg = load_config()
    if SELECTIVE:
        SEL = select()
    serial = pick_serial(cfg["e2e"])
    run_dir = os.path.join(root, ".lumos", "artifacts", "android", run_id)
    preflight(cfg, serial, run_dir)
    if PREFLIGHT:
        print(f"開跑前檢查都過了(裝置 {serial})。")
        return 0
    lock = take_lock(serial)
    st = None
    try:
        clear_toolkit_lock(serial)
        head = run(["git", "-C", root, "rev-parse", "HEAD"])[1].strip()
        st = Steps(run_dir, head, serial)
        accept(cfg, serial, st)
    except (Terminated, KeyboardInterrupt):
        for p in list(GROUPS):
            kill_group(p)
        if st is None:
            drop_lock(lock)
            die("還沒開跑就被中斷,沒寫任何東西")
        st.data["interrupted"] = True
        say("驗收被中斷:寫下「中斷」、交給 judge 記成沒判完")   # say 印不出來也不丟例外,下面照樣落地、交給 judge
    finally:
        stop_listening()   # 收尾與 judge 期間不再接中斷:紀錄要寫完
        drop_lock(lock)
    st.data["ended"] = now()
    st.save()
    rc = judge(run_dir)
    return 2 if st.data["interrupted"] else rc


sys.exit(main())
PY
