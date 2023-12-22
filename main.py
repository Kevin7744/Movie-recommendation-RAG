"""
Package installation

    pip install pymongo

"""

import pymongo

client = pymongo.MongoClient("<Your MongoDb URI>")
db = client.sample_mflix
collection = db.movies


# To test connection
# print(collection.find().limit(5))


import requests

hf_token = "<the hugging face token>"
embedding_url = ""

# Function to create embedding
def generate_embedding(text: str) -> list[float]:
    response = requests.post(
        embedding_url,
        headers={"Authorization": f"Bearer {hf_token}"},
        json = {"inputs": text}
    ) 
    
    if response.status_code != 200:
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    
    return response.json()

print(generate_embedding("Eest sample text"))

# Create vector embeddings for 50 sets in the field plot. 
# You can remove the limit 50 to run the whole data in the databse
for doc in collection.find({'plot':{"$exists": True}}).limit(50):
    doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
    collection.replace_one({'_id': doc['_id']}, doc)


query = "Imaginary characters from outer space at war"

results = collection.aggregate({
    {"$vectorSearch": {
        "queryVector": generate_embedding(query),
        "path": "plot_embedding_hf",
        "numCandidates": 100,
        "limit": 4,
        "index": "PlotSemanticSearch",}}
});

for document in results:
    print(f'Movie Name: {document["title"]}, \nMovie Plot: {document["plot"]}\n')