# SOP chi tiết (copy-paste vào Service Desk Plus)

Tài liệu này cung cấp SOP vận hành chi tiết cho 5 dịch vụ ưu tiên theo mô hình L1/L2, có thể copy-paste trực tiếp vào:
- **Category / Subcategory / Item mô tả**
- **Template phản hồi**
- **Resolution notes**
- **Checklist đóng ticket**

---

## 0) Chuẩn dùng chung cho mọi SOP

### 0.1 Trường bắt buộc khi nhận ticket
- Requester
- Affected service
- ITIL Type (Incident/Service Request/Problem/Change/Access)
- Impact
- Urgency
- Priority (map từ Impact x Urgency)
- Short description
- Detailed description
- Business impact
- Evidence (log/screenshot/timestamp)

### 0.2 SLA mục tiêu tạm thời (thay bằng SLA chính thức khi có)
- P1: phản hồi 15m, khôi phục 4h
- P2: phản hồi 30m, xử lý 8h làm việc
- P3: phản hồi 4h làm việc, xử lý 2 ngày làm việc
- P4: phản hồi 1 ngày làm việc, xử lý 5 ngày làm việc

### 0.3 Quy tắc escalate chung
- P1: escalate L2 sau 10 phút nếu chưa có hành động kỹ thuật.
- P2: escalate L2 khi đã dùng 50% SLA mà chưa có hướng xử lý.
- Mọi ticket liên quan bảo mật/compliance/data production: escalate ngay L2.

### 0.4 Template phản hồi chung
**ACK ban đầu**
> Ticket #[TicketID] đã được tiếp nhận với mức ưu tiên [Priority].
> Phân loại: [ITIL Type] | Dịch vụ: [Service].
> Cập nhật tiếp theo trước [ETA].

**Yêu cầu bổ sung thông tin**
> Để xử lý chính xác, vui lòng bổ sung: [logs/screenshot/time range/affected users].

**Cập nhật tiến độ**
> Hiện trạng: [status]. Hành động đang thực hiện: [action]. ETA cập nhật tiếp: [time].

**Đóng ticket**
> Ticket đã được xử lý bằng: [solution].
> Vui lòng xác nhận kết quả trong [x] ngày trước khi hệ thống tự động đóng.

---

## 1) SOP — Jira Administration

### 1.1 Phạm vi
- Login/access issue
- Permission/project role issue
- Workflow/scheme issue
- Automation rule issue
- Integration issue (Jira <-> tool khác)

### 1.2 Phân loại nhanh
- Không truy cập được diện rộng -> Incident (P1/P2)
- Yêu cầu cấp quyền/tạo project -> Service Request (P3/P4)
- Lỗi lặp lại nhiều lần cùng nguyên nhân -> Problem
- Thay đổi workflow/scheme production -> Change

### 1.3 Quy trình L1 (copy-paste)
1. Xác nhận user/project bị ảnh hưởng.
2. Kiểm tra trạng thái dịch vụ Jira (uptime, component status).
3. Kiểm tra account/group/role permission.
4. Thu thập ảnh màn hình + thời điểm lỗi + issue key mẫu.
5. Thử workaround tiêu chuẩn (re-login, clear cache, test bằng user tương đương).
6. Nếu hết lỗi: cập nhật resolution + đóng ticket theo checklist.
7. Nếu chưa hết lỗi và thuộc tiêu chí escalate: chuyển L2 kèm full evidence.

### 1.4 Điều kiện escalate L2
- Ảnh hưởng > 1 team hoặc service gián đoạn.
- Liên quan workflow/scheme/integration phức tạp.
- Cần quyền admin hệ thống Jira.

### 1.5 Resolution note mẫu
> Root cause: [permission misconfiguration / workflow conflict / integration failure].
> Action: [steps].
> Validation: [user confirmed / test case passed].
> Prevention: [KB update / config guardrail].

---

## 2) SOP — Tư vấn kiến trúc dịch vụ (Service Architecture)

### 2.1 Phạm vi
- Tư vấn giải pháp kiến trúc cho dịch vụ mới/cải tiến
- Review NFR (availability, scalability, security, observability)
- Tư vấn tích hợp hệ thống

### 2.2 Intake form bắt buộc (copy-paste)
- Business goal:
- Current pain point:
- Expected users/traffic:
- Availability target (SLA/SLO):
- RTO/RPO:
- Security/compliance requirements:
- Dependencies:
- Timeline:

### 2.3 Quy trình L1
1. Thu thập đầy đủ intake form.
2. Gắn nhãn mức ưu tiên theo business deadline/impact.
3. Kiểm tra thiếu dữ liệu và yêu cầu bổ sung.
4. Chuyển L2 kèm package đầy đủ.

### 2.4 Quy trình L2
1. Đánh giá hiện trạng + constraints.
2. Đề xuất 2-3 option kiến trúc (trade-off chi phí/rủi ro/độ trễ).
3. Khuyến nghị phương án + roadmap thực thi.
4. Ghi rõ assumption và điểm cần quyết định từ business owner.

### 2.5 Deliverable template
- Current state summary
- Proposed architecture options
- Risk register
- Recommended option
- Next 30/60/90-day actions

---

## 3) SOP — Service Desk Plus Administration

### 3.1 Phạm vi
- Form/template/catalog item
- Workflow trạng thái
- SLA policy
- Business rule/automation
- Role/permission

### 3.2 Quy trình thay đổi cấu hình
1. Xác định loại thay đổi: Standard / Normal / Emergency.
2. Đánh giá ảnh hưởng: user scope, service scope, rollback capability.
3. Thực hiện trên môi trường test (nếu có).
4. Chuẩn bị rollback plan.
5. Thực hiện trên production trong change window.
6. Xác nhận sau thay đổi + theo dõi 24h.

### 3.3 Checklist trước deploy
- [ ] Có ticket Change hợp lệ.
- [ ] Có owner phê duyệt.
- [ ] Có backup cấu hình hiện tại.
- [ ] Có rollback steps.
- [ ] Có thông báo tới nhóm liên quan.

### 3.4 Escalation bắt buộc
- Thay đổi có thể ảnh hưởng toàn bộ cổng tiếp nhận ticket.
- Mất dữ liệu biểu mẫu/tự động hóa lỗi diện rộng.
- Lỗi liên quan quyền admin toàn cục.

---

## 4) SOP — Zabbix Administration

### 4.1 Phạm vi
- Alert storm / false positive
- Host/proxy unavailable
- Trigger threshold tuning
- Template/notification issue

### 4.2 Quy trình L1
1. Xác nhận alert source, số lượng host bị ảnh hưởng, thời điểm bắt đầu.
2. Kiểm tra connectivity cơ bản (agent/proxy/network).
3. Kiểm tra maintenance window có đang bật không.
4. Đối chiếu với sự kiện thay đổi gần nhất.
5. Nếu là false positive lặp lại -> đề xuất tuning, chuyển L2.

### 4.3 Quy trình L2
1. Tuning trigger expression/threshold.
2. Rà soát template inheritance.
3. Kiểm tra queue, proxy load, poller/trapper health.
4. Tối ưu notification rule để giảm noise.

### 4.4 Resolution note mẫu
> Incident type: [alert storm / proxy down / trigger mis-tuning].
> Corrective action: [steps].
> Preventive action: [template update / threshold policy].

---

## 5) SOP — GitLab Administration

### 5.1 Phạm vi
- Access/project membership
- Pipeline failures
- Runner issues
- Registry/storage/quota
- Branch protection / merge policy

### 5.2 Quy trình L1
1. Xác nhận project/repo/branch bị ảnh hưởng.
2. Thu thập pipeline ID, job log, commit SHA.
3. Kiểm tra permission role (Guest/Reporter/Developer/Maintainer/Owner).
4. Kiểm tra trạng thái runner shared/group/project.
5. Thực hiện fix tiêu chuẩn nếu có runbook.

### 5.3 Điều kiện escalate L2
- Runner offline diện rộng.
- Pipeline fail hàng loạt nhiều project.
- Vấn đề liên quan registry/storage/performance.
- Chính sách bảo mật branch/protected tag.

### 5.4 Post-resolution checklist
- [ ] Pipeline chạy lại thành công.
- [ ] User xác nhận deploy/build bình thường.
- [ ] Đã cập nhật KB nếu gặp nguyên nhân mới.

---

## 6) Checklist đóng ticket (dùng chung)
- [ ] ITIL Type đúng
- [ ] Priority đúng
- [ ] Root cause được ghi rõ
- [ ] Hành động khắc phục đã xác minh
- [ ] User đã được thông báo/đã xác nhận
- [ ] Có cần mở Problem/Change follow-up không?
- [ ] Bài KB đã được tạo/cập nhật (nếu cần)

---

## 7) KPI vận hành SOP
- SLA compliance by priority/service
- FRT by service
- MTTR by service
- Reopen rate
- Escalation rate L1->L2
- Misclassification rate (ITIL Type)
- CSAT by service
- KB reuse rate

---

## 8) Hướng dẫn copy-paste vào Service Desk Plus
1. Tạo `Template` theo từng service dựa trên các mục 1-5.
2. Gắn `Category/Subcategory/Item` tương ứng service.
3. Cấu hình `Response Templates` từ mục 0.4.
4. Tạo `Resolution Template` từ mục 1.5 / 4.4.
5. Tạo `Closure Checklist` từ mục 6.
6. Tạo `Report/Dashboard` theo mục 7.

