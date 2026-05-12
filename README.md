# PIFluxDustLogger
Private Dust Logger with PMS7003
1. InfluxDB 2 설치
InfluxDB는 Linux에서 systemd 서비스로 설치할 수 있고, 공식 문서도 Debian/Ubuntu 계열에서 repository 추가 후 influxdb2 패키지 설치 방식을 안내합니다. 2

sudo apt update
sudo apt install -y curl gnupg

curl --silent --location -O https://repos.influxdata.com/influxdata-archive.key

gpg --show-keys --with-fingerprint --with-colons ./influxdata-archive.key 2>&1 \
| grep -q '^fpr:\+24C975CBA61A024EE1B631787C3D57159FC2F927:$' \
&& cat influxdata-archive.key \
| gpg --dearmor \
| sudo tee /etc/apt/keyrings/influxdata-archive.gpg > /dev/null

echo 'deb [signed-by=/etc/apt/keyrings/influxdata-archive.gpg] https://repos.influxdata.com/debian stable main' \
| sudo tee /etc/apt/sources.list.d/influxdata.list

sudo apt update
sudo apt install -y influxdb2
실행:

sudo systemctl enable --now influxdb
sudo systemctl status influxdb
접속:

http://라즈베리파이IP:8086
여기서 웹 UI로 다음을 생성하면 됩니다.

Org    : diehard
Bucket : pms7003
Token  : Python/Grafana에서 사용할 API Token
2. Grafana 설치
Grafana도 Docker 없이 Debian/Ubuntu 계열에 APT repository로 설치 가능합니다. 공식 문서상 APT repository 방식으로 설치하면 apt-get update 시 업데이트도 같이 관리됩니다. 3

sudo apt-get install -y apt-transport-https wget gnupg

sudo mkdir -p /etc/apt/keyrings

sudo wget -O /etc/apt/keyrings/grafana.asc https://apt.grafana.com/gpg-full.key
sudo chmod 644 /etc/apt/keyrings/grafana.asc

echo "deb [signed-by=/etc/apt/keyrings/grafana.asc] https://apt.grafana.com stable main" \
| sudo tee -a /etc/apt/sources.list.d/grafana.list

sudo apt update
sudo apt install -y grafana
실행:

sudo systemctl enable --now grafana-server
sudo systemctl status grafana-server
접속:

http://라즈베리파이IP:3000
기본 로그인:

ID: admin
PW: admin
처음 로그인하면 비밀번호 변경하라고 나옵니다.

3. Grafana에서 InfluxDB 연결
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
그리고 Save & test.
