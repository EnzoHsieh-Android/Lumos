package good

class SessionManager(private val clock: Clock) {
    fun isExpired(s: Session) = clock.millis() > s.expiresAt
    fun stamp() = Order(createdAt = Instant.now(clock))
    fun today() = LocalDate.now(clock)
}

class AndroidClock : TimeProvider {
    override fun now() = System.currentTimeMillis()
    override fun elapsed() = SystemClock.elapsedRealtime()
}

object SystemWallClock : Clock() {
    override fun instant(): Instant = Instant.now()
}

// 容易誤報:Android 的 SystemClock、System.nanoTime() 找不到權威原文說要改成注入,這條不報
class Uptime(private val start: Long) {
    fun elapsed() = SystemClock.elapsedRealtime() - start
    fun nanos() = System.nanoTime()
}

// 容易誤報:System.currentTimeMillis()、Date() 只有 Sonar 一條測試碼規則提到,沒有權威原文講正式碼,這條不報
class Legacy(private val s: Session) {
    fun isExpired() = System.currentTimeMillis() > s.expiresAt
    fun stamp() = Date()
}
