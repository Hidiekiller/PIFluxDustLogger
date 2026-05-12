import os
import time
import struct
from datetime import datetime, timezone

import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# =========================
# 사용자 설정
# =========================

# GPIO UART 사용 시 보통 /dev/serial0
# USB-UART 사용 시 보통 /dev/ttyUSB0
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600

INFLUX_URL = "http://localhost:8086"
INFLUX_ORG = "KillaDB"
INFLUX_BUCKET = "Dust"
INFLUX_TOKEN = "여기에_InfluxDB_Token_입력"

DEVICE_ID = "pms7003_01"
SITE = "field_01"

# 몇 초 평균값을 InfluxDB에 저장할지
WRITE_INTERVAL_SEC = 5

# 센서 안정화 시간
WARMUP_SEC = 30


# =========================
# PMS7003 처리 함수
# =========================

def checksum_ok(frame: bytes) -> bool:
    if len(frame) != 32:
        return False

    calculated = sum(frame[:30]) & 0xFFFF
    received = (frame[30] << 8) | frame[31]

    return calculated == received


def read_pms7003_frame(ser: serial.Serial) -> bytes:
    """
    PMS7003 32바이트 프레임을 안정적으로 읽음.
    Header 0x42 0x4d를 찾은 뒤 나머지 30바이트 수신.
    """

    while True:
        b1 = ser.read(1)

        if not b1:
            raise TimeoutError("Serial read timeout")

        if b1 != b"\x42":
            continue

        b2 = ser.read(1)

        if b2 != b"\x4d":
            continue

        rest = ser.read(30)

        if len(rest) != 30:
            continue

        frame = b1 + b2 + rest

        if checksum_ok(frame):
            return frame


def parse_pms7003(frame: bytes) -> dict:
    """
    PMS7003 frame 구조:
    2B + 13H + 2B + H = 32 bytes
    """

    data = struct.unpack(">2B13H2BH", frame)

    return {
        "frame_length": data[2],

        "pm1_0_cf1": data[3],
        "pm2_5_cf1": data[4],
        "pm10_cf1": data[5],

        # 일반 대기환경용 값
        "pm1_0": data[6],
        "pm2_5": data[7],
        "pm10": data[8],

        "cnt_0_3": data[9],
        "cnt_0_5": data[10],
        "cnt_1_0": data[11],
        "cnt_2_5": data[12],
        "cnt_5_0": data[13],
        "cnt_10": data[14],
    }


def avg(rows, key):
    return sum(row[key] for row in rows) / len(rows)


# =========================
# 메인
# =========================

def main():
    print("PMS7003 collector start")
    print(f"Serial port : {SERIAL_PORT}")
    print(f"InfluxDB    : {INFLUX_URL}")
    print(f"Org/Bucket  : {INFLUX_ORG} / {INFLUX_BUCKET}")

    client = InfluxDBClient(
        url=INFLUX_URL,
        token=INFLUX_TOKEN,
        org=INFLUX_ORG
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)

    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
        timeout=3
    )

    print(f"Warm-up {WARMUP_SEC} sec...")
    time.sleep(WARMUP_SEC)

    buffer = []
    last_write_time = time.time()

    while True:
        try:
            frame = read_pms7003_frame(ser)
            row = parse_pms7003(frame)

            buffer.append(row)

            now = time.time()

            if now - last_write_time >= WRITE_INTERVAL_SEC and buffer:
                pm1_0 = avg(buffer, "pm1_0")
                pm2_5 = avg(buffer, "pm2_5")
                pm10 = avg(buffer, "pm10")

                point = (
                    Point("dust")
                    .tag("device", DEVICE_ID)
                    .tag("site", SITE)
                    .field("pm1_0", float(pm1_0))
                    .field("pm2_5", float(pm2_5))
                    .field("pm10", float(pm10))
                    .time(datetime.now(timezone.utc), WritePrecision.S)
                )

                write_api.write(
                    bucket=INFLUX_BUCKET,
                    org=INFLUX_ORG,
                    record=point
                )

                print(
                    f"[WRITE] "
                    f"PM1.0={pm1_0:.1f} ug/m3, "
                    f"PM2.5={pm2_5:.1f} ug/m3, "
                    f"PM10={pm10:.1f} ug/m3, "
                    f"samples={len(buffer)}"
                )

                buffer.clear()
                last_write_time = now

        except KeyboardInterrupt:
            print("Stopped by user")
            break

        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(2)

    ser.close()
    client.close()


if __name__ == "__main__":
    main()
