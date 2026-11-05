// 容易誤報:DataStore 官方測試寫法,每個測試用 testScope 與暫存檔建一份
class StoreTest {
    @get:Rule val tmp = TemporaryFolder()
    private val testScope = TestScope()
    private val store = PreferenceDataStoreFactory.create(scope = testScope) { tmp.newFile("t.preferences_pb") } // GOOD
}
