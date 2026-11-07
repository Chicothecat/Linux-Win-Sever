# Thực nghiệm SSH và Fail2ban

Mã thực hành cho chương 4 của báo cáo. Môi trường gồm Windows 11 làm máy kiểm thử và Ubuntu trên VMware làm máy chủ SSH. Chỉ thực hiện với máy ảo và tài khoản lab thuộc phạm vi được phép kiểm thử.

Địa chỉ minh họa: Windows `192.168.232.1`, Ubuntu `192.168.232.131`, tài khoản `lab`, SSH TCP 22. Thay địa chỉ khi môi trường thực tế khác. Các tệp này được dựng lại theo quy trình trong báo cáo; không phải mã gốc được trích xuất từ PDF.

## 1 Chuẩn bị trên Ubuntu

Tại thư mục repository:

```bash
bash ubuntu/install.sh
```

Script cài OpenSSH và Fail2ban, có thể khiến Fail2ban khởi động theo chính sách gói. Dùng tài khoản `lab` đã có mật khẩu. Nếu UFW đang bật, thiết lập quy tắc phù hợp để Windows truy cập TCP 22. Bài thử dùng xác thực mật khẩu; cần bảo đảm tài khoản được phép dùng phương thức này.

Lấy dấu vân tay khóa máy chủ trực tiếp trong cửa sổ Ubuntu:

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

## 2 Kiểm tra từ Windows

Trong PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\windows\check_connection.ps1
py -m pip install -r requirements.txt
```

Khi SSH hỏi lần đầu, đối chiếu dấu vân tay với Ubuntu trước khi chấp nhận. Đăng nhập rồi dùng `exit` để trở về Windows. Khóa máy chủ được lưu trong `%USERPROFILE%\.ssh\known_hosts`. Python dùng tệp này và từ chối khóa chưa được tin cậy hoặc đã thay đổi.

## 3 Lượt thử trước bảo vệ

Chạy trực tiếp trong cửa sổ Ubuntu:

```bash
sudo systemctl stop fail2ban
sudo systemctl is-active fail2ban
```

Trạng thái cần là `inactive`; lệnh kiểm tra trả mã khác 0 khi dịch vụ không hoạt động. Trên Windows:

```powershell
py ssh_lab.py --host 192.168.232.131 --user lab
```

Nhập mật khẩu đúng khi chương trình hỏi; mật khẩu không được hiển thị hoặc ghi ra log. Chương trình thử tối đa 11 lần gồm 10 mẫu sai và mật khẩu đối chứng ở cuối. Mỗi lần mở một kết nối mới, chỉ dùng xác thực mật khẩu; dừng khi thành công hoặc gặp lỗi kết nối. Kết quả dự kiến là thành công lần 11 nếu không có cơ chế khác chặn trước đó. Đây là bài thử danh sách hữu hạn, không phải vét cạn không gian mật khẩu.

## 4 Bật Fail2ban

Trên Ubuntu:

```bash
bash ubuntu/enable_protection.sh
```

Script sao lưu cấu hình sshd.local nếu có, chép cấu hình trong `config/sshd.local`, kiểm tra cú pháp rồi bật Fail2ban. Tham số: `maxretry=5`, `findtime=10m`, `bantime=2m`, đọc nhật ký bằng backend systemd.

Chờ quá 10 phút sau lượt thử trước để các lỗi cũ ra khỏi khoảng xét, rồi kiểm tra trạng thái ban trước lượt mới. Nếu địa chỉ Windows đang bị cấm, bỏ cấm trực tiếp trên Ubuntu:

```bash
sudo fail2ban-client set sshd unbanip 192.168.232.1
sudo fail2ban-client status sshd
```

## 5 Lượt thử sau bảo vệ

Chạy lại đúng lệnh Python, cùng tài khoản và mật khẩu đối chứng. Không khởi động lại Fail2ban trong lượt thử. Sau đó trên Ubuntu:

```bash
bash ubuntu/check_evidence.sh
```

Đối chiếu thời điểm thử, IP nguồn, các lần xác thực thất bại, sự kiện `Ban` và `Banned IP list`. Số lượt Python hiển thị có thể khác ngưỡng 5 vì bộ lọc có thể ghi nhận nhiều sự kiện hoặc hành động cấm được áp dụng trễ. Lỗi mạng riêng lẻ chưa chứng minh Fail2ban đã cấm IP.

Thử một kết nối mới trên Windows trong lúc IP còn bị cấm:

```powershell
ssh -o ConnectTimeout=5 lab@192.168.232.131
```

## 6 Bỏ cấm và kiểm tra khôi phục

Trực tiếp trên Ubuntu:

```bash
sudo fail2ban-client set sshd unbanip 192.168.232.1
```

Trên Windows, chạy lại SSH và nhập mật khẩu đúng. Chạy `whoami` sau khi đăng nhập để chứng minh hoàn tất. Chỉ thấy lời nhắc mật khẩu chưa chứng minh đăng nhập thành công.

## Các tệp

| Tệp | Mục đích |
| --- | --- |
| ssh_lab.py | Thử 10 mật khẩu sai và một mật khẩu đối chứng |
| config/sshd.local | Cấu hình nhóm bảo vệ sshd |
| ubuntu/install.sh | Cài gói và khởi động SSH |
| ubuntu/enable_protection.sh | Kiểm tra cấu hình và bật Fail2ban |
| ubuntu/check_evidence.sh | Đọc nhật ký và danh sách IP bị cấm |
| windows/check_connection.ps1 | Kiểm tra TCP và đăng nhập thủ công |

Mã Python được kiểm tra cú pháp khi đóng gói. Chưa chạy thực nghiệm trên cặp máy Windows Ubuntu trong môi trường này; kết quả thực tế cần được ghi nhận tại máy lab.
