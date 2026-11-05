package sample.test

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import org.junit.Rule
import org.junit.Test

class LoginTextTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun clicksLogin() {
        composeTestRule.setContent { LoginScreen() }
        composeTestRule.onNodeWithText("Login").performClick() // BAD
        composeTestRule.onNodeWithText( "Welcome", substring = true).assertIsDisplayed() // BAD
    }
}
