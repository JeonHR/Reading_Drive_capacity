import os
import pandas as pd
import psutil
from datetime import datetime
import xml.etree.ElementTree as ET
import sys

# XML 파일 경로 설정
xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.xml")

# XML 파일에서 경로 읽기
def read_config_from_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        drives = [drive.text for drive in root.find("Drives").findall("Drive")]
        csv_path = root.find("CSVPath").text
        return drives, csv_path
    except Exception as e:
        print(f"Error reading XML file: {e}")
        sys.exit(1)

# 드라이브 정보 수집
def get_drive_info(drive):
    try:
        usage = psutil.disk_usage(drive)
        return {
            '컴퓨터 명': os.getenv('COMPUTERNAME', 'N/A'),
            '드라이브': drive,
            '드라이브 용량 (GB)': usage.total / (1024 ** 3),
            '사용한 용량 (GB)': usage.used / (1024 ** 3),
            '남은 용량 (GB)': usage.free / (1024 ** 3),
            '사용 비율 (%)': usage.percent,
            '수집 시간': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Error getting drive info for {drive}: {e}")
        sys.exit(1)

# 드라이브 정보 CSV 파일에 저장
def update_drive_info_csv(new_data, output_file):
    try:
        new_df = pd.DataFrame(new_data)
        
        if os.path.isfile(output_file):
            if not os.access(output_file, os.W_OK):
                print(f"Error: No write permission for the file {output_file}")
                return

            existing_df = pd.read_csv(output_file)
            # 동일 컴퓨터의 기존 데이터를 제거하고 최신 데이터로 갱신
            existing_df = existing_df[existing_df['컴퓨터 명'] != new_df['컴퓨터 명'].iloc[0]]
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df
        
        updated_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Drive information updated in {output_file}")
    except Exception as e:
        print(f"Error updating CSV file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # XML 파일에서 경로 읽기
    drives, csv_path = read_config_from_xml(xml_file_path)
    
    # 유효한 경로가 있는지 확인
    if not os.path.isdir(os.path.dirname(csv_path)):
        print(f"CSV file path does not exist: {csv_path}. Please check the path and try again.")
        sys.exit(1)

    # 드라이브 정보 수집 및 CSV 파일 저장
    all_drive_info = []
    for drive in drives:
        if os.path.isdir(drive):
            drive_info = get_drive_info(drive)
            all_drive_info.append(drive_info)
        else:
            print(f"Drive path does not exist: {drive}")

    if all_drive_info:
        update_drive_info_csv(all_drive_info, csv_path)
    else:
        print("No drive information to update.")
        sys.exit(1)
