# ✈️ Dự án Khai phá Dữ liệu Hàng không SFO: Tối ưu hóa Vận hành & Chiến lược

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()

## 📖 Tổng quan Dự án (Project Overview)
Dự án này ứng dụng các kỹ thuật Khai phá dữ liệu (Data Mining) chuyên sâu lên tập dữ liệu lịch sử của Sân bay Quốc tế San Francisco (SFO). 

Với mục tiêu phát triển theo định hướng **Analytics Engineering**, dự án không chỉ dừng lại ở việc làm sạch dữ liệu hay huấn luyện các mô hình Machine Learning, mà tập trung vào việc **"dịch thuật" kết quả toán học thành các quyết định chiến lược (Actionable Insights)**. Dữ liệu được khai thác để giải quyết ba bài toán cốt lõi của ngành hàng không: Dự báo năng lực, Định vị thị trường, và Phân tích cấu trúc liên minh.

## 📊 Tập dữ liệu (Dataset)
* **Nguồn:** [Airlines Traffic Passenger Statistics - Kaggle](https://www.kaggle.com/datasets/thedevastator/airlines-traffic-passenger-statistics/data)
* **Phạm vi:** Giai đoạn 2005 – 2016 tại sân bay SFO.
* **Quy mô:** Bao gồm lưu lượng hành khách hàng tháng được phân loại theo Hãng bay, Khu vực địa lý, Nhà ga, và Phân khúc giá vé.

## 🛠️ Công nghệ & Thư viện (Tech Stack)
* **Ngôn ngữ:** Python
* **Xử lý dữ liệu:** `pandas`, `numpy`
* **Machine Learning:** `scikit-learn` (Regression, K-Means)
* **Khai phá Luật kết hợp:** `mlxtend` (FP-Growth)
* **Trực quan hóa:** `matplotlib`, `seaborn`, `networkx`, `adjustText`

---

## 🏗️ Cấu trúc Dự án (Project Architecture)

Dự án được chia thành 1 phần tiền xử lý và 2 phân hệ phân tích độc lập nhưng bổ trợ cho nhau để tạo thành một bức tranh chiến lược toàn cảnh:

### Phần 1: Dự báo Lưu lượng & Phân tích Tính mùa vụ (Time-Series Forecasting) 📈
* **Thuật toán:** Hồi quy Tuyến tính Đa biến (Multiple Linear Regression).
* **Mô tả:** Phân rã dữ liệu chuỗi thời gian thành hai yếu tố: Xu hướng vĩ mô (Trend) và Tính chu kỳ mùa vụ (Seasonality).
* **Business Value:** Giúp Ban quản lý sân bay dự báo chính xác các tháng đỉnh điểm để tối ưu hóa nguồn nhân lực (An ninh, Check-in), đồng thời chọn đúng các tháng "đáy" mùa vụ để lên lịch bảo trì hạ tầng nhằm giảm thiểu rủi ro gián đoạn chuyến bay. Các hãng hàng không sử dụng dữ liệu này để định giá vé tự động (Dynamic Pricing) và điều phối phi đội.

### Phần 3: Khám phá Liên minh Hàng không (Network Discovery) 🕸️
* **Thuật toán:** Khai phá Luật kết hợp (FP-Growth / Association Rules).
* **Mô tả:** Biến đổi các chuyến bay thành các "giao dịch" để vạch trần mạng lưới bán vé liên danh (Code-Share) giữa Hãng bán vé, Hãng vận hành và Nhà ga.
* **Business Value:** Khám phá cấu trúc mạng lưới *Hub-and-Spoke* và sự độc quyền hạ tầng của các liên minh hàng không toàn cầu. Hỗ trợ sân bay tối ưu hóa hệ thống trung chuyển hành lý (transfer baggage) và quy hoạch mặt bằng bán lẻ thương mại (Duty-Free) dựa trên luồng di chuyển thực tế của các liên minh.

---

## 💡 Giá trị Cốt lõi (Key Takeaways)

> *"Dữ liệu giao thông hàng không không chỉ là những con số đếm hành khách vô tri. Nó là hệ quả của các chiến lược cạnh tranh, các thỏa thuận liên minh ngầm và sự dịch chuyển của kinh tế vĩ mô."*

Thông qua 3 góc nhìn: **Predictive** (Dự báo), **Clustering** (Phân cụm) và **Association** (Khai phá luật), dự án này chứng minh năng lực kết hợp giữa kỹ năng lập trình (Data Manipulation/Modeling) và Tư duy Kinh doanh (Business Acumen) để giải quyết các bài toán quản trị thực tiễn có quy mô lớn.

---

