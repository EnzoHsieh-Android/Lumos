// 正式碼:專案放在名叫 test 的祖先目錄底下(.../test/app/src/main/...)。
// 下面的寫法放在 src/test 或 src/androidTest 會被「只掃測試碼」的規則命中;
// 這裡是正式碼,那些規則一處都不准命中(路徑過濾要錨在 src/ 底下,不能只看路徑裡有沒有 test)。

var lastSyncAt: Long = 0L

object SessionHolder {
    var currentUser: String? = null
}

class RateLimiter {
    fun pause() {
        Thread.sleep(200)
        SystemClock.sleep(50)
        lastSyncAt = System.currentTimeMillis()
    }

    fun drain() = runBlocking {
        delay(100)
    }
}

class ScreenFactory {
    fun create(): HomeViewModel = HomeViewModel(Repo())
}

@LooperMode(LooperMode.Mode.LEGACY)
class DemoHarness {
    fun mainSwap() {
        Dispatchers.setMain(StandardTestDispatcher())
    }

    fun demo() = runTest {
        val io = StandardTestDispatcher()
        launch { feed.toList(items) }
        assertEquals(0, items.size)
    }

    fun demoAgain() {
        runTest { first() }
        runTest { second() }
    }

    suspend fun watch() {
        withTimeout(1_000) {
            feed.test { awaitItem() }
        }
        state.toList()
    }

    fun pick() {
        rule.onAllNodesWithTag("row")[0].performClick()
        rule.onNodeWithText("Login").performClick()
    }

    @Test
    fun smoke() {
        verify { repo.load() }
    }
}

class ClockDemo {
    fun virtual() = runTest {
        val io = UnconfinedTestDispatcher()
        work(io)
    }

    @Test
    fun blockBody() {
        runTest { work() }
    }

    @Test
    fun noCheck() {
        work()
    }
}
