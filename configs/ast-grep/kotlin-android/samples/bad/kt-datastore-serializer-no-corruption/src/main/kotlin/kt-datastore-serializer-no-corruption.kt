object SettingsSerializer : Serializer<Settings> {
    override val defaultValue = Settings()
    override suspend fun readFrom(input: InputStream): Settings = // BAD
        Json.decodeFromString(input.readBytes().decodeToString())
}
class UserSerializer : Serializer<User> {
    override suspend fun readFrom(input: InputStream): User { // BAD
        return User.parseFrom(input)
    }
}
