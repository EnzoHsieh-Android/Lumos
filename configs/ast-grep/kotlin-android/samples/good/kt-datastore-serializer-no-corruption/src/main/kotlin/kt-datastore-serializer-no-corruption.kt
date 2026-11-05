object SettingsSerializer : Serializer<Settings> {
    override suspend fun readFrom(input: InputStream): Settings = // GOOD
        try {
            json.decodeFromString(input.readBytes().decodeToString())
        } catch (e: SerializationException) {
            throw CorruptionException("bad settings", e)
        }
}
class Reader {
    fun readFrom(input: InputStream) = input.readBytes() // GOOD 不是 Serializer
}
