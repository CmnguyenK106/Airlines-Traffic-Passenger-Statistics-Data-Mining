import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from adjustText import adjust_text

# ==========================================
# PHẦN 1: TẢI VÀ TIỀN XỬ LÝ DỮ LIỆU
# ==========================================
print("Đang xử lý dữ liệu và trích xuất đặc trưng khu vực...")
df = pd.read_csv('D:\Data_mining\\assignment\\archive\Air_Traffic_Passenger_Statistics.csv') 

df = df.dropna(subset=['GEO Region'])

geo_total = df.groupby('GEO Region')['Passenger Count'].sum().reset_index(name='Total_Passengers')

low_fare_df = df[df['Price Category Code'] == 'Low Fare']
geo_low_fare = low_fare_df.groupby('GEO Region')['Passenger Count'].sum().reset_index(name='Low_Fare_Passengers')

geo_competition = df.groupby('GEO Region')['Operating Airline'].nunique().reset_index(name='Unique_Airlines')

features_df = geo_total.merge(geo_low_fare, on='GEO Region', how='left').fillna(0)
features_df = features_df.merge(geo_competition, on='GEO Region', how='left')

features_df['Low_Fare_Ratio'] = features_df['Low_Fare_Passengers'] / features_df['Total_Passengers']

# ==========================================
# PHẦN 2: CHUẨN HÓA VÀ CHẠY K-MEANS
# ==========================================
print("Đang huấn luyện mô hình phân cụm K-Means...")
X = features_df[['Total_Passengers', 'Low_Fare_Ratio', 'Unique_Airlines']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
features_df['Cluster'] = kmeans.fit_predict(X_scaled)
features_df['Cluster_Name'] = 'Nhóm Thị trường ' + features_df['Cluster'].astype(str)

# ==========================================
# PHẦN 3: TRỰC QUAN HÓA (VISUALIZATION) ĐÃ CHỈNH SỬA
# ==========================================
print("Đang vẽ bản đồ định vị thị trường...")
plt.figure(figsize=(14, 8))

scatter = sns.scatterplot(
    data=features_df, 
    x='Unique_Airlines', 
    y='Total_Passengers', 
    hue='Cluster_Name', 
    palette='viridis',
    size='Low_Fare_Ratio', 
    sizes=(100, 1500),
    alpha=0.8, 
    edgecolor='black'
)

# Gắn nhãn tên khu vực (GEO Region)
texts = []
for i in range(len(features_df)):
    texts.append(
        plt.text(
            features_df['Unique_Airlines'][i], 
            features_df['Total_Passengers'][i], 
            features_df['GEO Region'][i], 
            fontsize=9,                 # Đã giảm kích thước chữ xuống mức nhỏ gọn
            fontweight='bold', 
            color='#333333'
        )
    )

# Dùng adjust_text để né chữ (Đã bỏ mũi tên)
adjust_text(
    texts, 
    expand_points=(1.5, 1.5) 
    # Đã xóa dòng arrowprops=dict(...) ở đây để bỏ mũi tên chỉ dẫn
)

# Trang trí
plt.title('Phân tích Đặc tính Thị trường Địa lý (GEO Region Clustering)', fontsize=18, fontweight='bold', pad=20)
plt.xlabel('Mức độ Cạnh tranh (Số lượng Hãng bay khai thác)', fontsize=13)
plt.ylabel('Quy mô Thị trường (Tổng lượng Hành khách)', fontsize=13)

ax = plt.gca()
ax.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))

plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0., title="Chú giải (Kích thước = % Giá rẻ)")
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()

# Lưu ảnh
output_dir = 'output_visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
save_path = os.path.join(output_dir, '02B_GEO_Region_Clustering.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')

print(f"✅ Hoàn tất! Đã lưu biểu đồ tại: {save_path}")
plt.show()

# IN THỐNG KÊ CHI TIẾT
print("\n--- PHÂN TÍCH CHI TIẾT CÁC NHÓM THỊ TRƯỜNG ---")
summary = features_df.groupby('Cluster').agg({
    'GEO Region': lambda x: ', '.join(x),
    'Total_Passengers': 'mean',
    'Unique_Airlines': 'mean',
    'Low_Fare_Ratio': 'mean'
}).reset_index()

for idx, row in summary.iterrows():
    print(f"\n[NHÓM {row['Cluster']}] Các khu vực: {row['GEO Region']}")
    print(f" - Khách trung bình: {row['Total_Passengers']:,.0f}")
    print(f" - Số hãng cạnh tranh: {row['Unique_Airlines']:.1f}")
    print(f" - Tỷ lệ vé giá rẻ: {row['Low_Fare_Ratio']*100:.1f}%")