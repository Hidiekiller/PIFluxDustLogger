전체 구성
PMS7003
  ↓ UART
Python 수집 프로그램
  ↓
InfluxDB 로컬 DB :8086
  ↓
Grafana 로컬 대시보드 :3000
접속 주소는 보통 이렇게 됩니다.

InfluxDB : http://라즈베리파이IP:8086
Grafana  : http://라즈베리파이IP:3000

패널 설정:

Visualization : Time series
Time range    : Last 24 hours
Unit          : µg/m³
Refresh       : 30s 또는 1m

