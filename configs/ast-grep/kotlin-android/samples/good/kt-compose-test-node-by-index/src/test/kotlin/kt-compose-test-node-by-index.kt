package sample.test

import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onAllNodesWithTag
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test

class ListTagTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    // 好例一:用唯一 testTag 挑節點
    @Test
    fun clicksRowByTag() {
        composeTestRule.setContent { ItemList() }
        composeTestRule.onNodeWithTag("row-item-3").performClick()
        composeTestRule.onNodeWithTag("detail").assertIsDisplayed()
    }

    // 好例二:onAllNodes 只驗數量,不靠索引挑
    @Test
    fun rowCount() {
        composeTestRule.setContent { ItemList() }
        composeTestRule.onAllNodesWithTag("row").assertCountEquals(3)
    }

    // 好例三:一般清單的索引不是節點查詢
    @Test
    fun plainListIndex() {
        val items = listOf("a", "b", "c")
        assertEquals("c", items[2])
        assertEquals("a", items.get(0))
    }
}

// 容易誤報:onAllNodes 之後用 filterToOne 依語意挑唯一節點,不用索引
class ListFilterTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun clicksAnn() {
        composeTestRule.setContent { ItemList() }
        composeTestRule.onAllNodesWithTag("row").filterToOne(hasText("Ann")).performClick()
    }
}
