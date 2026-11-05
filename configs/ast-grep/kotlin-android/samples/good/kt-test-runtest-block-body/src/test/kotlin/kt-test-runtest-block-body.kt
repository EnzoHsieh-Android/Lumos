package sample.test

import kotlinx.coroutines.test.TestResult
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test

class CounterExpressionBodyTest {
    @Test
    fun increments() = runTest {
        val counter = Counter()
        counter.increment()
        assertEquals(1, counter.value)
    }

    @Test
    fun incrementsTyped(): TestResult = runTest {
        val counter = Counter()
        counter.increment()
        assertEquals(1, counter.value)
    }

    @Test
    fun incrementsInScope() = TestScope().runTest {
        val counter = Counter()
        counter.increment()
        assertEquals(1, counter.value)
    }

    // 區塊本體但沒有 runTest:一般同步測試
    @Test
    fun startsAtZero() {
        val counter = Counter()
        assertEquals(0, counter.value)
    }
}

// 容易誤報:區塊本體但 return runTest { },回傳值沒丟掉
class CounterReturnTest {
    @Test
    fun incrementsWithReturn(): TestResult {
        return runTest {
            val counter = Counter()
            counter.increment()
            assertEquals(1, counter.value)
        }
    }
}
