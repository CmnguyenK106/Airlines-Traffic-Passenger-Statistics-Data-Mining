import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import os
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

# ==========================================
# PHẦN 1: TẢI VÀ TẠO "GIỎ HÀNG" (TRANSACTIONS)
# ==========================================
print("1. Đang xử lý dữ liệu và tạo tập Giao dịch...")
df = pd.read_csv('D:\\Data_mining\\assignment\\archive\\Air_Traffic_Passenger_Statistics.csv')

# Lọc bỏ các dòng bị lỗi hoặc không có hãng cụ thể
df = df.dropna(subset=['Operating Airline', 'Published Airline', 'GEO Region'])

# ĐIỂM QUAN TRỌNG: Để mô hình hiểu được vai trò của từng item, ta thêm tiền tố (Prefix)
# PUB_ : Hãng bán vé (Thương hiệu mà khách hàng mua)
# OP_  : Hãng vận hành (Máy bay thực tế khách ngồi)
# GEO_ : Khu vực địa lý
df['Item_PUB'] = 'PUB_' + df['Published Airline']
df['Item_OP'] = 'OP_' + df['Operating Airline']
df['Item_GEO'] = 'GEO_' + df['GEO Region']

# Tạo danh sách các "Giao dịch" (Transactions)
# Mỗi dòng dữ liệu (1 cấu hình chuyến bay) là 1 giỏ hàng chứa 3 món: [Hãng bán vé, Hãng bay thật, Khu vực]
transactions = df[['Item_PUB', 'Item_OP', 'Item_GEO']].values.tolist()

# Mã hóa (One-Hot Encoding) tập giao dịch để thuật toán có thể đọc được
te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
basket_df = pd.DataFrame(te_ary, columns=te.columns_)

# ==========================================
# PHẦN 2: CHẠY THUẬT TOÁN FP-GROWTH
# ==========================================
print("2. Đang khai phá Luật kết hợp (FP-Growth)...")
# Dùng FP-Growth thay vì Apriori vì nó chạy nhanh hơn rất nhiều với dataset lớn
# min_support=0.01 nghĩa là tổ hợp này phải xuất hiện trong ít nhất 1% tổng số chuyến bay
frequent_itemsets = fpgrowth(basket_df, min_support=0.01, use_colnames=True)

# Tạo các luật kết hợp (Association Rules)
# min_threshold=0.5: Độ tin cậy (Confidence) tối thiểu 50%
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# CHỈ LỌC RA CÁC LUẬT LIÊN QUAN ĐẾN CODE-SHARE (LIÊN DANH)
# Ta muốn tìm quy luật: Nếu mua vé của hãng X (PUB) -> Bay máy bay của hãng Y (OP)
def is_code_share_rule(antecedents, consequents):
    # Trích xuất dạng chuỗi
    ant_str = ','.join(list(antecedents))
    con_str = ','.join(list(consequents))
    # Kiểm tra: Vế trái là hãng bán vé, vế phải là hãng vận hành
    # Và đảm bảo hãng bán vé KHÁC hãng vận hành (loại bỏ các chuyến hãng tự bán tự bay)
    if 'PUB_' in ant_str and 'OP_' in con_str:
        pub_name = ant_str.replace('PUB_', '')
        op_name = con_str.replace('OP_', '')
        return pub_name != op_name
    return False

# Áp dụng hàm lọc
rules['Is_Code_Share'] = rules.apply(lambda row: is_code_share_rule(row['antecedents'], row['consequents']), axis=1)
code_share_rules = rules[rules['Is_Code_Share']].copy()

# Sắp xếp theo độ Nâng (Lift) - Lift càng cao, mối liên kết càng chặt chẽ
code_share_rules = code_share_rules.sort_values(by='lift', ascending=False).reset_index(drop=True)

# ==========================================
# PHẦN 3: VẼ BẢN ĐỒ MẠNG LƯỚI (NETWORK GRAPH)
# ==========================================
print("3. Đang vẽ bản đồ Liên minh Hàng không...")
plt.figure(figsize=(15, 10))
G = nx.DiGraph() # Đồ thị có hướng (Directed Graph)

# Thêm các Node (Hãng bay) và Edges (Luật Code-share) vào đồ thị
# Chỉ lấy top 20 luật mạnh nhất để bản đồ không bị rối như tổ nhện
top_rules = code_share_rules.head(20)

for idx, row in top_rules.iterrows():
    # Lấy tên hãng bỏ đi tiền tố PUB_ và OP_
    seller = list(row['antecedents'])[0].replace('PUB_', '')
    operator = list(row['consequents'])[0].replace('OP_', '')
    
    # Lift dùng để tính độ dày của mũi tên liên kết
    lift_weight = row['lift']
    
    # Thêm cạnh nối từ Người bán (Seller) -> Người bay (Operator)
    G.add_edge(seller, operator, weight=lift_weight)

# Xác định vị trí các Node bằng thuật toán lò xo (spring_layout) để giãn cách đều
pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)

# Vẽ các Node (Chấm tròn)
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='skyblue', alpha=0.8, edgecolors='black')

# Vẽ các Cạnh (Mũi tên liên danh)
# Độ dày mũi tên tỷ lệ thuận với Lift
edges = G.edges()
weights = [G[u][v]['weight'] * 0.5 for u,v in edges]
nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle='-|>', arrowsize=20, width=weights, edge_color='gray')

# Vẽ Nhãn (Tên hãng bay)
nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_family='sans-serif')

plt.title('Bản đồ Mạng lưới Liên danh (Code-Share Network)\nMũi tên chỉ từ Hãng bán vé -> Hãng vận hành thực tế', fontsize=16, fontweight='bold', pad=20)
plt.axis('off') # Tắt trục tọa độ

# Lưu ảnh
output_dir = 'output_visualizations'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
save_path = os.path.join(output_dir, '03_CodeShare_Network.png')
plt.savefig(save_path, dpi=300, bbox_inches='tight')
print(f"✅ Đã lưu bản đồ mạng lưới tại: {save_path}")

plt.show()

# IN RA TOP CÁC LUẬT ĐỂ PHÂN TÍCH
print("\n--- TOP CÁC HỢP ĐỒNG LIÊN DANH CHẶT CHẼ NHẤT (Sắp xếp theo Lift) ---")
for i, row in top_rules.head(5).iterrows():
    ant = list(row['antecedents'])[0].replace('PUB_', '')
    con = list(row['consequents'])[0].replace('OP_', '')
    print(f"Nếu khách mua vé của [{ant}] => {row['confidence']*100:.1f}% khả năng bị đẩy sang bay máy bay của [{con}] (Lift: {row['lift']:.2f})")