import numpy as np

# Specify the path to your co-occurrence matrix file
#co_occurrence_file = "edgeOnly.csv"
co_occurrence_file="explicit_cooccurrence_matrix_11_12_2023.csv"
outFilePrefix='QAnon_Reddit_Explicit_Clusters'
numclustersBegin=2
numclustersEnd=6

# Load the co-occurrence matrix from the file
data = np.loadtxt(co_occurrence_file, delimiter=',', dtype=str)
data=data[1:]

# Extract the terms and counts from the loaded data
terms = np.unique(np.concatenate((data[:, 0], data[:, 1])))
term_indices = {term: index for index, term in enumerate(terms)}
counts = data[:, 2].astype(int)
print(f"num terms = ",len(terms))

# Create an empty co-occurrence matrix
num_terms = len(terms)
co_occurrence_matrix = np.zeros((num_terms, num_terms), dtype=int)

# Populate the co-occurrence matrix with the counts
for term1, term2, count in data:
    index1 = term_indices[term1]
    index2 = term_indices[term2]
    co_occurrence_matrix[index1, index2] = count
    co_occurrence_matrix[index2, index1] = count  # Assuming co-occurrence is symmetric

# Print the co-occurrence matrix
#print(co_occurrence_matrix[0:5])

from sklearn.cluster import KMeans

# Assuming you have a term co-occurrence matrix stored in a numpy array called 'co_occurrence_matrix'
# Each row represents a term and each column represents a document or occurrence

# Set the number of clusters you want to create

for num_clusters in range(numclustersBegin,numclustersEnd+1):
    # Create an instance of KMeans with the desired number of clusters
    kmeans = KMeans(n_clusters=num_clusters)

    # Fit the model to the term co-occurrence matrix
    kmeans.fit(co_occurrence_matrix)

    # Get the cluster labels for each term
    cluster_labels = kmeans.labels_

    with open (outFilePrefix+str(num_clusters)+'.csv','w') as f:
        for term, label in zip(terms, cluster_labels):
            f.write(f"{term},{label}\n")


