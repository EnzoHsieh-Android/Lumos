// 容易誤報:同樣的 setMain/resetMain 放在本機單元測試(src/test)是對的,這條規則不該掃到
class VmLocalTest {
    @Before fun setUp() {
        Dispatchers.setMain(StandardTestDispatcher()) // GOOD
    }
    @After fun tearDown() { Dispatchers.resetMain() } // GOOD
}
