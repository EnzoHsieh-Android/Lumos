val r1 = Retrofit.Builder() // BAD
    .baseUrl(BASE)
    .addConverterFactory(GsonConverterFactory.create())
    .addConverterFactory(ScalarsConverterFactory.create())
    .build()
val r2 = Retrofit.Builder().addConverterFactory(json.asConverterFactory(type)).addConverterFactory(ProtoConverterFactory.create()).build() // BAD
val r3 = Retrofit.Builder().addConverterFactory(MoshiConverterFactory.create(moshi)).addConverterFactory(WireConverterFactory.create()).build() // BAD
