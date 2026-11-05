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
