import marqo


class MarqoConnector:
    def __init__(self, url: str = 'http://localhost:8882'):
        self.client = marqo.Client(url=url)

    def create_index(self, index_name: str, model: str):
        self.client.create_index(index_name, model=model)

    def add_documents(self, index_name: str, documents: list, tensor_fields: list):
        self.client.index(index_name).add_documents(documents, tensor_fields=tensor_fields)

    def search(self, index_name: str, query: str):
        return self.client.index(index_name).search(q=query)


if __name__ == "__main__":
    marqo_connector = MarqoConnector()
    marqo_connector.create_index("my-first-index", model="hf/e5-base-v2")
    marqo_connector.add_documents(
        "my-first-index",
        [
            {
                "Title": "The Travels of Marco Polo",
                "Description": "A 13th-century travelogue describing Polo's travels"
            },
            {
                "Title": "Extravehicular Mobility Unit (EMU)",
                "Description": "The EMU is a spacesuit that provides environmental protection, "
                               "mobility, life support, and communications for astronauts",
                "_id": "article_591"
            }
        ],
        tensor_fields=["Description"]
    )
    results = marqo_connector.search("my-first-index", "What is the best outfit to wear on the moon?")
    print(results)
