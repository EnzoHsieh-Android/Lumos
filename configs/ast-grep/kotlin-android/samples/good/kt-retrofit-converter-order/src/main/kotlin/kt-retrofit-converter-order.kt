val r1 = Retrofit.Builder()
    .baseUrl(BASE)
    .addConverterFactory(ScalarsConverterFactory.create()) // GOOD 專用在前
    .addConverterFactory(GsonConverterFactory.create())
    .build()
val r2 = Retrofit.Builder().addConverterFactory(ProtobufConverterFactory.create()).addConverterFactory(json.asConverterFactory(type)).build() // GOOD
val r3 = Retrofit.Builder().addConverterFactory(GsonConverterFactory.create()).build() // GOOD 只有一個
