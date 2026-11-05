package sample.test

import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.LooperMode
import org.robolectric.annotation.LooperMode.Mode.LEGACY

@RunWith(RobolectricTestRunner::class)
@LooperMode(LooperMode.Mode.LEGACY) // BAD
class LegacyLooperTest {
    @Test
    fun postsImmediately() {
        val handlerUser = HandlerUser()
        handlerUser.post()
        assertTrue(handlerUser.ran)
    }
}

@RunWith(RobolectricTestRunner::class)
class LegacyMethodLooperTest {
    @Test
    @LooperMode(LEGACY) // BAD
    fun postsImmediatelyOnMethod() {
        val handlerUser = HandlerUser()
        handlerUser.post()
        assertTrue(handlerUser.ran)
    }
}
