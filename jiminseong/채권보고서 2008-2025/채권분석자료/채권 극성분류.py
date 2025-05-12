import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 1. 데이터 불러오기
data = pd.read_csv('채권분석TF.csv')

# 2. 결측치 처리
data.fillna(0, inplace=True)

# 3. 특징 벡터로 변환
X = data.values

# 4. PCA로 차원 축소 (시각화용 2차원)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)

# 5. KMeans 클러스터링 (클러스터 3개로 설정)
kmeans = KMeans(n_clusters=3, random_state=42)
clusters = kmeans.fit_predict(X_pca)

# 6. 결과를 데이터프레임에 추가 및 CSV로 저장
data['Sentiment_Cluster'] = clusters
data.to_csv('채권분석_클러스터링결과.csv', index=False, encoding='utf-8-sig')
print("클러스터링 결과가 '채권분석_클러스터링결과.csv'로 저장되었습니다.")

# 7. 클러스터링 결과 시각화
plt.figure(figsize=(10, 7))

# 고유한 클러스터 번호를 가져와서 각 클러스터별로 다른 색상으로 그리기
unique_clusters = np.unique(clusters)
colors = ['blue', 'green', 'orange']  # 필요 시 더 많은 색상 추가

for cluster_label, color in zip(unique_clusters, colors):
    # 해당 클러스터에 속한 포인트들만 추출
    cluster_points = X_pca[clusters == cluster_label]
    plt.scatter(cluster_points[:, 0], cluster_points[:, 1],
                c=color, label=f'Cluster {cluster_label}', alpha=0.5)

# 클러스터 중심(Centroids) 표시
centroids = kmeans.cluster_centers_
plt.scatter(centroids[:, 0], centroids[:, 1],
            s=250, c='red', marker='X', label='Centroids')

# 중심점에 텍스트 레이블 추가
for i, center in enumerate(centroids):
    plt.text(center[0], center[1], f'C{i}', fontsize=12,
             fontweight='bold', color='black', ha='center', va='center',
             bbox=dict(facecolor='white', alpha=0.6, edgecolor='red'))

plt.title('K-means Clustering (3 Clusters) on Sentiment Data')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.legend()
plt.grid(True)
plt.show()

