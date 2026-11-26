severity: clean

**1. 分層與依賴方向**
- 修法把兩處各自讀 package 的地方收成同一支 `_choice_cov_pkg_of`,依賴方向沒有倒置也沒有跨層。
- 這支 helper 放在 `_CHOICE_COV_PKG_RE` 正下方,跟 `_choice_cov_src_pkgs`、`_choice_cov_req` 同在 `_CHOICE_COV_*` 這一族。`_choice_cov_src_pkgs`(`scripts/lumos:79840`)和 `_choice_cov_req`(`scripts/lumos:80000`)現在都呼叫它。
- 上一輪點的「另寫行內正規式」已經不在:`scripts/lumos` 裡這個正規式只剩 `scripts/lumos:79799` 一處定義。
- `_rg_package`(`scripts/lumos:53969`)是 Room 結構檢查用的另一支。它回傳點分隔、不去反引號,跟覆蓋這邊要的斜線分隔、去反引號不同。diff 沒碰它,這個分歧是舊有的,不算這次引入。

**2. 命名與錯誤處理**
- 新名字 `_choice_cov_pkg_of` 沿用 `_choice_cov_*` 前綴。它的 docstring 寫法(一句用途加判準來源)跟鄰居 `_choice_cov_test_srcset` 一致。
- 沒有宣告時回 `""`,跟原本兩處的行為一致,不另拋例外。
- 測試 `t_choice_cov_pkg_of` 沿用 `tempfile.mkdtemp(prefix="gctl-ckc-…")` 和 `try/finally` 加 `_ck_cleanup(tmp)`(`scripts/test_lumos.py:144203`),用 `_load_lumos_inproc()` 載入,docstring 也照鄰居 `t_choice_cov_proj_pkgs` 的格式。
- 筆記已改成「抽 `_choice_cov_pkg_of`,壞法行與掃主程式套件共用」,並補上 `[test:t_choice_cov_pkg_of]`。上一輪「寫改成鄰居同款不實」那條已經修掉,現在的描述跟程式一致。

**3. 第二種做法**
- 這輪修補沒有引入新的第二種做法。package 正規式只剩一支,兩個呼叫端走同一條路徑。
- 正規式把 `[ \t]+` 換成 `[ \t\r\n]+`,沒有用 `\s`,所以全檔守衛(禁止 `\s*` 搭多行旗標)不受影響。

不對齊共 0 條,其中 major 0 條
