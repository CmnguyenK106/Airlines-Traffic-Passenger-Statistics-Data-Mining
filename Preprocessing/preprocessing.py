import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def clean_and_visualize_data(file_path):
    print("⏳ Đang tải và phân tích dữ liệu...")
    # 1. Tải dữ liệu gốc
    df_raw = pd.read_csv(file_path)
    df_clean = df_raw.copy()
    
    # ==========================================
    # LƯU TRẠNG THÁI TRƯỚC KHI LÀM SẠCH (BEFORE)
    # ==========================================
    # Đếm số lượng rỗng của mỗi cột
    missing_before = df_raw.isnull().sum()
    missing_before = missing_before[missing_before > 0].sort_values(ascending=False)
    
    # Tính tổng khách của từng hãng bay (để xem nhiễu)
    airline_totals_before = df_raw.groupby('Operating Airline')['Passenger Count'].sum()

    # ==========================================
    # THỰC HIỆN LÀM SẠCH (CLEANING PROCESS)
    # ==========================================
    print("🧹 Đang thực hiện các bước làm sạch...")
    # 1. Xóa cột thừa
    df_clean = df_clean.drop(columns=['Operating Airline IATA Code', 'Published Airline IATA Code'], errors='ignore') 
    
    # 2. Điền giá trị rỗng cho Terminal
    if 'Terminal' in df_clean.columns:
        df_clean['Terminal'] = df_clean['Terminal'].fillna('Unknown')
        
    # 3. Xóa dòng rỗng ở các cột quan trọng
    df_clean = df_clean.dropna(subset=['GEO Region', 'Price Category Code'])

    # 4. Loại bỏ hành khách <= 0
    df_clean = df_clean[df_clean['Passenger Count'] > 0]
    
    # 5. Loại bỏ hãng bay nhiễu (Tổng khách < 50,000)
    threshold = 50000
    airline_totals = df_clean.groupby('Operating Airline')['Passenger Count'].transform('sum')
    df_clean = df_clean[airline_totals > threshold].reset_index(drop=True)

    # ==========================================
    # LƯU TRẠNG THÁI SAU KHI LÀM SẠCH (AFTER)
    # ==========================================
    missing_after = df_clean.isnull().sum()
    missing_after = missing_after[missing_after > 0] # Lọc các cột còn rỗng (Kỳ vọng là trống không)
    
    airline_totals_after = df_clean.groupby('Operating Airline')['Passenger Count'].sum()

    # ==========================================
    # TRỰC QUAN HÓA (VISUALIZATION DASHBOARD)
    # ==========================================
    print("📊 Đang vẽ biểu đồ báo cáo...")
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('BÁO CÁO CHẤT LƯỢNG DỮ LIỆU (BEFORE & AFTER CLEANING)', fontsize=18, fontweight='bold', y=0.98)

    # --- BIỂU ĐỒ 1: Missing Values (Trước) ---
    if not missing_before.empty:
        sns.barplot(x=missing_before.values, y=missing_before.index, ax=axes[0, 0], palette="Reds_r")
        axes[0, 0].set_title('Dữ liệu Khuyết thiếu - TRƯỚC (Số lượng Null)', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Số lượng dòng bị Null')
    else:
        axes[0, 0].text(0.5, 0.5, 'Không có Null', ha='center', fontsize=14)

    # --- BIỂU ĐỒ 2: Missing Values (Sau) ---
    if not missing_after.empty:
        sns.barplot(x=missing_after.values, y=missing_after.index, ax=axes[0, 1], palette="Greens_r")
    axes[0, 1].set_title('Dữ liệu Khuyết thiếu - SAU', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlim(axes[0, 0].get_xlim()) # Đồng bộ trục X với biểu đồ trước để dễ so sánh

    # --- BIỂU ĐỒ 3: Nhiễu Hãng bay (Trước) ---
    # Dùng thang đo Logarit (log_scale) vì chênh lệch giữa hãng nhỏ và lớn là quá khủng khiếp
    sns.histplot(airline_totals_before, bins=30, log_scale=True, ax=axes[1, 0], color='#e74c3c')
    axes[1, 0].axvline(threshold, color='black', linestyle='--', linewidth=2, label=f'Ngưỡng cắt ({threshold})')
    axes[1, 0].set_title('Phân phối Quy mô Hãng bay - TRƯỚC', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Tổng lượng Hành khách lịch sử (Thang đo Logarit)')
    axes[1, 0].set_ylabel('Số lượng Hãng bay')
    axes[1, 0].legend()

    # --- BIỂU ĐỒ 4: Nhiễu Hãng bay (Sau) ---
    sns.histplot(airline_totals_after, bins=30, log_scale=True, ax=axes[1, 1], color='#2ecc71')
    axes[1, 1].set_title('Phân phối Quy mô Hãng bay - SAU (Đã lọc nhiễu)', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Tổng lượng Hành khách lịch sử (Thang đo Logarit)')
    axes[1, 1].set_ylabel('Số lượng Hãng bay')
    axes[1, 1].set_xlim(axes[1, 0].get_xlim()) # Đồng bộ trục X

    plt.tight_layout(rect=[0, 0, 1, 0.96]) # Chừa khoảng trống cho tựa đề tổng
    
    # Lưu ảnh báo cáo
    output_dir = 'output_visualizations'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    save_path = os.path.join(output_dir, '00_Data_Cleaning_Report.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Đã lưu Dashboard báo cáo làm sạch tại: {save_path}")
    
    plt.show()

    # In thông số rút gọn
    print("\n--- THỐNG KÊ NHANH ---")
    print(f"Dòng ban đầu: {len(df_raw):,} | Hãng bay ban đầu: {df_raw['Operating Airline'].nunique()}")
    print(f"Dòng sau dọn: {len(df_clean):,} | Hãng bay giữ lại: {df_clean['Operating Airline'].nunique()}")
    print(f"Số dòng bị xóa: {len(df_raw) - len(df_clean):,} ({(len(df_raw) - len(df_clean))/len(df_raw)*100:.2f}%)")

    return df_clean

# Chạy thử
CSV_FILE_PATH = 'D:\Data_mining\\assignment\\archive\Air_Traffic_Passenger_Statistics.csv'
cleaned_df = clean_and_visualize_data(CSV_FILE_PATH)