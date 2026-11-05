package sample.test

import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class CartSingleRunTestTest {
    // 好例一:每個測試各自一個 runTest(運算式本體)
    @Test
    fun add() = runTest {
        val cart = Cart()
        cart.add("apple")
        assertEquals(1, cart.size())
    }

    @Test
    fun remove() = runTest {
        val cart = Cart()
        cart.add("apple")
        cart.remove("apple")
        assertEquals(0, cart.size())
    }

    // 好例二:一個 runTest 裡多個 launch,不是多個 runTest
    @Test
    fun concurrentAdds() = runTest {
        val cart = Cart()
        launch { cart.add("a") }
        launch { cart.add("b") }
        advanceUntilIdle()
        assertEquals(2, cart.size())
    }
}

// 容易誤報:兩個 runTest 在兩個不同的測試類別,各自只有一個
class CartCheckoutTest {
    @Test
    fun checkout() = runTest {
        val cart = Cart()
        cart.add("apple")
        assertEquals(1, cart.checkout().items)
    }
}
