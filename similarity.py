from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained SBERT model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can also use 'paraphrase-MiniLM-L6-v2' or other models

def job_title_similarity_sbert(title1, title2):
    # Encode the job titles using SBERT to get embeddings
    embedding1 = model.encode([title1])[0]  # Get the embedding for title1
    embedding2 = model.encode([title2])[0]  # Get the embedding for title2
    
    # Calculate cosine similarity between the two embeddings
    similarity = cosine_similarity([embedding1], [embedding2])[0][0]
    return similarity

# # Example usage
# similarity_score = job_title_similarity_sbert("Telecommunications Engineering Specialist", "Physical Therapist Assistant")
# print(f"Similarity Score: {similarity_score}")
