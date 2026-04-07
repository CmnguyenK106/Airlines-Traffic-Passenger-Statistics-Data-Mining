# Dự báo Lưu lượng Hành khách & Phân tích Tính mùa vụ
### Phân tích Kinh doanh & Báo cáo Kết quả (Time-Series Forecasting)
**Tập dữ liệu:** Thống kê Hành khách Hàng không (SFO, giai đoạn 2005–2016)  
**Phương pháp:** Hồi quy Tuyến tính Đa biến (Multiple Linear Regression) phân rã Chuỗi thời gian  

---

## Mục lục
1. [Tổng quan Dự án](#1-tổng-quan-dự-án)
2. [Tóm tắt Tập dữ liệu](#2-tóm-tắt-tập-dữ-liệu)
3. [Các Đặc trưng sử dụng để Dự báo](#3-các-đặc-trưng-sử-dụng-để-dự-báo)
4. [Phân rã Động lực học Chuỗi thời gian](#4-phân-rã-động-lực-học-chuỗi-thời-gian)
5. [Business Insights theo từng Nhóm lợi ích](#5-business-insights-theo-từng-nhóm-lợi-ích)
   - [Ban quản lý Sân bay (Vận hành SFO)](#ban-quản-lý-sân-bay-vận-hành-sfo)
   - [Hãng hàng không – Chiến lược Cạnh tranh](#hãng-hàng-không--chiến-lược-cạnh-tranh)
   - [Nhà đầu tư & Hoạch định Hạ tầng](#nhà-đầu-tư--hoạch-định-hạ-tầng)
6. [Tổng hợp các Phát hiện Cốt lõi](#6-tổng-hợp-các-phát-hiện-cốt-lõi)
7. [Danh sách File Đầu ra](#7-danh-sách-file-đầu-ra)

---

## 1. Tổng quan Dự án

Phân tích này áp dụng mô hình **Hồi quy Tuyến tính Đa biến** lên dữ liệu tổng lưu lượng hành khách hàng tháng tại SFO. Khác với việc chỉ nhìn vào con số tổng, dự án này phân rã dữ liệu lịch sử thành hai yếu tố cốt lõi: **Xu hướng vĩ mô (Trend)** và **Tính mùa vụ chu kỳ (Seasonality)**. 

Mục tiêu là dự báo chính xác lượng khách trong tương lai, đồng thời trả lời câu hỏi chiến lược: *"Sự tăng trưởng lưu lượng của tháng này là do nền kinh tế thực sự đang đi lên (Trend), hay chỉ đơn giản là do đang bước vào kỳ nghỉ hè (Seasonality)?"*. Khả năng tách bạch hai yếu tố này là nền tảng cho mọi quyết định phân bổ nguồn lực.

---

## 2. Tóm tắt Tập dữ liệu

| Thuộc tính | Chi tiết |
|---|---|
| **Nguồn dữ liệu** | Sân bay Quốc tế San Francisco (SFO) |
| **Giai đoạn** | 2005 – 2016 |
| **Độ chi tiết (Granularity)** | Dữ liệu gom nhóm (Aggregated) theo Tổng hành khách từng Tháng |
| **Các biến (Variables) chính** | `Year`, `Month`, `Passenger Count` (Biến mục tiêu - Target) |

---

## 3. Các Đặc trưng sử dụng để Dự báo

Dữ liệu chuỗi thời gian thô được biến đổi (Feature Engineering) thành các biến số học để đưa vào mô hình Hồi quy:

| Đặc trưng (Feature) | Mô tả thuật toán | Ý nghĩa Kinh doanh |
|---|---|---|
| `Time_Index` | Biến số nguyên tăng dần (1, 2, 3...) theo từng tháng trôi qua. | Bắt dính **Xu hướng (Trend)** dài hạn của ngành hàng không qua các năm. |
| `Month_2` đến `Month_12` | Biến giả (Dummy Variables - 0 hoặc 1) đại diện cho các tháng trong năm (Tháng 1 làm mốc). | Bắt dính **Tính mùa vụ (Seasonality)** để nhận diện tháng cao điểm/thấp điểm cố định hàng năm. |

---

## 4. Phân rã Động lực học Chuỗi thời gian

Mô hình dự báo cho thấy lưu lượng hành khách tại SFO bị chi phối bởi hai thế lực chính:

| Động lực (Dynamics) | Tín hiệu từ Dữ liệu | Khía cạnh phản ánh |
|---|---|---|
| **Trend (Xu hướng)** | Đường cơ sở (baseline) liên tục dốc lên qua các năm (Hệ số $\beta_1$ dương). | **Sức khỏe kinh tế vĩ mô:** Phản ánh GDP tăng trưởng, tỷ lệ thất nghiệp giảm và sự bành trướng của tầng lớp trung lưu sẵn sàng chi tiêu cho du lịch. |
| **Seasonality (Mùa vụ)** | Các đỉnh (Peaks) vào mùa Hè (Tháng 6-8) & Lễ Tết (Tháng 12). Các đáy (Troughs) vào mùa Tựu trường (Tháng 9-10). | **Hành vi người tiêu dùng:** Phản ánh thói quen di chuyển cố định của xã hội, mang tính lặp lại cực kỳ chính xác mỗi năm. |

---

## 5. Business Insights theo từng Nhóm lợi ích

### Ban quản lý Sân bay (Vận hành SFO)

#### Tối ưu hóa Nguồn nhân lực & Chi phí (Staffing)
Tính mùa vụ (Seasonality) là kim chỉ nam cho Giám đốc Vận hành (COO):
- **Tháng Cao điểm (Peak):** Mô hình dự báo trước những tháng có lưu lượng đột biến. Sân bay sẽ chủ động tăng cường tuyển dụng nhân sự bán thời gian (part-time), tăng ca cho đội ngũ an ninh (TSA), hỗ trợ check-in và vệ sinh để tránh vỡ trận.
- **Tháng Thấp điểm (Trough):** Vào các tháng đáy chu kỳ (như tháng 9), sân bay có thể phê duyệt lịch nghỉ phép luân phiên cho nhân sự chính thức, cắt giảm giờ làm để tối ưu hóa quỹ lương mà không ảnh hưởng đến chất lượng dịch vụ.

#### Quản trị Rủi ro & Bảo trì (Maintenance)
Các dự án bảo trì lớn luôn tiềm ẩn rủi ro gây gián đoạn chuyến bay (ví dụ: thảm lại nhựa đường băng, nâng cấp phần mềm băng chuyền hành lý). Bằng cách nhìn vào bản đồ Mùa vụ, Ban quản lý sẽ **cố tình ép lịch khởi công** vào các tháng thấp điểm nhất trong năm để giảm thiểu tối đa thiệt hại kinh tế nếu xảy ra sự cố.

### Hãng hàng không – Chiến lược Cạnh tranh

#### Định giá Động (Dynamic Pricing) & Doanh thu
- **Tối đa hóa Lợi nhuận (Profit Maximization):** Khi mô hình dự báo tháng tới là đỉnh mùa vụ (Cầu vượt Cung), các hãng bay sẽ khóa các hạng vé giá rẻ (`Low Fare`), đẩy giá vé lên mức trần để tối ưu hóa biên lợi nhuận trên mỗi ghế.
- **Kích cầu (Demand Stimulation):** Tại các tháng đáy mùa vụ, chi phí cố định (thuê máy bay, lương phi hành đoàn) vẫn phải trả. Các bộ phận Marketing sẽ dùng dữ liệu dự báo này để tung ra các chiến dịch "Mùa Thu Vàng", "Flash Sale" nhằm kích thích nhu cầu, cố gắng lấp đầy ghế trống càng nhiều càng tốt.

#### Điều phối Mạng lưới và Đội bay (Fleet Allocation)
Hãng bay có thể luân chuyển các máy bay thân rộng (như Boeing 777) vào các đường bay có mùa vụ đang lên để chở được nhiều khách nhất, đồng thời đưa các máy bay vào xưởng bảo dưỡng định kỳ (C-check, D-check) vào những tháng lưu lượng được dự báo giảm sút.

### Nhà đầu tư & Hoạch định Hạ tầng

#### Quyết định Đầu tư Vốn (CapEx Planning)
Yếu tố Xu hướng (Trend) là chỉ báo quan trọng nhất cho các quyết định dài hạn. Nếu đường Trend thể hiện mức tăng trưởng liên tục 5-7%/năm, các nhà hoạch định chiến lược có thể tính toán chính xác được: **Đến tháng/năm nào thì tổng lưu lượng sẽ chính thức vượt qua công suất thiết kế tối đa của nhà ga hiện tại?**
- Từ đó, họ có đủ thời gian chuẩn bị (thường là 3-5 năm) để xin giấy phép, lập ngân sách và khởi công xây dựng Nhà ga (Terminal) hoặc đường băng mới trước khi tình trạng quá tải xảy ra.

---

## 6. Tổng hợp các Phát hiện Cốt lõi

| Giai đoạn Dự báo | Hành động của Sân bay | Hành động của Hãng Hàng không |
|---|---|---|
| **Đỉnh Mùa vụ (Peaks)**<br>*(Tháng 6-8, Tháng 12)* | Tối đa hóa công suất, tăng cường nhân sự an ninh & dịch vụ mặt đất. | Đẩy giá vé lên mức trần, triển khai máy bay thân rộng. |
| **Đáy Mùa vụ (Troughs)**<br>*(Tháng 9, Tháng 10)* | Lên lịch bảo trì hạ tầng lớn, phê duyệt nghỉ phép cho nhân viên. | Tung khuyến mãi kích cầu, đưa máy bay vào bảo dưỡng định kỳ. |
| **Xu hướng Tăng Dài hạn**<br>*(Trend Line)* | Khởi động dự án nâng cấp năng lực nhà ga & bãi đỗ. | Mở rộng quy mô đội bay, đàm phán mua thêm Slot bay tại SFO. |

### 💡 Insight Quan Trọng Nhất
> Việc bóc tách dữ liệu chuỗi thời gian chứng minh rằng: **Lãnh đạo doanh nghiệp không nên hoảng loạn khi thấy lượng khách tháng này giảm so với tháng trước, và cũng không nên tự mãn khi thấy lượng khách tăng vọt**. Sự thay đổi đó có thể chỉ là tính chu kỳ tự nhiên của thời gian (Seasonality). Một doanh nghiệp chỉ thực sự khỏe mạnh khi đường Xu hướng (Trend) – thứ đã được loại bỏ mọi nhiễu động mùa vụ – duy trì được góc nghiêng dương ổn định.

---

## 7. Danh sách File Đầu ra

| Tên File | Mô tả |
|---|---|
| `trend_forecasting_regression.py` | Script mã nguồn Python xử lý dữ liệu và huấn luyện mô hình Linear Regression |
| `historical_and_forecast_data.csv` | Bảng dữ liệu chứa giá trị thực tế và giá trị dự báo của mô hình trên tập Test |
| `01_Trend_Seasonality_Forecast.png` | Biểu đồ trực quan hóa đường thực tế và đường dự báo theo các tháng ảo |
| `01B_RealTimeline_Forecast.png` | Biểu đồ trực quan hóa khớp với trục thời gian thực (Năm/Tháng) |
| `model_evaluation_metrics.txt` | Báo cáo tóm tắt các chỉ số sai số của mô hình (R-squared, RMSE) |

---
*Phân tích được thực hiện trong khuôn khổ dự án Data Mining cá nhân, ứng dụng thuật toán Hồi quy tuyến tính đa biến (Multiple Linear Regression) lên tập dữ liệu Airlines Traffic Passenger Statistics.*