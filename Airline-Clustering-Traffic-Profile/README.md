# Phân cụm Hãng hàng không theo Hồ sơ Lưu lượng bay
### Phân tích Kinh doanh & Báo cáo Kết quả
**Tập dữ liệu:** Thống kê Hành khách Hàng không (SFO, giai đoạn 2005–2016)  
**Phương pháp:** Phân cụm K-Means dựa trên các Đặc trưng Lưu lượng cấp độ Hãng bay  

---

## Mục lục
1. [Tổng quan Dự án](#1-tổng-quan-dự-án)
2. [Tóm tắt Tập dữ liệu](#2-tóm-tắt-tập-dữ-liệu)
3. [Các Đặc trưng sử dụng để Phân cụm](#3-các-đặc-trưng-sử-dụng-để-phân-cụm)
4. [Phân loại Cụm & Hồ sơ Đặc trưng](#4-phân-loại-cụm--hồ-sơ-đặc-trưng)
5. [Business Insights theo từng Nhóm lợi ích](#5-business-insights-theo-từng-nhóm-lợi-ích)
   - [Ban quản lý Sân bay (Vận hành SFO)](#ban-quản-lý-sân-bay-vận-hành-sfo)
   - [Hãng hàng không – Chiến lược Cạnh tranh](#hãng-hàng-không--chiến-lược-cạnh-tranh)
   - [Nhà đầu tư & Chuyên gia Phân tích](#nhà-đầu-tư--chuyên-gia-phân-tích)
   - [Nhà hoạch định Đường bay & Nhu cầu](#nhà-hoạch-định-đường-bay--nhu-cầu)
6. [Tổng hợp các Phát hiện Cốt lõi](#6-tổng-hợp-các-phát-hiện-cốt-lõi)
7. [Danh sách File Đầu ra](#7-danh-sách-file-đầu-ra)

---

## 1. Tổng quan Dự án

Dự án này áp dụng thuật toán **Phân cụm K-Means** lên tập dữ liệu Thống kê Hành khách Hàng không để phân nhóm các hãng bay dựa trên "hồ sơ lưu lượng" (traffic profile) của họ, thay vì chỉ đánh giá dựa trên quy mô lớn/nhỏ đơn thuần. Mục tiêu là vượt qua các con số thống kê hành khách bề mặt để khám phá sự khác biệt về cấu trúc giữa các hãng vận tải — về cơ cấu đường bay, chiến lược giá vé, độ phủ địa lý và quỹ đạo tăng trưởng.

Phân cụm biến một bảng dữ liệu phẳng thành một **bản đồ cảnh quan cạnh tranh**, vạch trần những hãng bay nào có chiến lược tương đồng, ai là kẻ ngoại lai, và sự dịch chuyển lớn của toàn ngành (chẳng hạn như sự trỗi dậy của các hãng hàng không giá rẻ) được thể hiện trên dữ liệu ra sao.

---

## 2. Tóm tắt Tập dữ liệu

| Thuộc tính | Chi tiết |
|---|---|
| **Nguồn dữ liệu** | Sân bay Quốc tế San Francisco (SFO) |
| **Giai đoạn** | 2005 – 2016 |
| **Độ chi tiết (Granularity)** | Báo cáo theo từng tháng của từng hãng hàng không |
| **Các cột dữ liệu chính** | `Operating Airline` (Hãng vận hành), `GEO Summary` (Tổng quan Địa lý), `GEO Region` (Khu vực), `Activity Type` (Loại hoạt động), `Price Category` (Phân khúc giá), `Terminal` (Nhà ga), `Passenger Count` (Số lượng hành khách) |

---

## 3. Các Đặc trưng (Features) sử dụng để Phân cụm

Mỗi hãng hàng không được tổng hợp thành một dòng duy nhất (1 vector) với 7 đặc trưng được kỹ thuật hóa (Feature Engineering) như sau:

| Đặc trưng | Mô tả toán học | Ý nghĩa Kinh doanh |
|---|---|---|
| `total_passengers` | Tổng lượng hành khách trong toàn bộ giai đoạn | Quy mô tổng thể và mức độ thống trị tại SFO |
| `intl_ratio` | Tỷ lệ hành khách bay Quốc tế | Định hướng hoạt động: Hãng Toàn cầu hay Nội địa |
| `lcc_ratio` | Tỷ lệ hành khách thuộc phân khúc Vé giá rẻ (Low-Cost) | Định vị thương hiệu: Giá rẻ vs. Dịch vụ đầy đủ |
| `terminal_diversity` | Số lượng Nhà ga (Terminal) khác nhau được sử dụng | Mức độ chiếm dụng không gian và hạ tầng tại sân bay |
| `region_diversity` | Số lượng Khu vực địa lý khác nhau được khai thác | Độ phủ và sự đa dạng của mạng lưới đường bay |
| `enplane_ratio` | Tỷ lệ khách cất cánh (Khởi hành) trên tổng hoạt động | Đặc tính trạm: SFO là Điểm đi (Departure-heavy) hay Điểm đến (Arrival-heavy) |
| `growth_ratio` | Lưu lượng TB giai đoạn cuối so với TB giai đoạn đầu | Đà tăng trưởng hoặc suy thoái theo thời gian |

---

## 4. Phân loại Cụm & Hồ sơ Đặc trưng

Số lượng cụm tối ưu được xác định bằng phương pháp **Elbow** và **Silhouette Score**. Mỗi cụm đại diện cho một "Chân dung hãng bay" (Archetype) đặc trưng:

| Chân dung Cụm (Archetype) | Đặc điểm Nhận diện | Ví dụ Thực tế |
|---|---|---|
| **Ông lớn Truyền thống Thống trị**<br>*(Dominant Full-Service Carrier)* | Tổng khách cực cao, độ đa dạng khu vực cao, tỷ lệ quốc tế ở mức trung bình | Hãng bay dùng SFO làm "Hub" với mạng lưới nội địa và quốc tế dày đặc |
| **Chuyên gia Quốc tế Toàn cầu**<br>*(Global International Carrier)* | Tỷ lệ quốc tế cao, đa dạng khu vực cao, lượng khách nội địa thấp | Các hãng chuyên bay đường dài phục vụ Châu Á, Châu Âu... |
| **Thế lực Giá rẻ Đang lên**<br>*(Low-Cost Growth Carrier)* | Tỷ lệ vé giá rẻ (LCC) cao, đà tăng trưởng mạnh, mạng lưới khu vực hẹp | Các hãng hàng không ngân sách thấp đang bành trướng mạnh mẽ tại SFO |
| **Hãng Ngách / Trạm trung chuyển**<br>*(Niche / Regional Carrier)* | Quy mô nhỏ, các chỉ số đa dạng thấp, tăng trưởng âm hoặc đi ngang | Hãng bay nhỏ, bay thuê chuyến hoặc đang trên đà thu hẹp hoạt động |

*(Lưu ý: Nhãn của các cụm được gán tự động bởi thuật toán dựa trên giá trị trung bình của các đặc trưng. Các chân dung trên là tài liệu hướng dẫn diễn giải).*

---

## 5. Business Insights theo từng Nhóm lợi ích

### Ban quản lý Sân bay (Vận hành SFO)

#### Quy hoạch Nhà ga & Cổng ra máy bay (Gates)
Phân cụm vạch trần những hãng bay nào là **người dùng hạng nặng (heavy users)** so với các **người dùng ngách (niche users)**. Các hãng thuộc cụm thống trị (Volume cao, đa dạng nhà ga cao) là nguồn tạo ra áp lực hạ tầng lớn nhất. Sân bay có thể dùng dữ liệu này để:
- Biện minh cho các dự án mở rộng nhà ga tại các khu vực Boarding có nhu cầu cao.
- Phân bổ lại các cổng bay đang bị lãng phí từ tay các cụm có lưu lượng thấp.
- Dự báo nhu cầu không gian trong tương lai dựa trên các cụm đang có đà tăng trưởng nhanh.

#### Tối ưu hóa Doanh thu
Sân bay kiếm tiền từ phí hạ cánh, thuê cổng, cấp phép phòng chờ VIP và bán lẻ. Các cụm có quy mô lớn và độ đa dạng cao đóng góp tỷ trọng doanh thu vượt trội. Quyết định:
- Ưu tiên các Thỏa thuận mức dịch vụ (SLA) và quyền truy cập cổng VIP cho các hãng thuộc cụm thống trị.
- Nhận diện các hãng bay thuộc cụm ngách đang chiếm dụng cổng nhưng mang lại biên lợi nhuận thấp.
- Sử dụng dữ liệu đà tăng trưởng để dự đoán hãng nào sẽ cần thêm không gian trong các năm tới.

#### Phân bổ Nhân sự & Nguồn lực
Các hãng có mức lưu lượng trung bình hàng tháng cao và ổn định đại diện cho **nhu cầu đáng tin cậy quanh năm**. Dữ liệu này định hướng cho:
- Mức độ bố trí nhân sự an ninh tại từng nhà ga.
- Bố trí nhân lực Hải quan và Xuất nhập cảnh cho các cụm quốc tế.
- Các hợp đồng vệ sinh, cung cấp suất ăn và phục vụ mặt đất.

---

### Hãng hàng không – Chiến lược Cạnh tranh

#### Đối chuẩn Cạnh tranh (Competitive Benchmarking)
Thuật toán phân cụm xếp mỗi hãng bay vào một nhóm đối thủ dựa trên hành vi giao thông thực tế, chứ không chỉ quy mô. Một hãng bay có thể tự đặt câu hỏi:
- **Ai đang nằm cùng cụm với tôi?** — Đó mới là đối thủ cạnh tranh thực sự tại SFO.
- **Điều gì tạo ra khoảng cách với các cụm lân cận?** — Những khoảng trống này là cơ hội hoặc lỗ hổng chiến lược.
- **Có sự sai lệch định vị nào không?** — Ví dụ: `intl_ratio` cao nhưng `lcc_ratio` cũng cao cho thấy hãng đang cố cạnh tranh bằng giá trong một phân khúc đòi hỏi chất lượng dịch vụ.

#### Cơ hội Mở rộng Đường bay
Các hãng thuộc cụm **"thống trị nội địa, độ đa dạng khu vực thấp"** có một tín hiệu chiến lược rõ ràng: cần mở rộng ra quốc tế. Sự khác biệt về `region_diversity` và `intl_ratio` giữa các cụm chính là bản đồ chỉ ra những thị trường chưa được khai thác. Hành động trọng tâm:
- Xác định các tuyến bay quốc tế đang bị đối thủ phục vụ nhưng lại vắng bóng trong mạng lưới của mình.
- Đánh giá xem quy mô hoạt động hiện tại (terminal_diversity) có đủ sức hỗ trợ mở rộng hay không.
- Sử dụng xu hướng tăng trưởng để chọn đúng thời điểm gia nhập thị trường.

#### Nhận diện Tín hiệu Rút lui khỏi thị trường
Các hãng có `growth_ratio < 0.8` đang cho thấy sự **suy giảm lưu lượng** tại SFO. Đây là mỏ vàng thông tin cho đối thủ vì:
- Hãng đang suy thoái có thể sắp từ bỏ một số đường bay — tạo ra khoảng trống công suất để lấp đầy.
- Cổng bay và Slot bay của họ có thể sắp được giải phóng để phân bổ lại.
- Các thỏa thuận hợp tác hoặc liên danh (codeshare) có thể trở nên hấp dẫn hơn khi các hãng nhỏ thu hẹp quy mô.

---

### Nhà đầu tư & Chuyên gia Phân tích

#### Động lực học: Giá rẻ vs. Dịch vụ Đầy đủ
Đặc trưng `lcc_ratio` qua các cụm lượng hóa mức độ bành trướng dữ dội của các **Hãng bay giá rẻ so với Hãng truyền thống** trong giai đoạn 2005–2016. Một cụm kết hợp giữa `lcc_ratio` cao và `growth_ratio` cao là bằng chứng trực tiếp cho thấy mô hình Low-Cost đang giành chiến thắng về thị phần, phù hợp với xu hướng toàn cầu trong thập kỷ này.
**Hệ quả đầu tư:** Các hãng thuộc cụm này đang giành được lợi thế cạnh tranh mang tính cấu trúc tại một trong những sân bay quốc tế bận rộn nhất nước Mỹ.

#### Quỹ đạo Tăng trưởng như một Tín hiệu Sớm
Chỉ số `growth_ratio` so sánh 30% thời gian đầu và 30% thời gian cuối của chu kỳ quan sát. Điều này tạo ra một **tín hiệu động lượng dài hạn**, giúp giới phân tích:
- Phát hiện các hãng đang âm thầm chiếm lĩnh thị phần trước khi báo chí đưa tin.
- Cảnh báo về các hãng đang rơi vào suy thoái cấu trúc và có thể đối mặt với áp lực tài chính.
- So sánh hiệu suất riêng tại SFO với bức tranh mạng lưới tổng thể của hãng.

#### Rủi ro Tập trung Thị trường
Nếu một cụm chỉ chứa một số lượng rất nhỏ hãng bay nhưng lại nắm giữ tỷ trọng hành khách cực lớn, điều đó báo hiệu **rủi ro tập trung thị trường** cho sân bay:
- Phụ thuộc nặng nề vào một hãng bay (hoặc một nhóm nhỏ).
- Rủi ro lớn nếu hãng bay thống trị quyết định cắt giảm chuyến bay tại SFO.
- Cần có cơ sở để tung ra các chương trình ưu đãi nhằm thu hút hãng bay từ các cụm khác.

---

### Nhà hoạch định Đường bay & Nhu cầu

#### Cấu trúc Thị trường Quốc tế
Sự kết hợp giữa `intl_ratio` và `region_diversity` chỉ ra rõ ai là những **nhà khai thác toàn cầu thực thụ** so với các hãng gom khách nội địa. Các hãng điểm cao ở cả hai chỉ số này là động lực chính của nhu cầu hành khách quốc tế. Điều này quan trọng đối với:
- Hoạch định nguồn lực Hải quan và Xuất nhập cảnh.
- Đầu tư vào bán lẻ và phòng chờ tại nhà ga quốc tế.
- Dự báo doanh thu miễn thuế và thu đổi ngoại tệ.

#### Diễn giải Tỷ lệ Khởi hành (Enplane Ratio)
Một `enplane_ratio` chênh lệch đáng kể so với mức 0.5 tiết lộ sự mất cân đối về hướng di chuyển của hành khách:
- **Tỷ lệ Khởi hành cao:** SFO chủ yếu là **Trạm xuất phát** — hành khách bắt đầu hành trình tại đây.
- **Tỷ lệ Khởi hành thấp:** SFO chủ yếu là **Trạm đích đến** — hành khách kết thúc hành trình tại đây.
Sự phân biệt này quyết định việc hoạch định nhu cầu: Cụm khởi hành cao đòi hỏi hạ tầng check-in, phòng chờ và bán lẻ trước chuyến bay. Cụm đích đến cao đòi hỏi dịch vụ vận tải mặt đất, băng chuyền hành lý và khách sạn.

#### Hoạch định Nhu cầu Mùa vụ
Các đặc trưng được xây dựng từ dữ liệu hàng tháng phản ánh hành vi mang tính cấu trúc dài hạn. Các cụm có lượng khách trung bình ổn định cung cấp **nhu cầu nền tảng dự đoán được**, giúp nhà hoạch định tự tin ký kết các hợp đồng dài hạn. Các cụm tăng trưởng cao dự báo nhu cầu tương lai, trong khi cụm suy thoái báo hiệu dư địa công suất có thể tái cơ cấu.

---

## 6. Tổng hợp các Phát hiện Cốt lõi

| Chân dung Cụm | Tín hiệu Trọng điểm | Khuyến nghị Hành động Kinh doanh |
|---|---|---|
| **Thống trị, Đa dạng cao** | Lãnh đạo thị trường tại SFO | Ưu tiên không gian cổng ra máy bay, ký hợp đồng dài hạn, đầu tư mở rộng công suất. |
| **`intl_ratio` & `region_diversity` cao** | Hãng toàn cầu thúc đẩy lượng khách quốc tế | Đầu tư mạnh vào hạ tầng Nhà ga Quốc tế và công suất luân chuyển của Hải quan. |
| **`lcc_ratio` & `growth_ratio` cao** | Hãng giá rẻ đang chiếm lĩnh thị phần | Nhận thức rõ áp lực về giá; cân nhắc các phương án cạnh tranh chiến lược về giá vé. |
| **Quy mô & `growth_ratio` thấp** | Hãng ngách hoặc đang lụi tàn | Giám sát các động thái rút khỏi tuyến bay; chuẩn bị kế hoạch tái phân bổ cổng bay. |
| **Chỉ số trung bình trên mọi mặt** | Hãng tầm trung có tiềm năng tăng trưởng | Đưa vào danh sách mục tiêu cho các chương trình hợp tác, ưu đãi hoặc nâng cấp slot bay. |

### 💡 Insight Quan Trọng Nhất
> Phân cụm chứng minh rằng: **Hành vi của các hãng hàng không tại SFO không phải là một chuỗi tuyến tính từ Nhỏ đến Lớn**. Nó là một không gian đa chiều, nơi Lưu lượng, Cấu trúc đường bay, Chiến lược giá và Đà tăng trưởng kết hợp lại tạo thành những bản sắc cạnh tranh hoàn toàn khác biệt. Việc gộp chung tất cả các hãng bay chỉ dựa vào Tổng lượng khách sẽ làm lu mờ đi những sự khác biệt mang tính cấu trúc — vốn là chìa khóa để tối ưu hóa doanh thu sân bay, động lực cạnh tranh và tăng trưởng lưu lượng dài hạn.

---

## 7. Danh sách File Đầu ra

| Tên File | Mô tả |
|---|---|
| `airline_clustering.py` | Script phân tích bằng Python (Các bước 1–9) |
| `airline_clusters.csv` | Danh sách mọi hãng bay kèm Nhãn cụm và Giá trị Đặc trưng |
| `cluster_profiles.csv` | Giá trị đặc trưng trung bình theo từng Cụm |
| `01_feature_distributions.png` | Biểu đồ Histogram của 7 đặc trưng phân cụm |
| `02_correlation_heatmap.png` | Bản đồ nhiệt (Heatmap) thể hiện độ tương quan giữa các biến |
| `03_elbow_silhouette.png` | Biểu đồ ranh giới khuỷu tay (Elbow) và điểm Silhouette |
| `04_pca_clusters.png` | Biểu đồ phân tán (Scatter plot) 2D với nhãn cụm sau khi dùng PCA |
| `05_radar_charts.png` | Biểu đồ mạng nhện (Radar) theo từng cụm |
| `06_cluster_heatmap.png` | Bản đồ nhiệt (Heatmap) Cụm × Đặc trưng |
| `07_top_airlines_per_cluster.png` | Danh sách các hãng bay hàng đầu theo khối lượng hành khách trong mỗi cụm |

---
*Phân tích được thực hiện như một phần của bài tập Data Mining sử dụng tập dữ liệu Airlines Traffic Passenger Statistics từ Kaggle.*