package sample.test

import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test

val defaultUser: String = "amy"

object Constants {
    val retryCount = 3
}

class SessionIsolatedTest {
    companion object {
        // 好例一:companion 裡的 lateinit(@BeforeClass 建一次的伺服器之類)
        lateinit var server: FakeServer
        // 好例二:companion 裡的 val
        val timeoutMs = 1_000L
    }

    // 好例三:實例屬性的 var,JUnit 每個測試建新實例
    private var loginCount = 0
    private lateinit var session: Session

    @Before
    fun setUp() {
        session = Session(defaultUser)
    }

    @Test
    fun login() {
        // 好例四:函式裡的區域 var
        var attempts = 0
        attempts++
        loginCount++
        assertEquals(1, attempts + loginCount - 1)
        assertEquals(Constants.retryCount, session.maxRetries)
    }
}
