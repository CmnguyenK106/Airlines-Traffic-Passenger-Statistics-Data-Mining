# Khám phá Mạng lưới Đường bay và Hành vi Liên minh Hàng không
### Phân tích Kinh doanh & Báo cáo Kết quả (Association Rules)
**Tập dữ liệu:** Thống kê Hành khách Hàng không (SFO, giai đoạn 2005–2016)  
**Phương pháp:** Khai phá Luật kết hợp (FP-Growth / Apriori) trên Mạng lưới Code-Share  

---

## Mục lục
1. [Tổng quan Dự án](#1-tổng-quan-dự-án)
2. [Tóm tắt Tập dữ liệu](#2-tóm-tắt-tập-dữ-liệu)
3. [Cấu trúc Giao dịch & Thang đo Thuật toán](#3-cấu-trúc-giao-dịch--thang-đo-thuật-toán)
4. [Các Mô hình Mạng lưới Cốt lõi](#4-các-mô-hình-mạng-lưới-cốt-lõi)
5. [Business Insights theo từng Nhóm lợi ích](#5-business-insights-theo-từng-nhóm-lợi-ích)
   - [Ban quản lý Sân bay (Vận hành SFO)](#ban-quản-lý-sân-bay-vận-hành-sfo)
   - [Hãng hàng không – Chiến lược Cạnh tranh](#hãng-hàng-không--chiến-lược-cạnh-tranh)
   - [Đối tác Bán lẻ & Thương mại](#đối-tác-bán-lẻ--thương-mại)
6. [Tổng hợp các Phát hiện Cốt lõi](#6-tổng-hợp-các-phát-hiện-cốt-lõi)
7. [Danh sách File Đầu ra](#7-danh-sách-file-đầu-ra)

---

## 1. Tổng quan Dự án

Phân tích này áp dụng thuật toán **Khai phá Luật kết hợp (Association Rules - FP-Growth)** để giải mã cấu trúc mạng lưới hàng không tại Sân bay Quốc tế San Francisco (SFO). Thay vì bài toán "Giỏ hàng siêu thị" thông thường, dự án coi mỗi chuyến bay là một "giao dịch" để tìm ra những mối liên kết ẩn giấu giữa **Thương hiệu bán vé**, **Hãng vận hành thực tế**, **Khu vực địa lý** và **Nhà ga**.

Mục tiêu là vạch trần các thỏa thuận Liên danh (Code-sharing), chiến lược thuê ngoài (Outsourcing) đường bay ngắn, và sự độc quyền hạ tầng của các liên minh hàng không toàn cầu. Biến các dòng dữ liệu rời rạc thành một **Bản đồ Mạng lưới (Network Graph)** trực quan, có giá trị cao trong quy hoạch hạ tầng và chiến lược kinh doanh.

---

## 2. Tóm tắt Tập dữ liệu

| Thuộc tính | Chi tiết |
|---|---|
| **Nguồn dữ liệu** | Sân bay Quốc tế San Francisco (SFO) |
| **Giai đoạn** | 2005 – 2016 |
| **Độ chi tiết (Granularity)** | Hồ sơ chuyến bay (Biến đổi thành dạng List giao dịch) |
| **Các cột dữ liệu chính** | `Published Airline` (Hãng bán vé), `Operating Airline` (Hãng bay thực tế), `GEO Region` (Khu vực đến/đi), `Terminal` (Nhà ga) |

---

## 3. Cấu trúc Giao dịch & Thang đo Thuật toán

Mỗi dòng dữ liệu được chuyển hóa thành một "Giỏ hàng" (Transaction) gồm 4 hạng mục (Items), được gắn tiền tố để thuật toán phân biệt vai trò:
* `PUB_`: Hãng phát hành vé (Thương hiệu)
* `OP_`: Hãng vận hành chuyến bay (Tài sản vật lý)
* `GEO_`: Khu vực địa lý
* `TER_`: Nhà ga khởi hành / đến

Các quy luật (Rules) được đánh giá dựa trên 3 thang đo toán học, tương ứng với ý nghĩa kinh doanh:

| Thang đo (Metric) | Mô tả thuật toán | Ý nghĩa Kinh doanh |
|---|---|---|
| **Support (Độ hỗ trợ)** | Tần suất xuất hiện của quy luật trên tổng dữ liệu | **Quy mô hợp tác:** Liên minh này nắm giữ bao nhiêu % thị phần của toàn sân bay? |
| **Confidence (Độ tin cậy)** | Xác suất xảy ra Vế phải khi Vế trái đã xảy ra | **Mức độ phụ thuộc:** Khách mua vé hãng A có tỷ lệ bị đẩy sang hãng B là bao nhiêu? |
| **Lift (Độ nâng)** | Tỷ lệ giữa Confidence và xác suất xảy ra ngẫu nhiên | **Sự liên kết có chủ đích:** $Lift > 1$ chứng tỏ hai hãng chủ động bắt tay nhau tạo thành liên minh chiến lược. |

---

## 4. Các Mô hình Mạng lưới Cốt lõi

Dựa trên các quy luật có **Lift cao** được lọc ra từ thuật toán, thị trường hàng không tại SFO thể hiện 3 mô hình cấu trúc đặc trưng:

| Mô hình Mạng lưới | Quy luật (Rule) Tiêu biểu | Đặc điểm Nhận diện |
|---|---|---|
| **Hub-and-Spoke (Trục và Nan hoa)** | `(PUB_Ông_Lớn) -> (OP_Hãng_Khu_Vực)` | Hãng lớn bán vé nhưng đẩy khách sang máy bay nhỏ của hãng vệ tinh để bay chặng ngắn. |
| **Global Alliance (Liên minh Toàn cầu)** | `(GEO_Quốc_Tế) -> (PUB_Hãng_Ngoại, OP_Hãng_Mỹ)` | Bán chéo vé (Code-share) xuyên lục địa để lấp đầy ghế mà không cần mua thêm máy bay. |
| **Terminal Monopoly (Độc quyền Nhà ga)** | `(PUB_Hãng_A, OP_Hãng_B) -> (TER_Nhà_Ga_X)` | Toàn bộ hệ sinh thái của một Liên minh bị "nhốt" tại một Nhà ga duy nhất. |

---

## 5. Business Insights theo từng Nhóm lợi ích

### Ban quản lý Sân bay (Vận hành SFO)

#### Quy hoạch Hạ tầng & Hậu cần (Logistics)
Phân tích mạng lưới chỉ ra những cặp hãng bay có tỷ lệ "nhồi khách" cho nhau cực cao (Lift > 2.0). Điều này mang lại quyết định quy hoạch sống còn:
- **Tối ưu Băng chuyền Hành lý:** Nếu Hãng A và Hãng B có hợp đồng Code-share mạnh mẽ (khách bay nối chuyến liên tục giữa 2 hãng), sân bay phải bố trí hai hãng này ở chung một Nhà ga, hoặc xây dựng hệ thống luân chuyển hành lý (transfer baggage) ngầm cực kỳ tốc độ giữa khu vực của họ để tránh thất lạc hành lý.
- **Quyền lực Đàm phán:** Khám phá quy luật "Độc quyền Nhà ga" cho thấy các Ông lớn không thể dễ dàng chuyển dời hoạt động. Sân bay có lợi thế lớn khi đàm phán tăng phí thuê mặt bằng hoặc yêu cầu hãng tự bỏ tiền nâng cấp cơ sở vật chất tại nhà ga đó.

### Hãng hàng không – Chiến lược Cạnh tranh

#### Chiến lược "Thuê ngoài" (Outsourcing)
Thuật toán vạch trần mô hình Hub-and-Spoke: Các hãng bay lớn (Legacy Carriers) đang sử dụng thương hiệu của mình để bán vé, nhưng lại "thuê ngoài" các chặng bay ngắn, ít khách cho các hãng hàng không khu vực (Regional Carriers). 
- **Lợi ích:** Giúp Hãng lớn duy trì mạng lưới bay rộng khắp, thu gom khách từ tỉnh lẻ về Hub (SFO) mà không phải chịu chi phí khổng lồ để duy trì và vận hành các đội máy bay cỡ nhỏ.

#### Mở rộng Tầm vóc Toàn cầu (Global Reach)
Bằng cách phân tích các Rule liên kết với `GEO_Region`, hãng bay có thể nhận diện lỗ hổng mạng lưới của mình.
- **Quyết định:** Thay vì tự mở đường bay mới tốn kém sang thị trường xa lạ (như Châu Á), hãng quyết định ký hợp đồng Code-share với một đối tác bản địa (có Support và Lift cao tại khu vực đó) để ngay lập tức đưa thị trường đó vào danh mục bán vé của mình.

### Đối tác Bán lẻ & Thương mại

#### Tối ưu hóa Vị trí Cửa hàng (Retail Placement)
Sự kết hợp giữa `Khu vực địa lý` $\rightarrow$ `Nhà ga` $\rightarrow$ `Hãng bay` cung cấp dữ liệu vi mô cho các thương hiệu bán lẻ:
- Nếu quy luật chỉ ra tệp khách bay đến Châu Á luôn xuất phát từ một Khu vực Cửa ra máy bay (Boarding Area) cụ thể, các thương hiệu cao cấp (Duty-Free, Đồ hiệu, Quà lưu niệm Mỹ) cần đấu thầu bằng được mặt bằng tại khu vực này, vì tệp khách Á Đông có xu hướng chi tiêu mạnh tay trước khi rời Mỹ.

---

## 6. Tổng hợp các Phát hiện Cốt lõi

| Mô hình Khai phá | Tín hiệu Mạng lưới | Đề xuất Hành động Kinh doanh (Action) |
|---|---|---|
| **Mạng lưới Code-Share mạnh** | Lift > 1.5 giữa Hãng Bán vé và Hãng Vận hành | Sân bay: Gom các hãng này vào chung một khu vực để giảm tải hệ thống trung chuyển hành lý. |
| **Độc quyền Cục bộ** | Support cao gắn chặt với 1 Terminal duy nhất | Sân bay: Nắm lợi thế đàm phán; Hãng bay: Nâng cấp trải nghiệm phòng chờ VIP tại "sân nhà". |
| **Dòng chảy Quốc tế** | Liên kết mạnh giữa GEO cụ thể và 1 Hãng bay Mỹ | Bán lẻ: Định vị các thương hiệu ẩm thực / mua sắm phù hợp với văn hóa của tệp khách đó tại cửa Boarding. |

### 💡 Insight Quan Trọng Nhất
> Khai phá Luật kết hợp chứng minh rằng: **Các hãng hàng không không hoạt động độc lập như những hòn đảo, mà chúng đan xen thành các siêu liên minh chiến lược**. Việc nhận diện và lượng hóa sức mạnh của các "mũi tên Code-share" này giúp sân bay ngừng quy hoạch hạ tầng theo từng hãng riêng lẻ, mà chuyển sang quy hoạch theo **Hệ sinh thái Liên minh** — giúp tiết kiệm hàng triệu đô la chi phí hậu cần và tối đa hóa trải nghiệm nối chuyến của hành khách.

---

## 7. Danh sách File Đầu ra

| Tên File | Mô tả |
|---|---|
| `association_rules_network.py` | Script mã nguồn Python sử dụng FP-Growth và NetworkX |
| `code_share_rules_table.csv` | Bảng tổng hợp toàn bộ các quy luật Code-Share kèm chỉ số Support, Confidence, Lift |
| `03_CodeShare_Network.png` | Bản đồ mạng lưới (Network Graph) thể hiện các mối liên minh |
| `04_Terminal_Monopoly_Rules.csv` | Danh sách các quy luật liên kết trực tiếp Hãng bay với Hạ tầng Nhà ga |

---
*Phân tích được thực hiện trong khuôn khổ dự án Data Mining cá nhân, ứng dụng Thuật toán FP-Growth lên tập dữ liệu Airlines Traffic Passenger Statistics.*