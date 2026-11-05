package bad

class SessionManager(private val store: Store) {
    fun isExpired(s: Session): Boolean {
        return System.currentTimeMillis() > s.expiresAt // BAD
    }

    fun stamp() = Order(createdAt = Instant.now()) // BAD

    fun uptime() = SystemClock.elapsedRealtime() - store.start // BAD

    fun today() = LocalDate.now() // BAD
}
