import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
from ftplib import FTP

class SimpleVisualizationTool(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_and_visualize_data()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        
        # 창 크기 조정
        self.resize(1200, 600)  # 초기 창 크기 설정 (폭, 높이)
        self.setWindowTitle('Simple Data Visualization Tool')
        self.show()

    def read_config_from_xml(self, xml_file_path):
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            ftp_server = root.find('FTPServer').text
            username = root.find('Username').text
            password = root.find('Password').text
            remote_file = root.find('RemoteFilePath').text
            local_file = root.find('LocalFilePath').text

            return ftp_server, username, password, remote_file, local_file
        except Exception as e:
            print(f"Error reading XML file: {e}")
            return None, None, None, None, None

    def download_file_from_ftp(self, server, username, password, remote_path, local_path):
        try:
            ftp = FTP(server)
            ftp.login(user=username, passwd=password)

            # 파일 다운로드
            with open(local_path, 'wb') as file:
                ftp.retrbinary(f'RETR {remote_path}', file.write)

            ftp.quit()
        except Exception as e:
            print(f"Error downloading file from FTP: {e}")

    def load_and_visualize_data(self):
        # 실행 폴더 내의 XML 파일 경로 지정
        xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.xml")
        if not os.path.isfile(xml_file_path):
            print(f"XML configuration file not found at {xml_file_path}")
            return
        
        ftp_server, username, password, remote_file, local_file = self.read_config_from_xml(xml_file_path)

        if ftp_server is None:
            return

        # FTP에서 파일 다운로드
        self.download_file_from_ftp(ftp_server, username, password, remote_file, local_file)

        # 지정된 CSV 파일이 존재하는지 확인
        if not os.path.isfile(local_file):
            print(f"CSV file not found at {local_file}")
            return

        self.visualize_data(local_file)

    def visualize_data(self, file_path):
        df = pd.read_csv(file_path)

        # 소수점 2자리로 용량 표시 및 수집 시간 형식 맞춤
        df['드라이브 용량 (GB)'] = df['드라이브 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['사용한 용량 (GB)'] = df['사용한 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['남은 용량 (GB)'] = df['남은 용량 (GB)'].apply(lambda x: f"{x:.2f}")
        df['수집 시간'] = pd.to_datetime(df['수집 시간']).apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))

        # 행 수와 열 수 설정
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns) + 1)  # 추가 열 (비율) 포함

        # 열 헤더 설정
        headers = list(df.columns) + ['비율']
        self.table.setHorizontalHeaderLabels(headers)

        for row in range(len(df)):
            for col in range(len(df.columns)):
                self.table.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))

            # 사용 비율(%)에 따라 QProgressBar 생성 및 설정
            usage_ratio = int(df['사용 비율 (%)'][row])  # numpy.float64를 int로 변환
            progress_bar = QProgressBar(self)
            progress_bar.setValue(usage_ratio)  # 사용 비율(%)을 설정
            self.table.setCellWidget(row, len(df.columns), progress_bar)
        
        # 열 크기 자동 조절
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleVisualizationTool()
    sys.exit(app.exec_())
