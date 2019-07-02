from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import logging


# Calculate clusters for input vectors k-means
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


# Calculate clusters for input vectors ward hierarchical
def ward_hierarchical_calculate(k, vectors):
    try:
        X = np.array(vectors)
        ward_hir = AgglomerativeClustering(n_clusters=k, linkage="ward")
        results = ward_hir.fit_predict(X)
        return results.tolist()
    except Exception as ex:
        logging.error("Error on k_means_calculate: " + str(ex))
    return None
