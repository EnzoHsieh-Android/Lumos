package sample.test

import org.junit.Assert.assertEquals
import org.junit.FixMethodOrder
import org.junit.Test
import org.junit.runners.MethodSorters

var sharedCache: MutableMap<String, String> = mutableMapOf() // BAD

object Fixtures {
    var currentUser: String? = null // BAD
}

@FixMethodOrder(MethodSorters.NAME_ASCENDING) // BAD
class SessionOrderedTest {
    companion object {
        var loginCount = 0 // BAD
    }

    @Test
    fun a_login() {
        loginCount++
        Fixtures.currentUser = "amy"
        assertEquals(1, loginCount)
    }

    @Test
    fun b_reuse() {
        assertEquals("amy", Fixtures.currentUser)
    }
}
