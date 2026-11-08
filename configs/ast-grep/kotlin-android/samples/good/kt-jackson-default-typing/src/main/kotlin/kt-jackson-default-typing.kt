fun mapperOne(): ObjectMapper = ObjectMapper().registerModule(KotlinModule.Builder().build())

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes(JsonSubTypes.Type(value = Card::class, name = "card"), JsonSubTypes.Type(value = Bank::class, name = "bank"))
sealed class Payment

fun parse(mapper: ObjectMapper, json: String): Payment = mapper.readValue(json, Payment::class.java)
