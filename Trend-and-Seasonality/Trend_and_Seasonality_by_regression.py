import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # Thư viện hỗ trợ format ngày tháng
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 1. TẢI VÀ TIỀN XỬ LÝ DỮ LIỆU
# Giả sử df là dataframe của bạn
df = pd.read_csv(r'D:\Data_mining\assignment\archive\Air_Traffic_Passenger_Statistics.csv')

df['Activity Period'] = df['Activity Period'].astype(str)
df['Year'] = df['Activity Period'].str[:4].astype(int)
df['Month'] = df['Activity Period'].str[4:6].astype(int)

monthly_data = df.groupby(['Year', 'Month'])['Passenger Count'].sum().reset_index()
monthly_data = monthly_data.sort_values(by=['Year', 'Month']).reset_index(drop=True)

# ---> ĐIỂM MỚI 1: TẠO CỘT DATETIME THỰC TẾ <---
# Thêm ngày = 1 ảo để Pandas có thể convert thành cấu trúc chuỗi thời gian (YYYY-MM-DD)
monthly_data['Date'] = pd.to_datetime(monthly_data[['Year', 'Month']].assign(DAY=1))

# 2. FEATURE ENGINEERING
monthly_data['Time_Index'] = np.arange(1, len(monthly_data) + 1)
# Lưu ý: Khi get_dummies, ta thao tác trên một dataframe mới để không làm mất cột Date ở dataframe gốc
model_data = pd.get_dummies(monthly_data, columns=['Month'], drop_first=True, dtype=int)

# 3. CHIA TẬP DỮ LIỆU
test_size = 12

# Bỏ cột Date khỏi tập X vì Linear Regression không đọc được định dạng Datetime
X = model_data.drop(columns=['Year', 'Passenger Count', 'Date'])
y = model_data['Passenger Count']
dates = model_data['Date'] # Tách riêng cột Date để lát nữa vẽ biểu đồ

X_train, X_test = X.iloc[:-test_size], X.iloc[-test_size:]
y_train, y_test = y.iloc[:-test_size], y.iloc[-test_size:]
# Chia cả tập Date để vẽ trục X cho Train và Test
dates_train, dates_test = dates.iloc[:-test_size], dates.iloc[-test_size:]

# 4. HUẤN LUYỆN & DỰ BÁO
model = LinearRegression()
model.fit(X_train, y_train)

y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# 5. TRỰC QUAN HÓA VỚI TRỤC THỜI GIAN THỰC TẾ
plt.figure(figsize=(16, 7))

# ---> ĐIỂM MỚI 2: TRỤC X BÂY GIỜ LÀ CỘT 'DATE' <---
# Vẽ đường thực tế
plt.plot(monthly_data['Date'], monthly_data['Passenger Count'], 
         label='Thực tế (Actual)', color='#2ca02c', marker='.', markersize=6, alpha=0.7)

# Vẽ đường dự báo (Train)
plt.plot(dates_train, y_pred_train, 
         label='Dự báo mô hình (Train)', color='#1f77b4', linestyle='--')

# Vẽ đường dự báo (Test)
plt.plot(dates_test, y_pred_test, 
         label='Dự báo tương lai (Test - 12 tháng cuối)', color='#d62728', linewidth=2.5)

# Kẻ vạch phân chia Train/Test bằng ngày cuối cùng của tập Train
plt.axvline(x=dates_train.iloc[-1], color='gray', linestyle=':', linewidth=2, label='Ranh giới Train/Test')

# ---> ĐIỂM MỚI 3: ĐỊNH DẠNG LẠI TRỤC X CHO CHUYÊN NGHIỆP <---
ax = plt.gca()
# Chỉ hiện Tháng/Năm (vd: 01-2015)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
# Mỗi năm hiện 1 vạch tick mark lớn để biểu đồ không bị đặc chữ
ax.xaxis.set_major_locator(mdates.YearLocator())
# Xoay chữ 45 độ cho dễ đọc
plt.xticks(rotation=45)

# Trang trí
plt.title('Dự báo Lưu lượng Hành khách SFO (Khớp với Trục thời gian thực tế)', fontsize=16, fontweight='bold')
plt.xlabel('Thời gian (Tháng - Năm)', fontsize=12)
plt.ylabel('Tổng lượng Hành khách', fontsize=12)
plt.ticklabel_format(style='plain', axis='y') # Tắt format 1e6
plt.legend(loc='upper left')
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()

# Lưu và hiển thị
output_dir = 'output_visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
save_path = os.path.join(output_dir, '01_Trend_Seasonality_RealTimeline.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')

plt.show()