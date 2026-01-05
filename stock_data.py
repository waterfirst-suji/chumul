"""
주가 데이터 수집 모듈
yfinance를 사용하여 실시간 주가 데이터를 가져옵니다.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


class StockDataFetcher:
    """주가 데이터를 가져오는 클래스"""

    def __init__(self, ticker: str):
        """
        Args:
            ticker: 주식 티커 심볼 (예: 'NVDA', 'AAPL', 'TSLA')
        """
        self.ticker = ticker.upper()

    def get_historical_data(self, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
        """
        과거 주가 데이터를 가져옵니다.
        yf.download()를 직접 사용합니다.

        Args:
            period: 데이터 기간 ('1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval: 데이터 간격 ('1d', '1h', '1wk', '1mo')

        Returns:
            주가 데이터가 담긴 DataFrame
        """
        # yf.download() 직접 사용 - 가장 안정적
        df = yf.download(self.ticker, period=period, interval=interval, progress=False)

        if df.empty:
            raise ValueError(f"'{self.ticker}' 티커에 대한 데이터를 찾을 수 없습니다.")

        # 인덱스를 날짜 컬럼으로 변환
        df.reset_index(inplace=True)

        return df

    def get_stock_info(self) -> dict:
        """
        주식 기본 정보를 가져옵니다.

        Returns:
            주식 정보 딕셔너리
        """
        try:
            ticker_obj = yf.Ticker(self.ticker)
            info = ticker_obj.info

            # 현재 가격 가져오기
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))

            # 현재 가격이 없으면 최근 데이터에서 가져오기
            if current_price == 'N/A':
                try:
                    df = yf.download(self.ticker, period='1d', progress=False)
                    if not df.empty:
                        current_price = float(df['Close'].iloc[-1])
                except:
                    pass

            return {
                'name': info.get('longName', self.ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'current_price': current_price,
            }
        except Exception as e:
            return {
                'name': self.ticker,
                'sector': 'N/A',
                'industry': 'N/A',
                'market_cap': 'N/A',
                'current_price': 'N/A',
            }

    def validate_ticker(self) -> bool:
        """
        티커 심볼이 유효한지 검증합니다.

        Returns:
            유효하면 True, 아니면 False
        """
        try:
            df = yf.download(self.ticker, period='5d', progress=False)
            return not df.empty
        except:
            return True  # 에러 시 True 반환 (실제 데이터 수집 시 재확인)


def get_available_tickers() -> list:
    """
    자주 사용되는 주요 기술주 티커 목록을 반환합니다.

    Returns:
        티커 심볼 리스트
    """
    return [
        'NVDA',   # Nvidia
        'AAPL',   # Apple
        'MSFT',   # Microsoft
        'GOOGL',  # Google
        'AMZN',   # Amazon
        'TSLA',   # Tesla
        'META',   # Meta
        'AMD',    # AMD
        'INTC',   # Intel
        'NFLX',   # Netflix
        'CSCO',   # Cisco
        'ADBE',   # Adobe
        'CRM',    # Salesforce
        'ORCL',   # Oracle
        'IBM',    # IBM
        # 한국 주식
        '005930.KS',  # 삼성전자
        '000660.KS',  # SK하이닉스
        '035420.KS',  # 네이버
        '035720.KS',  # 카카오
    ]
