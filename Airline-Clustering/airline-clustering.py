import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. TẢI DỮ LIỆU VÀ TIỀN XỬ LÝ (Nếu chưa tải)
df = pd.read_csv(r'D:\Data_mining\assignment\archive\Air_Traffic_Passenger_Statistics.csv')

# --- ĐIỂM QUAN TRỌNG: Lọc dữ liệu ---
# Đôi khi có những hãng bay 'chỉ ghé qua 1 lần' làm nhiễu dữ liệu. 
# Ta chỉ phân tích những dữ liệu có thật (Adjusted) hoặc lấy tổng quan.
# Ở đây ta giả định dùng toàn bộ dữ liệu.

# 2. FEATURE ENGINEERING (Tạo đặc trưng cho từng hãng bay)
# a. Tính tổng lượng khách của mỗi hãng
airline_total = df.groupby('Operating Airline')['Passenger Count'].sum().reset_index(name='Total_Passengers')

# b. Tính lượng khách bay vé giá rẻ (Low Fare)
low_fare_df = df[df['Price Category Code'] == 'Low Fare']
low_fare_stats = low_fare_df.groupby('Operating Airline')['Passenger Count'].sum().reset_index(name='Low_Fare_Passengers')

# c. Tính lượng khách bay Quốc tế (International)
intl_df = df[df['GEO Summary'] == 'International']
intl_stats = intl_df.groupby('Operating Airline')['Passenger Count'].sum().reset_index(name='Intl_Passengers')

# Gộp (Merge) các bảng lại với nhau
features_df = airline_total.merge(low_fare_stats, on='Operating Airline', how='left').fillna(0)
features_df = features_df.merge(intl_stats, on='Operating Airline', how='left').fillna(0)

# Tạo các tỷ lệ (Ratios) quan trọng cho mô hình
features_df['Low_Fare_Ratio'] = features_df['Low_Fare_Passengers'] / features_df['Total_Passengers']
features_df['Intl_Ratio'] = features_df['Intl_Passengers'] / features_df['Total_Passengers']

# Lọc bỏ các hãng bay quá nhỏ (ví dụ < 50,000 khách trong toàn bộ lịch sử) để tránh nhiễu
features_df = features_df[features_df['Total_Passengers'] > 50000].reset_index(drop=True)

# 3. CHUẨN HÓA DỮ LIỆU (DATA SCALING)
# K-Means cực kỳ nhạy cảm với sự chênh lệch đơn vị. Total_Passengers là hàng triệu, 
# trong khi Ratio chỉ từ 0-1. Ta phải Scale chúng về cùng một hệ quy chiếu.
X = features_df[['Total_Passengers', 'Low_Fare_Ratio', 'Intl_Ratio']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. CHẠY THUẬT TOÁN K-MEANS
# Giả sử qua phân tích Elbow Method, ta chọn K = 4 (chia làm 4 nhóm hãng bay)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
features_df['Cluster'] = kmeans.fit_predict(X_scaled)

# Lưu tên cụm (Tên này có thể thay đổi tùy vào kết quả chạy thực tế của bạn)
# Ta đánh nhãn tạm thời là Cụm 0, 1, 2, 3
features_df['Cluster_Name'] = 'Cụm ' + features_df['Cluster'].astype(str)

# 5. TRỰC QUAN HÓA KẾT QUẢ (VISUALIZATION)
plt.figure(figsize=(14, 8))

# Sử dụng Seaborn để vẽ Scatter Plot
# Trục X: Tỷ lệ vé giá rẻ | Trục Y: Tổng lượng khách | Kích thước bóng: Tỷ lệ bay Quốc tế
scatter = sns.scatterplot(
    data=features_df, 
    x='Low_Fare_Ratio', 
    y='Total_Passengers', 
    hue='Cluster_Name', 
    palette='Set1', 
    size='Intl_Ratio', 
    sizes=(50, 800), # Kích thước bong bóng nhỏ nhất -> lớn nhất
    alpha=0.7, 
    edgecolor='black'
)

# Thêm tên của các hãng bay lớn vào biểu đồ để dễ nhận diện
# Chỉ đánh dấu các hãng có trên 5 triệu khách để tránh rối mắt
for i in range(len(features_df)):
    if features_df['Total_Passengers'][i] > 5000000:
        plt.text(features_df['Low_Fare_Ratio'][i] + 0.01, 
                 features_df['Total_Passengers'][i], 
                 features_df['Operating Airline'][i], 
                 fontsize=9, fontweight='bold')

# 1. VẼ BIỂU ĐỒ TƯƠNG TÁC VỚI PLOTLY
fig = px.scatter(
    features_df,
    x='Low_Fare_Ratio',
    y='Total_Passengers',
    color='Cluster_Name',
    size='Intl_Ratio',          # Kích thước bong bóng theo Tỷ lệ Quốc tế
    hover_name='Operating Airline', # Điểm "ăn tiền": Di chuột vào sẽ hiện tên hãng!
    size_max=40,                # Giới hạn kích thước bong bóng lớn nhất
    title='Bản đồ Định vị Hãng Hàng không (K-Means Clustering)',
    labels={
        'Low_Fare_Ratio': 'Tỷ trọng Vé Giá Rẻ (0 - 1.0)',
        'Total_Passengers': 'Tổng quy mô Hành khách',
        'Cluster_Name': 'Cụm Hãng bay',
        'Intl_Ratio': 'Tỷ trọng Quốc tế'
    },
    template='plotly_white'     # Giao diện nền trắng chuyên nghiệp
)

# 2. TÙY CHỈNH THÊM CHO ĐẸP
fig.update_layout(
    font=dict(size=12),
    hoverlabel=dict(bgcolor="white", font_size=14, font_family="Rockwell")
)

# 3. LƯU THÀNH FILE HTML TƯƠNG TÁC VÀ HIỂN THỊ
output_dir = 'output_visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

save_path_html = os.path.join(output_dir, '02_Airline_Clustering_Interactive.html')
fig.write_html(save_path_html)
print(f"✅ Đã lưu biểu đồ tương tác tại: {save_path_html}. Hãy mở file này bằng trình duyệt Web (Chrome/Edge)!")

# Hiển thị ngay trên Jupyter Notebook
fig.show()

# IN THỐNG KÊ CỦA TỪNG CỤM ĐỂ PHÂN TÍCH INSIGHT
cluster_summary = features_df.groupby('Cluster').agg({
    'Operating Airline': 'count',
    'Total_Passengers': 'mean',
    'Low_Fare_Ratio': 'mean',
    'Intl_Ratio': 'mean'
}).rename(columns={'Operating Airline': 'Số lượng Hãng'})
print("\n--- ĐẶC ĐIỂM TRUNG BÌNH CỦA CÁC CỤM ---")
print(cluster_summary)