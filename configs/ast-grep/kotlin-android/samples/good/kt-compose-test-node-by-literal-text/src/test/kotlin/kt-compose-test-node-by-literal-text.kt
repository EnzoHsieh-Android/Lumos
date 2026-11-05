package sample.test

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import org.junit.Rule
import org.junit.Test

class LoginResourceTextTest {
    @get:Rule
    val composeTestRule = createAndroidComposeRule<LoginActivity>()

    // 好例一:從資源取字串
    @Test
    fun clicksLoginFromResource() {
        val label = composeTestRule.activity.getString(R.string.login)
        composeTestRule.onNodeWithText(label).performClick()
        composeTestRule.onNodeWithTag("home").assertIsDisplayed()
    }

    // 好例二:用 testTag
    @Test
    fun clicksLoginByTag() {
        composeTestRule.onNodeWithTag("login-button").performClick()
        composeTestRule.onNodeWithTag("home").assertIsDisplayed()
    }

    // 好例三:直接把資源呼叫寫在參數裡
    @Test
    fun welcomeFromResource() {
        composeTestRule.onNodeWithText(composeTestRule.activity.getString(R.string.welcome)).assertIsDisplayed()
    }
}

// 容易誤報:onNodeWithTag 的參數是寫死字串(tag 本來就是給測試用的),不是顯示文字
class LoginTagTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun showsError() {
        composeTestRule.onNodeWithTag("login-error").assertIsDisplayed()
    }
}
