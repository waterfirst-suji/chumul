"""
닷컴 버블과 AI 붐 비교 분석을 위한 경제 데이터 수집 스크립트
FRED API와 yfinance를 활용하여 다양한 경제 지표를 수집합니다.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EconomicDataCollector:
    """경제 데이터 수집 클래스"""

    def __init__(self):
        self.dotcom_start = "1995-01-01"
        self.dotcom_end = "2003-12-31"
        self.ai_start = "2020-01-01"
        self.ai_end = datetime.now().strftime("%Y-%m-%d")

    def get_stock_data(self, ticker, start_date, end_date):
        """주식 데이터 수집"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def get_nasdaq_data(self):
        """NASDAQ 지수 데이터 수집"""
        print("NASDAQ 지수 데이터 수집 중...")

        # 닷컴 버블 시기
        nasdaq_dotcom = self.get_stock_data("^IXIC", self.dotcom_start, self.dotcom_end)
        if nasdaq_dotcom is not None:
            nasdaq_dotcom.to_csv('bubble_analysis/data/nasdaq_dotcom.csv')
            print(f"  - 닷컴 시기: {len(nasdaq_dotcom)} 레코드 수집 완료")

        # AI 붐 시기
        nasdaq_ai = self.get_stock_data("^IXIC", self.ai_start, self.ai_end)
        if nasdaq_ai is not None:
            nasdaq_ai.to_csv('bubble_analysis/data/nasdaq_ai.csv')
            print(f"  - AI 시기: {len(nasdaq_ai)} 레코드 수집 완료")

        return nasdaq_dotcom, nasdaq_ai

    def get_tech_stocks_dotcom(self):
        """닷컴 버블 시기 주요 기술주 데이터 수집"""
        print("\n닷컴 버블 시기 주요 기술주 데이터 수집 중...")

        tech_stocks = {
            'MSFT': 'Microsoft',
            'CSCO': 'Cisco',
            'INTC': 'Intel',
            'ORCL': 'Oracle',
            'DELL': 'Dell'
        }

        dotcom_stocks = {}
        for ticker, name in tech_stocks.items():
            print(f"  - {name} ({ticker}) 수집 중...")
            data = self.get_stock_data(ticker, self.dotcom_start, self.dotcom_end)
            if data is not None:
                dotcom_stocks[ticker] = data
                data.to_csv(f'bubble_analysis/data/{ticker}_dotcom.csv')
                print(f"    완료: {len(data)} 레코드")

        return dotcom_stocks

    def get_tech_stocks_ai(self):
        """AI 붐 시기 주요 기술주 데이터 수집"""
        print("\nAI 붐 시기 주요 기술주 데이터 수집 중...")

        ai_stocks = {
            'NVDA': 'Nvidia',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'META': 'Meta',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla'
        }

        ai_tech_stocks = {}
        for ticker, name in ai_stocks.items():
            print(f"  - {name} ({ticker}) 수집 중...")
            data = self.get_stock_data(ticker, self.ai_start, self.ai_end)
            if data is not None:
                ai_tech_stocks[ticker] = data
                data.to_csv(f'bubble_analysis/data/{ticker}_ai.csv')
                print(f"    완료: {len(data)} 레코드")

        return ai_tech_stocks

    def get_treasury_yield(self):
        """미국 국채 수익률 데이터 수집 (금리 대용)"""
        print("\n미국 국채 수익률 데이터 수집 중...")

        # 10년물 국채 수익률을 금리 지표로 사용
        tnx_dotcom = self.get_stock_data("^TNX", self.dotcom_start, self.dotcom_end)
        if tnx_dotcom is not None:
            tnx_dotcom.to_csv('bubble_analysis/data/treasury_yield_dotcom.csv')
            print(f"  - 닷컴 시기: {len(tnx_dotcom)} 레코드 수집 완료")

        tnx_ai = self.get_stock_data("^TNX", self.ai_start, self.ai_end)
        if tnx_ai is not None:
            tnx_ai.to_csv('bubble_analysis/data/treasury_yield_ai.csv')
            print(f"  - AI 시기: {len(tnx_ai)} 레코드 수집 완료")

        return tnx_dotcom, tnx_ai

    def create_economic_indicators_manual(self):
        """
        주요 경제 지표를 수동으로 입력 (FRED API 없이)
        공개된 역사적 데이터를 기반으로 생성
        """
        print("\n경제 지표 데이터 생성 중...")

        # 닷컴 버블 시기 경제 지표 (연간 데이터)
        dotcom_indicators = {
            'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
            'GDP_Growth': [2.7, 3.8, 4.4, 4.5, 4.8, 4.1, 1.0, 1.8, 2.9],  # 실질 GDP 성장률 (%)
            'Unemployment': [5.6, 5.4, 4.9, 4.5, 4.2, 4.0, 4.7, 5.8, 6.0],  # 실업률 (%)
            'CPI_Inflation': [2.8, 3.0, 2.3, 1.6, 2.2, 3.4, 2.8, 1.6, 2.3],  # CPI 인플레이션 (%)
            'Fed_Funds_Rate': [5.5, 5.3, 5.5, 5.4, 5.0, 6.2, 3.9, 1.7, 1.1],  # 연방기금금리 (%)
            'M1_Growth': [0.9, -1.6, 0.3, 1.5, 2.1, -2.6, 8.7, 8.1, 7.0],  # M1 통화량 증가율 (%)
        }

        # AI 붐 시기 경제 지표 (연간 데이터)
        ai_indicators = {
            'Year': [2020, 2021, 2022, 2023, 2024, 2025],
            'GDP_Growth': [-2.2, 5.8, 1.9, 2.5, 2.8, 2.3],  # 실질 GDP 성장률 (%) - 2024, 2025는 추정
            'Unemployment': [8.1, 5.4, 3.6, 3.6, 4.0, 4.3],  # 실업률 (%) - 2024, 2025는 추정
            'CPI_Inflation': [1.2, 4.7, 8.0, 4.1, 3.4, 2.8],  # CPI 인플레이션 (%) - 2024, 2025는 추정
            'Fed_Funds_Rate': [0.4, 0.1, 1.7, 5.1, 5.3, 4.5],  # 연방기금금리 (%) - 2024, 2025는 추정
            'M1_Growth': [23.6, 14.2, -5.1, -2.3, 0.5, 1.2],  # M1 통화량 증가율 (%) - 2024, 2025는 추정
        }

        # 국가 부채 대 GDP 비율
        debt_to_gdp = {
            'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                     2020, 2021, 2022, 2023, 2024, 2025],
            'Debt_to_GDP': [66.0, 65.0, 63.0, 60.0, 57.0, 54.0, 54.0, 56.0, 59.0,
                           106.0, 122.0, 120.0, 119.0, 122.0, 124.0],  # % - 2024, 2025는 추정
        }

        # DataFrame 생성 및 저장
        df_dotcom = pd.DataFrame(dotcom_indicators)
        df_ai = pd.DataFrame(ai_indicators)
        df_debt = pd.DataFrame(debt_to_gdp)

        df_dotcom.to_csv('bubble_analysis/data/economic_indicators_dotcom.csv', index=False)
        df_ai.to_csv('bubble_analysis/data/economic_indicators_ai.csv', index=False)
        df_debt.to_csv('bubble_analysis/data/debt_to_gdp.csv', index=False)

        print("  - 경제 지표 데이터 생성 완료")

        return df_dotcom, df_ai, df_debt

    def calculate_pe_ratios(self):
        """P/E 비율 계산 (역사적 추정치)"""
        print("\nP/E 비율 데이터 생성 중...")

        # 닷컴 버블 시기 NASDAQ P/E
        dotcom_pe = {
            'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
            'NASDAQ_PE': [25, 30, 35, 45, 80, 120, 60, 40, 35],  # 추정치
            'SP500_PE': [18, 20, 22, 28, 30, 26, 22, 20, 21],  # 추정치
        }

        # AI 붐 시기 P/E
        ai_pe = {
            'Year': [2020, 2021, 2022, 2023, 2024, 2025],
            'NASDAQ_PE': [35, 40, 25, 30, 35, 32],  # 추정치
            'SP500_PE': [22, 26, 18, 21, 23, 22],  # 추정치
            'Mag7_PE': [40, 50, 30, 40, 45, 42],  # Magnificent 7 평균 P/E 추정치
        }

        df_dotcom_pe = pd.DataFrame(dotcom_pe)
        df_ai_pe = pd.DataFrame(ai_pe)

        df_dotcom_pe.to_csv('bubble_analysis/data/pe_ratios_dotcom.csv', index=False)
        df_ai_pe.to_csv('bubble_analysis/data/pe_ratios_ai.csv', index=False)

        print("  - P/E 비율 데이터 생성 완료")

        return df_dotcom_pe, df_ai_pe

    def collect_all_data(self):
        """모든 데이터 수집 실행"""
        print("=" * 60)
        print("닷컴 버블 vs AI 붐 경제 데이터 수집 시작")
        print("=" * 60)

        # 주가 데이터
        self.get_nasdaq_data()
        self.get_tech_stocks_dotcom()
        self.get_tech_stocks_ai()

        # 금리 데이터
        self.get_treasury_yield()

        # 경제 지표
        self.create_economic_indicators_manual()

        # P/E 비율
        self.calculate_pe_ratios()

        print("\n" + "=" * 60)
        print("모든 데이터 수집 완료!")
        print("=" * 60)


if __name__ == "__main__":
    collector = EconomicDataCollector()
    collector.collect_all_data()
