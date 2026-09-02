# metric-guard code r1 通才席(standard 循序單席)
H-1|major|blocking:是:findall[-1] 當「最新」賭加列方向——新列插上方(常見寫法)實測仍抓舊 rev,防線失準。
引句:「latest = logm[-1] if logm else ""」
H-2|minor:只驗 START 唯一;內文提早出現 END 字面=靜默截斷雜湊,紅得誤導。
引句:「text.count("METRIC-CRITERIA:START") == 1」
H-3|minor:iterdir 不遞迴,scripts/hooks 等子層在掃描面外(現網零漏報,休眠風險);autonomous_loop 副檔名白名單同型。
引句:「scan = [q for q in (root / "scripts").iterdir() if q.is_file()]」
H-4|minor:紅字訊息吐 Python 變數名 ALLOWED,違白話家規。
引句:「加進 ALLOWED,數字值進閘就立事故(spec C 節)」
抑噪:bootstrap 值親算一致 4020fe48;標記邊界與 spec 自洽;ALLOWED 突變=紅還原淨空;現況 4 綠。
severity: major
