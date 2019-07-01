from sklearn.cluster import KMeans
import numpy as np
import logging


# Calculate clusters for input vectors
def k_means_calculate(k, vectors):
    try:
        X = np.array(vectors)
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans = kmeans.fit(X)
        results = kmeans.predict(X)
        return results.tolist()
    except Exception as ex:
        logging.error("Error on k_means_calculate: " + str(ex))
    return None
