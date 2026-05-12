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
1. 라즈베리파이 OS 확인
InfluxDB 2.x는 64-bit Raspberry Pi OS 권장입니다.

uname -m
결과가 아래처럼 나오면 OK입니다.

aarch64
2. 기본 패키지 설치
sudo apt update
sudo apt upgrade -y
sudo apt install -y curl wget gnupg apt-transport-https python3 python3-pip python3-venv
3. InfluxDB 설치
curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key

cat influxdata-archive.key | gpg --dearmor | sudo tee /etc/apt/keyrings/influxdata-archive.gpg > /dev/null

echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
| sudo tee /etc/apt/sources.list.d/influxdata.list

sudo apt update
sudo apt install -y influxdb2
실행:

sudo systemctl enable --now influxdb
접속:

http://라즈베리파이IP:8086
초기 설정에서 아래처럼 만들면 됩니다.

Organization : diehard
Bucket       : pms7003
Token        : 생성 후 복사해두기
4. Grafana 설치
sudo mkdir -p /etc/apt/keyrings

wget -q -O - https://apt.grafana.com/gpg.key \
| gpg --dearmor \
| sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null

echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" \
| sudo tee /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt install -y grafana
실행:

sudo systemctl enable --now grafana-server
접속:

http://라즈베리파이IP:3000
기본 로그인:

ID : admin
PW : admin
5. Grafana에서 InfluxDB 연결
Grafana에서:

Connections
→ Data sources
→ Add data source
→ InfluxDB
설정값:

항목	값
Query language	Flux
URL	http://localhost:8086
Organization	diehard
Token	InfluxDB에서 만든 Token
Default bucket	pms7003
주의할 점은 Docker를 안 쓰는 방식이므로 URL은 http://localhost:8086 입니다.

6. Grafana Query 예시
패널에서 아래 Flux query 사용:

from(bucket: "pms7003")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "dust")
  |> filter(fn: (r) => r._field == "pm1_0" or r._field == "pm2_5" or r._field == "pm10")
  |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
  |> yield(name: "mean")
패널 설정:

Visualization : Time series
Time range    : Last 24 hours
Unit          : µg/m³
Refresh       : 30s 또는 1m
7. Python 수집 프로그램에서는
InfluxDB 접속 주소를 이렇게 쓰면 됩니다.

INFLUX_URL = "http://localhost:8086"
INFLUX_ORG = "diehard"
INFLUX_BUCKET = "pms7003"
INFLUX_TOKEN = "InfluxDB에서_생성한_토큰"
