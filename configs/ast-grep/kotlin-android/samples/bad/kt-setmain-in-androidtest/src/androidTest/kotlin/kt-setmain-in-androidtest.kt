class UiTest {
    @Before fun setUp() {
        Dispatchers.setMain(StandardTestDispatcher()) // BAD
    }
    @Test fun t() { setMain(dispatcher) } // BAD
}
