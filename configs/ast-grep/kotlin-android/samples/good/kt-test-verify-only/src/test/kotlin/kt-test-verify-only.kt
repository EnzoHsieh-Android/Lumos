package sample.test

import io.mockk.mockk
import io.mockk.verify
import org.junit.Assert.assertEquals
import org.junit.Test

class PaymentStateTest {
    private val analytics = mockk<Analytics>(relaxed = true)

    // 好例一:verify 之外還斷言可觀察的結果
    @Test
    fun paysAndUpdatesBalance() {
        val wallet = FakeWallet(balance = 500)
        val payment = Payment(analytics, wallet)
        payment.pay(100)
        verify { analytics.log("purchase") }
        assertEquals(400, wallet.balance)
    }

    // 好例二:用假實作只斷言狀態
    @Test
    fun recordsOrder() {
        val api = FakeOrderApi()
        val payment = Payment(analytics, api)
        payment.submit()
        assertEquals(1, api.submitted.size)
    }

    // 好例三:非 @Test 的輔助函式裡呼叫 verify
    private fun verifyLogged(event: String) {
        verify { analytics.log(event) }
    }
}

// 容易誤報:coVerify 搭配斷言回傳結果
class SyncResultTest {
    private val api = mockk<Api>(relaxed = true)

    @Test
    fun syncReturnsCount() = runTest {
        val sync = Sync(api)
        val n = sync.run()
        coVerify { api.push(any()) }
        assertEquals(1, n)
    }
}
