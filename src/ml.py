from sklearn.cluster import KMeans
import numpy as np


# Calculate clusters for input vectors
def k_means_calculate(k, vectors):
    X = np.array(vectors)
    kmeans = KMeans(n_clusters=k, random_state=0)
    kmeans = kmeans.fit(X)
    results = kmeans.predict(X)
    return results
