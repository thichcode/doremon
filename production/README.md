# Production package — Service Owner (PA2)

Bộ này hiện thực hóa PA2 ở mức app chạy được trên **1 branch**:
- Cấu hình chuẩn hóa dịch vụ/SLA/escalation ở dạng machine-readable JSON.
- Mapping SOP theo từng service ưu tiên.
- Bộ template phản hồi user.
- CLI app để validate config, render template, build payload và **apply trực tiếp sang Service Desk Plus API**.
- CLI app để validate config, render template, và build payload cho Service Desk Plus.

## Cấu trúc
- `app/main.py`: entrypoint CLI.
- `app/config_loader.py`: loader config/templates.
- `app/validator.py`: logic validate cấu hình.
- `app/payload_builder.py`: build payload JSON cho Service Desk Plus.
- `app/sdp_client.py`: client tích hợp Service Desk Plus API (auth + apply + rollback).
- `config/sdp-integration.json`: mapping resource endpoint/method cho API.
- `config/services.json`: danh mục 5 service ưu tiên + nhóm resolver.
- `config/sla-and-escalation.json`: SLA, escalation, CSAT baseline.
- `config/service-sop-map.json`: SOP logic theo từng service.
- `templates/response-templates.json`: mẫu phản hồi ticket.
- `scripts/validate_production_config.py`: wrapper script validate nhanh.

## Chạy app
```bash
python3 -m production.app.main validate
python3 -m production.app.main build-sdp-payload --out production/out/sdp-payload.json
python3 -m production.app.main render-response --template acknowledge --set TicketID=123 --set Priority=P2 --set ITILType=Incident --set Service=Jira --set ETA="30m"
python3 -m production.app.main apply-sdp-config --base-url "https://sdp.example.com" --token "<AUTHTOKEN>" --backup-dir production/out/backups
```

## Môi trường
Có thể dùng env thay cho tham số CLI:
- `SDP_BASE_URL`
- `SDP_AUTHTOKEN`

## Dry run
```bash
python3 -m production.app.main apply-sdp-config --dry-run --base-url "https://sdp.example.com"
```

## Chạy test
```bash
python3 -m unittest production.tests.test_app production.tests.test_sdp_client
```

## Cơ chế rollback
Khi apply thật (không dry-run), app sẽ:
1. Đọc trạng thái hiện tại từng resource qua API GET.
2. Lưu snapshot vào `production/out/backups/sdp-backup-*.json`.
3. Apply resource theo payload.
4. Nếu có lỗi giữa chừng, tự rollback bằng snapshot đã lưu.
python3 -m unittest production.tests.test_app
```

## Ghi chú vận hành
- Các giá trị SLA/escalation hiện là baseline để chạy ngay.
- Khi có file MD chính thức từ bạn, cập nhật lại JSON trong `config/`, chạy `validate`, rồi build lại payload.
