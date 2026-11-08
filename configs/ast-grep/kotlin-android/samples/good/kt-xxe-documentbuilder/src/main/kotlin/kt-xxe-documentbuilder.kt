fun parseOne(input: InputStream): Document {
    val factory = DocumentBuilderFactory.newInstance()
    factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true) // GOOD 官方 XXE 指引
    factory.isExpandEntityReferences = false
    return factory.newDocumentBuilder().parse(input)
}
fun buildOne(): Document {
    return DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument() // GOOD 只產生 XML、不解析
}
