package sample.test

import android.os.SystemClock
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.assertIsDisplayed
import org.junit.Rule
import org.junit.Test

class SplashSleepTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun splashDisappears() {
        composeTestRule.setContent { SplashScreen() }
        Thread.sleep(2_000) // BAD
        composeTestRule.onNodeWithTag("home").assertIsDisplayed()
    }

    @Test
    fun workerFinishes() {
        val worker = SyncWorker()
        worker.start()
        SystemClock.sleep(500) // BAD
        check(worker.done)
    }
}
