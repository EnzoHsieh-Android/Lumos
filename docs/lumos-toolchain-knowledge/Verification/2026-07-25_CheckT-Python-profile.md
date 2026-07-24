---
type: verification
status: pass
date: 2026-07-25
valid_under:
  - "TEST_PROFILES.python:行首錨 PYTHON_TEST_RE+檔名錨 file_name_match(fnmatch)+comment_strip=none+scaffold_name 模板"
  - "discover_test_methods 依 profile.comment_strip 分流(c-style 預設向後相容/none 不剝);檔名錨在 ext 後、讀檔前"
  - "本 repo .lumos/config.json test_profile=python+inline method_regex 收斂 t_(取代非疊加)"
revalidate_when:
  - "動 discover_test_methods/TEST_PROFILES/PYTHON_TEST_RE/cmd_guard_scaffold 的 scaffold_name 接點"
plan_refs:
  - "[[Projects/CheckT-Python-profile_計劃]]"
tags:
  - type/verification
  - status/pass
summary: |-
  TEST:t_python_profile_discovery 9(炸點 fixture t_mid 不被吃/行首認 t_·test_/縮排類內不認/註解 def 不認/檔名錨 helper.py 不認/scaffold_ext+scaffold_name 命中檔名錨/csharp 對照組用 .cs fixture 剝離照舊)+t_python_profile_multiplatform 1(platforms 路徑欄位經 dict 直達)+端到端 doctor Check T「2 條合約 0 偽證據」+全套 1402 綠
  KEY:dogfooding 缺口補上——TEST_PROFILES 加 python(行首錨+檔名錨+comment_strip=none),lumos 自家 Python 合約可走 Check T 形式綁定;真遺忘合約(test+audit 2026-07-24 已備)隨之升回正式硬合約
  KEY:★根因修★=discover_test_methods 原對所有語言剝 C 式註解,test_lumos.py 中文註解 status/* 與 27 萬字元外 glob 字面 **/ 配對、吃掉半個檔(260→94,166 個測試蒸發)——既有地雷,每次 doctor 都在踩,至今無合約指到被吃區間才沒發作。修=comment_strip 語言感知(python=none:行首錨天然排除被註解 # def,不需 hash 剝離器)
  KEY:python profile 誠實天花板(留檔)=無框架註冊標記可錨,行首無斷言 helper 仍判 real;三引號內欄位0 def 極罕誤認;c-style 對 .cs 字串字面 /* 誤剝=既有病另立;haystack 語言範圍與 discover 不一致=訊息措辭失準不影響 real 判定
  VERIFY:design-loop r1 light(canary caught;審計員實測揪出根因改寫整個計劃——原 dirs 診斷是錯的)+std 單席 Codex(2b+4M+1m 全折:行首錨/scaffold_name/file_name_match 型別明定/multiplatform dict 直達/對照組 .cs);TDD 紅→綠
---
# 2026-07-25_CheckT-Python-profile

Check T Python profile 落地＋註解剝離根因修。spec：[[Projects/CheckT-Python-profile_計劃]]。

## 做了什麼
- `TEST_PROFILES` 加 `python`：行首錨（`^def t_*/test_*`，排巢狀/類內/被註解）＋檔名錨（`test_*.py`/`*_test.py`，pytest 收集慣例）＋`comment_strip="none"`＋`scaffold_name="test_{m}"`（scaffold 產物自己命中檔名錨）。
- `discover_test_methods` 依 profile 分流註解剝離（c-style 預設向後相容）；檔名錨在 ext 檢查後、讀檔前。
- 本 repo config 轉 `test_profile: python`；真遺忘合約升回正式 ★INVARIANT★——`doctor` Check T 回「2 條合約 0 偽證據 0 未審」。

## 根因（審計改寫）
原以為是 dirs 找不到資料夾——錯。真兇：discover 對**所有語言**剝 C 式註解，`test_lumos.py` 中文註解的 `status/*` 與遠處 glob 字面 `**/` 配對、一口吃掉半個檔（實測 260→94）。此地雷**既有**、每次 doctor 都在踩。r1 審計員用可執行實測揪出，Codex 複核再折 6 條（行首錨、scaffold 命名、欄位型別、multiplatform 路徑、對照組 fixture）。

## Android 側（順帶體檢）
Citrus_KDS（kotlin，1 合約 0 偽證據，73 節點綠）／CompassKiosk（19 節點綠）均正常；c-style 剝離對其語言正確、不動。
