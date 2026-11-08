fun mapperOne(): ObjectMapper {
    val mapper = ObjectMapper()
    mapper.activateDefaultTyping(mapper.polymorphicTypeValidator, ObjectMapper.DefaultTyping.NON_FINAL) // BAD 全域預設型別
    return mapper
}

fun mapperTwo(ptv: PolymorphicTypeValidator): JsonMapper =
    JsonMapper.builder().activateDefaultTyping(ptv).build() // BAD

@Suppress("DEPRECATION")
fun mapperThree(): ObjectMapper = ObjectMapper().also { it.enableDefaultTyping() } // BAD 舊 API
