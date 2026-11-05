package sample.test

import io.mockk.coVerify
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.junit.Test

class PaymentInteractionTest {
    private val analytics = mockk<Analytics>(relaxed = true)
    private val api = mockk<OrderApi>(relaxed = true)

    @Test // BAD
    fun logsPurchase() {
        val payment = Payment(analytics, api)
        payment.pay(100)
        verify { analytics.log("purchase") }
    }

    @Test // BAD
    fun submitsOrder() = runTest {
        val payment = Payment(analytics, api)
        payment.submit()
        coVerify(exactly = 1) { api.submit(any()) }
    }
}
