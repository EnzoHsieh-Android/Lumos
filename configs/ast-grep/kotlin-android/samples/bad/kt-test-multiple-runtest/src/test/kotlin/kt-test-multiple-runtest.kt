package sample.test

import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class CartMultipleRunTestTest {
    @Test
    fun addThenRemove() {
        val cart = Cart()
        runTest {
            cart.add("apple")
            assertEquals(1, cart.size())
        }
        runTest { // BAD
            cart.remove("apple")
            assertEquals(0, cart.size())
        }
    }

    @Test
    fun mixedScopes() {
        val scope = TestScope()
        val cart = Cart()
        runTest {
            cart.add("pear")
        }
        scope.runTest { // BAD
            assertEquals(1, cart.size())
        }
    }
}
