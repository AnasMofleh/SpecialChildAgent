from scraper import WebScraper
from semantic_kernel.functions import kernel_function
import numpy as np
import pandas as pd


class WebsiteReaderPlugin:
    """A simple plugin to retrieve relevant content from a website."""

    def __init__(self, client, embeddings_model):
        self.client = client
        self.embeddings_model = embeddings_model
        self.base_urls = [
            "https://mittspeciellabarn.se/",
            "https://mittspeciellabarn.se/community-support/",
            "https://mittspeciellabarn.se/activities/",
            "https://mittspeciellabarn.se/services/",
            "https://mittspeciellabarn.se/about-us/",
        ]
        self.df = None

    async def read_index(self, filename="urlEmbeddings.csv"):
        try:
            self.df = pd.read_csv(filename)
            self.df["embeddings"] = self.df.embeddings.apply(eval).apply(np.array)
            print(f"✅ Loaded index from {filename}.")
        except FileNotFoundError:
            print(f"❌ File {filename} not found. Building index ...")
            chunks, links = self.build_index()
            embeddings = await self.get_embeddings(chunks)
            self.df = pd.DataFrame(
                {"url": links, "text": chunks, "embeddings": embeddings}
            )
            self.df.to_csv(filename, index=False)
            print(f"✅ Index built and saved to {filename}.")

    @kernel_function(
        description="Provides relevant information and resources from the website."
    )
    async def search_website(self, user_query, top_k=3):
        try:
            print("🔍 Searching for relevant information...")
            # Extract actual query text from the dict
            if isinstance(user_query, dict):
                user_query = list(user_query.values())[0]
            user_query_embedding = await self.get_embeddings([user_query])
            similarities = self.df.embeddings.apply(
                lambda e: self.cosine_similarity(e, user_query_embedding[0])
            )
            top_indices = similarities.nlargest(top_k).index
            top_texts = self.df.loc[top_indices, "text"].tolist()
            print("✅ Found relevant information.")
            return top_texts
        except Exception as e:
            print("❌ Error in search_website function:", e)
            print("user_query:", user_query)
            return ["could not find any relevant information."]

    ################################################
    ############### helper functions ###############
    ################################################

    def build_index(self, max_level=4):
        """Build an index of the website content."""

        unique_links_dict = WebScraper().scrape(self.base_urls, max_level=max_level)
        chunks = []
        links = []
        for url, text in unique_links_dict.items():
            if text.strip():
                chunked = self.chunk_text(text)
                chunks.extend(chunked)
                links.extend([url] * len(chunked))
        print(
            f"✅ Created {len(chunks)} text chunks ready for embedding. Compared to the original {len(unique_links_dict.keys())} text chunks."
        )
        return chunks, links

    def chunk_text(self, text, max_tokens=300):
        """Chunk the text into smaller pieces of tokens."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), max_tokens):
            chunk = " ".join(words[i : i + max_tokens])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    async def get_embeddings(self, texts):
        embeddings = await self.client.embeddings.create(
            input=texts, model=self.embeddings_model, dimensions=1536
        )
        embeddings = [e.embedding for e in embeddings.data]
        return embeddings

    async def get_embedding(self, text):
        embeddings = await self.client.embeddings.create(
            input=[text], model=self.embeddings_model, dimensions=1536
        )
        return embeddings.data[0].embedding

    def cosine_similarity(self, a, b):
        from scipy.spatial.distance import cosine

        # Note that scipy.spatial.distance.cosine computes the cosine distance, which is 1 - cosine similarity.
        # https://en.wikipedia.org/wiki/Cosine_similarity#Cosine_distance
        return 1 - cosine(a, b)
