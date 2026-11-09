// 語意覆核級已知誤報:收集的是有限流,launch 會自己結束,形狀看不出流是不是無限
class FiniteTest {
    @Test fun a() = runTest {
        val list = mutableListOf<Int>()
        launch { repo.finiteFlow().collect { list += it } }
        advanceUntilIdle()
    }
    @Test fun b() = runTest {
        val values = mutableListOf<Int>()
        launch { flowOf(1, 2).collect { values += it } }   // 有限流;不用 toList(會撞會擋的 TEST-5)
        advanceUntilIdle()
    }
}
