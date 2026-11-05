package sample.test

import android.os.Looper.getMainLooper
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.LooperMode

// 好例一:明寫 PAUSED 並手動 idle
@RunWith(RobolectricTestRunner::class)
@LooperMode(LooperMode.Mode.PAUSED)
class PausedLooperTest {
    @Test
    fun postsAfterIdle() {
        val handlerUser = HandlerUser()
        handlerUser.post()
        shadowOf(getMainLooper()).idle()
        assertTrue(handlerUser.ran)
    }
}

// 好例二:不寫 LooperMode,用預設 PAUSED
@RunWith(RobolectricTestRunner::class)
class DefaultLooperTest {
    @Test
    fun postsAfterIdleDefault() {
        val handlerUser = HandlerUser()
        handlerUser.post()
        shadowOf(getMainLooper()).idle()
        assertTrue(handlerUser.ran)
    }
}
