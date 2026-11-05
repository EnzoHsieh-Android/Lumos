package sample.test

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.performClick
import org.junit.Rule
import org.junit.Test

class ListIndexTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun clicksThirdRow() {
        composeTestRule.setContent { ItemList() }
        composeTestRule.onAllNodesWithTag("row")[2].performClick() // BAD
        composeTestRule.onAllNodesWithText("Item").get(0).assertIsDisplayed() // BAD
    }

    @Test
    fun unmergedTreeIndex() {
        composeTestRule.setContent { ItemList() }
        composeTestRule.onAllNodesWithTag("row", useUnmergedTree = true).get(1).assertIsDisplayed() // BAD
    }
}
