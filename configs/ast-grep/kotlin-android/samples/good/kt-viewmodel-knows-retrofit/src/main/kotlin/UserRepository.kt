import retrofit2.HttpException // GOOD:資料層認得 retrofit 是對的

// 容易誤報:同樣 import retrofit2、catch HttpException,但在資料層,並把它轉成網域錯誤再往上丟
class UserRepository(private val api: UserApi) {
    suspend fun load(): User = try {
        api.user()
    } catch (e: HttpException) {
        throw NetworkError(e.code())
    }
}
