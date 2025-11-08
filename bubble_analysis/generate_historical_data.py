"""
역사적 데이터를 기반으로 주가 및 경제 지표 데이터를 생성합니다.
실제 역사적 추세를 반영하여 분석 가능한 데이터를 생성합니다.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_nasdaq_dotcom():
    """닷컴 버블 시기 NASDAQ 지수 데이터 생성 (1995-2003)"""

    # 실제 NASDAQ 지수의 주요 포인트 (역사적 데이터)
    dates = pd.date_range('1995-01-01', '2003-12-31', freq='M')

    # 1995: ~1,000 -> 2000년 3월: ~5,000 -> 2002년 10월: ~1,100
    key_points = {
        '1995-01-01': 755,
        '1996-01-01': 1059,
        '1997-01-01': 1291,
        '1998-01-01': 1570,
        '1999-01-01': 2193,
        '2000-03-01': 5048,  # 버블 정점
        '2000-12-01': 2471,
        '2001-12-01': 1950,
        '2002-10-01': 1114,  # 저점
        '2003-12-01': 2003
    }

    # 선형 보간으로 월별 데이터 생성
    index_values = []
    date_list = [datetime.strptime(d, '%Y-%m-%d') for d in key_points.keys()]
    value_list = list(key_points.values())

    for date in dates:
        # 가장 가까운 두 키포인트 사이에서 보간
        if date <= date_list[0]:
            value = value_list[0]
        elif date >= date_list[-1]:
            value = value_list[-1]
        else:
            for i in range(len(date_list) - 1):
                if date_list[i] <= date < date_list[i+1]:
                    # 선형 보간
                    days_total = (date_list[i+1] - date_list[i]).days
                    days_elapsed = (date - date_list[i]).days
                    ratio = days_elapsed / days_total
                    value = value_list[i] + (value_list[i+1] - value_list[i]) * ratio
                    break

        # 일일 변동성 추가 (±2%)
        value = value * (1 + np.random.normal(0, 0.02))
        index_values.append(value)

    df = pd.DataFrame({
        'Date': dates,
        'Close': index_values,
        'Open': [v * 0.99 for v in index_values],
        'High': [v * 1.02 for v in index_values],
        'Low': [v * 0.98 for v in index_values],
        'Volume': np.random.randint(800000000, 1500000000, len(dates))
    })

    df.set_index('Date', inplace=True)
    return df

def generate_nasdaq_ai():
    """AI 붐 시기 NASDAQ 지수 데이터 생성 (2020-2025)"""

    dates = pd.date_range('2020-01-01', '2025-11-08', freq='M')

    # 실제 NASDAQ 지수의 주요 포인트
    key_points = {
        '2020-01-01': 9150,
        '2020-03-01': 7417,  # COVID 하락
        '2020-12-01': 12888,
        '2021-11-01': 16057,  # 정점
        '2022-12-01': 10466,  # 금리 인상 하락
        '2023-01-01': 11467,
        '2024-01-01': 14765,
        '2024-07-01': 17599,
        '2025-11-01': 18500  # 추정
    }

    index_values = []
    date_list = [datetime.strptime(d, '%Y-%m-%d') for d in key_points.keys()]
    value_list = list(key_points.values())

    for date in dates:
        if date <= date_list[0]:
            value = value_list[0]
        elif date >= date_list[-1]:
            value = value_list[-1]
        else:
            for i in range(len(date_list) - 1):
                if date_list[i] <= date < date_list[i+1]:
                    days_total = (date_list[i+1] - date_list[i]).days
                    days_elapsed = (date - date_list[i]).days
                    ratio = days_elapsed / days_total
                    value = value_list[i] + (value_list[i+1] - value_list[i]) * ratio
                    break

        value = value * (1 + np.random.normal(0, 0.02))
        index_values.append(value)

    df = pd.DataFrame({
        'Date': dates,
        'Close': index_values,
        'Open': [v * 0.99 for v in index_values],
        'High': [v * 1.02 for v in index_values],
        'Low': [v * 0.98 for v in index_values],
        'Volume': np.random.randint(3000000000, 5000000000, len(dates))
    })

    df.set_index('Date', inplace=True)
    return df

def generate_tech_stock_dotcom(ticker):
    """닷컴 시기 개별 기술주 데이터 생성"""

    dates = pd.date_range('1995-01-01', '2003-12-31', freq='M')

    # 각 종목별 특성
    stock_profiles = {
        'MSFT': {'start': 8, 'peak': 58, 'bottom': 21, 'end': 27},
        'CSCO': {'start': 2, 'peak': 80, 'bottom': 8, 'end': 23},
        'INTC': {'start': 7, 'peak': 75, 'bottom': 13, 'end': 32},
        'ORCL': {'start': 5, 'peak': 46, 'bottom': 9, 'end': 12},
        'DELL': {'start': 2, 'peak': 59, 'bottom': 17, 'end': 35}
    }

    profile = stock_profiles.get(ticker, {'start': 10, 'peak': 100, 'bottom': 20, 'end': 40})

    # 시계열 생성
    n = len(dates)
    prices = []
    for i, date in enumerate(dates):
        if date.year < 1999:
            # 초기 상승 (1995-1998)
            ratio = (date.year - 1995 + date.month/12) / 4
            price = profile['start'] + (profile['peak'] * 0.4 - profile['start']) * ratio
        elif date.year == 1999:
            # 급격한 상승 (1999)
            ratio = date.month / 12
            price = profile['peak'] * 0.4 + (profile['peak'] - profile['peak'] * 0.4) * ratio
        elif date.year == 2000:
            # 정점 후 하락 (2000)
            ratio = date.month / 12
            price = profile['peak'] - (profile['peak'] - profile['bottom']) * ratio * 0.5
        elif date.year <= 2002:
            # 지속적 하락 (2001-2002)
            ratio = (date.year - 2000 + date.month/12) / 3
            price = profile['peak'] * 0.5 - (profile['peak'] * 0.5 - profile['bottom']) * ratio
        else:
            # 회복 (2003)
            ratio = date.month / 12
            price = profile['bottom'] + (profile['end'] - profile['bottom']) * ratio

        price = price * (1 + np.random.normal(0, 0.03))
        prices.append(max(price, 1))

    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': [p * 0.98 for p in prices],
        'High': [p * 1.04 for p in prices],
        'Low': [p * 0.96 for p in prices],
        'Volume': np.random.randint(10000000, 50000000, len(dates))
    })

    df.set_index('Date', inplace=True)
    return df

def generate_tech_stock_ai(ticker):
    """AI 붐 시기 개별 기술주 데이터 생성"""

    dates = pd.date_range('2020-01-01', '2025-11-08', freq='M')

    # 각 종목별 특성
    stock_profiles = {
        'NVDA': {'start': 60, 'covid_low': 50, 'mid': 200, 'peak': 950},
        'MSFT': {'start': 160, 'covid_low': 140, 'mid': 280, 'peak': 430},
        'GOOGL': {'start': 68, 'covid_low': 55, 'mid': 100, 'peak': 155},
        'META': {'start': 210, 'covid_low': 145, 'mid': 190, 'peak': 500},
        'AMZN': {'start': 93, 'covid_low': 81, 'mid': 120, 'peak': 180},
        'TSLA': {'start': 30, 'covid_low': 22, 'mid': 700, 'peak': 410}
    }

    profile = stock_profiles.get(ticker, {'start': 100, 'covid_low': 80, 'mid': 200, 'peak': 400})

    prices = []
    for date in dates:
        if date.year == 2020 and date.month <= 3:
            # COVID 하락
            ratio = date.month / 3
            price = profile['start'] - (profile['start'] - profile['covid_low']) * ratio
        elif date.year == 2020:
            # COVID 회복
            ratio = (date.month - 3) / 9
            price = profile['covid_low'] + (profile['mid'] - profile['covid_low']) * ratio
        elif date.year <= 2021:
            # 2021 상승
            ratio = (date.year - 2020 + date.month/12) / 2
            price = profile['mid'] + (profile['mid'] * 1.3 - profile['mid']) * ratio
        elif date.year == 2022:
            # 2022 하락 (금리 인상)
            ratio = date.month / 12
            price = profile['mid'] * 1.3 - (profile['mid'] * 1.3 - profile['mid'] * 0.7) * ratio
        elif date.year == 2023:
            # 2023 AI 붐 시작
            ratio = date.month / 12
            if ticker == 'NVDA':
                price = profile['mid'] * 0.7 + (profile['mid'] * 1.5 - profile['mid'] * 0.7) * ratio
            else:
                price = profile['mid'] * 0.7 + (profile['mid'] * 1.2 - profile['mid'] * 0.7) * ratio
        else:
            # 2024-2025 지속적 상승
            ratio = (date.year - 2023 + date.month/12) / 2.9
            price = profile['mid'] * (1.5 if ticker == 'NVDA' else 1.2) + \
                    (profile['peak'] - profile['mid'] * (1.5 if ticker == 'NVDA' else 1.2)) * ratio

        price = price * (1 + np.random.normal(0, 0.04))
        prices.append(max(price, 1))

    df = pd.DataFrame({
        'Date': dates,
        'Close': prices,
        'Open': [p * 0.99 for p in prices],
        'High': [p * 1.03 for p in prices],
        'Low': [p * 0.97 for p in prices],
        'Volume': np.random.randint(20000000, 100000000, len(dates))
    })

    df.set_index('Date', inplace=True)
    return df

def create_economic_indicators():
    """경제 지표 데이터 생성"""

    # 닷컴 버블 시기 경제 지표 (연간 데이터)
    dotcom_indicators = {
        'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
        'GDP_Growth': [2.7, 3.8, 4.4, 4.5, 4.8, 4.1, 1.0, 1.8, 2.9],
        'Unemployment': [5.6, 5.4, 4.9, 4.5, 4.2, 4.0, 4.7, 5.8, 6.0],
        'CPI_Inflation': [2.8, 3.0, 2.3, 1.6, 2.2, 3.4, 2.8, 1.6, 2.3],
        'Fed_Funds_Rate': [5.5, 5.3, 5.5, 5.4, 5.0, 6.2, 3.9, 1.7, 1.1],
        'M1_Growth': [0.9, -1.6, 0.3, 1.5, 2.1, -2.6, 8.7, 8.1, 7.0],
    }

    # AI 붐 시기 경제 지표 (연간 데이터)
    ai_indicators = {
        'Year': [2020, 2021, 2022, 2023, 2024, 2025],
        'GDP_Growth': [-2.2, 5.8, 1.9, 2.5, 2.8, 2.3],
        'Unemployment': [8.1, 5.4, 3.6, 3.6, 4.0, 4.3],
        'CPI_Inflation': [1.2, 4.7, 8.0, 4.1, 3.4, 2.8],
        'Fed_Funds_Rate': [0.4, 0.1, 1.7, 5.1, 5.3, 4.5],
        'M1_Growth': [23.6, 14.2, -5.1, -2.3, 0.5, 1.2],
    }

    # 국가 부채 대 GDP 비율
    debt_to_gdp = {
        'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                 2020, 2021, 2022, 2023, 2024, 2025],
        'Debt_to_GDP': [66.0, 65.0, 63.0, 60.0, 57.0, 54.0, 54.0, 56.0, 59.0,
                       106.0, 122.0, 120.0, 119.0, 122.0, 124.0],
    }

    # P/E 비율
    dotcom_pe = {
        'Year': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003],
        'NASDAQ_PE': [25, 30, 35, 45, 80, 120, 60, 40, 35],
        'SP500_PE': [18, 20, 22, 28, 30, 26, 22, 20, 21],
    }

    ai_pe = {
        'Year': [2020, 2021, 2022, 2023, 2024, 2025],
        'NASDAQ_PE': [35, 40, 25, 30, 35, 32],
        'SP500_PE': [22, 26, 18, 21, 23, 22],
        'Mag7_PE': [40, 50, 30, 40, 45, 42],
    }

    return (pd.DataFrame(dotcom_indicators), pd.DataFrame(ai_indicators),
            pd.DataFrame(debt_to_gdp), pd.DataFrame(dotcom_pe), pd.DataFrame(ai_pe))

def main():
    """모든 데이터 생성 및 저장"""
    print("=" * 60)
    print("역사적 데이터 생성 시작")
    print("=" * 60)

    # NASDAQ 지수
    print("\nNASDAQ 지수 데이터 생성 중...")
    nasdaq_dotcom = generate_nasdaq_dotcom()
    nasdaq_ai = generate_nasdaq_ai()
    nasdaq_dotcom.to_csv('bubble_analysis/data/nasdaq_dotcom.csv')
    nasdaq_ai.to_csv('bubble_analysis/data/nasdaq_ai.csv')
    print(f"  - 닷컴 시기: {len(nasdaq_dotcom)} 레코드 생성 완료")
    print(f"  - AI 시기: {len(nasdaq_ai)} 레코드 생성 완료")

    # 닷컴 시기 기술주
    print("\n닷컴 버블 시기 기술주 데이터 생성 중...")
    dotcom_tickers = ['MSFT', 'CSCO', 'INTC', 'ORCL', 'DELL']
    for ticker in dotcom_tickers:
        df = generate_tech_stock_dotcom(ticker)
        df.to_csv(f'bubble_analysis/data/{ticker}_dotcom.csv')
        print(f"  - {ticker}: {len(df)} 레코드 생성 완료")

    # AI 붐 시기 기술주
    print("\nAI 붐 시기 기술주 데이터 생성 중...")
    ai_tickers = ['NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'TSLA']
    for ticker in ai_tickers:
        df = generate_tech_stock_ai(ticker)
        df.to_csv(f'bubble_analysis/data/{ticker}_ai.csv')
        print(f"  - {ticker}: {len(df)} 레코드 생성 완료")

    # 경제 지표
    print("\n경제 지표 데이터 생성 중...")
    dotcom_ind, ai_ind, debt, dotcom_pe, ai_pe = create_economic_indicators()
    dotcom_ind.to_csv('bubble_analysis/data/economic_indicators_dotcom.csv', index=False)
    ai_ind.to_csv('bubble_analysis/data/economic_indicators_ai.csv', index=False)
    debt.to_csv('bubble_analysis/data/debt_to_gdp.csv', index=False)
    dotcom_pe.to_csv('bubble_analysis/data/pe_ratios_dotcom.csv', index=False)
    ai_pe.to_csv('bubble_analysis/data/pe_ratios_ai.csv', index=False)
    print("  - 모든 경제 지표 데이터 생성 완료")

    print("\n" + "=" * 60)
    print("모든 데이터 생성 완료!")
    print("=" * 60)

if __name__ == "__main__":
    main()
