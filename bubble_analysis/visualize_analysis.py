"""
닷컴 버블과 AI 붐 비교 분석을 위한 시각화 스크립트
다양한 차트와 그래프를 생성하여 비교 분석합니다.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import seaborn as sns
from datetime import datetime
import os

# 한글 폰트 설정 (한글 깨짐 방지)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# 시각화 스타일 설정
sns.set_style("whitegrid")
sns.set_palette("husl")

class BubbleAnalysisVisualizer:
    """버블 분석 시각화 클래스"""

    def __init__(self, data_dir='bubble_analysis/data', output_dir='bubble_analysis/visualizations'):
        self.data_dir = data_dir
        self.output_dir = output_dir

        # 데이터 로드
        self.load_data()

    def load_data(self):
        """모든 데이터 파일 로드"""
        print("데이터 로드 중...")

        # NASDAQ 지수
        self.nasdaq_dotcom = pd.read_csv(f'{self.data_dir}/nasdaq_dotcom.csv', index_col=0, parse_dates=True)
        self.nasdaq_ai = pd.read_csv(f'{self.data_dir}/nasdaq_ai.csv', index_col=0, parse_dates=True)

        # 경제 지표
        self.econ_dotcom = pd.read_csv(f'{self.data_dir}/economic_indicators_dotcom.csv')
        self.econ_ai = pd.read_csv(f'{self.data_dir}/economic_indicators_ai.csv')
        self.debt_gdp = pd.read_csv(f'{self.data_dir}/debt_to_gdp.csv')
        self.pe_dotcom = pd.read_csv(f'{self.data_dir}/pe_ratios_dotcom.csv')
        self.pe_ai = pd.read_csv(f'{self.data_dir}/pe_ratios_ai.csv')

        # 기술주
        self.dotcom_stocks = {}
        for ticker in ['MSFT', 'CSCO', 'INTC', 'ORCL', 'DELL']:
            self.dotcom_stocks[ticker] = pd.read_csv(
                f'{self.data_dir}/{ticker}_dotcom.csv', index_col=0, parse_dates=True
            )

        self.ai_stocks = {}
        for ticker in ['NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN', 'TSLA']:
            self.ai_stocks[ticker] = pd.read_csv(
                f'{self.data_dir}/{ticker}_ai.csv', index_col=0, parse_dates=True
            )

        print("데이터 로드 완료!")

    def plot_nasdaq_comparison(self):
        """NASDAQ 지수 비교 차트"""
        print("\n1. NASDAQ 지수 비교 차트 생성 중...")

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

        # 닷컴 버블 시기
        nasdaq_dotcom_normalized = (self.nasdaq_dotcom['Close'] / self.nasdaq_dotcom['Close'].iloc[0]) * 100
        ax1.plot(nasdaq_dotcom_normalized.index, nasdaq_dotcom_normalized.values,
                linewidth=2, color='#e74c3c', label='Dotcom Bubble (1995-2003)')
        ax1.axvline(pd.Timestamp('2000-03-01'), color='red', linestyle='--', alpha=0.7, label='Peak (Mar 2000)')
        ax1.axvline(pd.Timestamp('2002-10-01'), color='green', linestyle='--', alpha=0.7, label='Bottom (Oct 2002)')
        ax1.set_title('NASDAQ Index - Dotcom Bubble Era (Normalized to 100)', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=11)
        ax1.set_ylabel('Index (Base=100)', fontsize=11)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)

        # AI 붐 시기
        nasdaq_ai_normalized = (self.nasdaq_ai['Close'] / self.nasdaq_ai['Close'].iloc[0]) * 100
        ax2.plot(nasdaq_ai_normalized.index, nasdaq_ai_normalized.values,
                linewidth=2, color='#3498db', label='AI Boom (2020-2025)')
        ax2.axvline(pd.Timestamp('2020-03-01'), color='orange', linestyle='--', alpha=0.7, label='COVID Crash (Mar 2020)')
        ax2.axvline(pd.Timestamp('2021-11-01'), color='red', linestyle='--', alpha=0.7, label='Peak (Nov 2021)')
        ax2.set_title('NASDAQ Index - AI Boom Era (Normalized to 100)', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=11)
        ax2.set_ylabel('Index (Base=100)', fontsize=11)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/nasdaq_comparison.png', dpi=300, bbox_inches='tight')
        print("   -> nasdaq_comparison.png 저장 완료")
        plt.close()

    def plot_nasdaq_overlay(self):
        """NASDAQ 지수 중첩 비교 (정규화)"""
        print("\n2. NASDAQ 지수 중첩 비교 차트 생성 중...")

        fig, ax = plt.subplots(figsize=(14, 8))

        # 닷컴 버블 정규화 (버블 시작부터의 개월 수)
        dotcom_months = range(len(self.nasdaq_dotcom))
        dotcom_normalized = (self.nasdaq_dotcom['Close'] / self.nasdaq_dotcom['Close'].iloc[0]) * 100

        # AI 붐 정규화
        ai_months = range(len(self.nasdaq_ai))
        ai_normalized = (self.nasdaq_ai['Close'] / self.nasdaq_ai['Close'].iloc[0]) * 100

        ax.plot(dotcom_months, dotcom_normalized.values, linewidth=2.5,
               color='#e74c3c', label='Dotcom Bubble (1995-2003)', alpha=0.8)
        ax.plot(ai_months, ai_normalized.values, linewidth=2.5,
               color='#3498db', label='AI Boom (2020-2025)', alpha=0.8)

        ax.set_title('NASDAQ Index Comparison: Dotcom vs AI Boom (Normalized)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Months from Start', fontsize=12)
        ax.set_ylabel('Index (Base=100)', fontsize=12)
        ax.legend(fontsize=11, loc='upper left')
        ax.grid(True, alpha=0.3)

        # 주요 포인트 표시
        ax.axhline(y=100, color='gray', linestyle=':', alpha=0.5)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/nasdaq_overlay.png', dpi=300, bbox_inches='tight')
        print("   -> nasdaq_overlay.png 저장 완료")
        plt.close()

    def plot_tech_stocks_dotcom(self):
        """닷컴 시기 주요 기술주 비교"""
        print("\n3. 닷컴 시기 기술주 비교 차트 생성 중...")

        fig, ax = plt.subplots(figsize=(14, 8))

        colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        for i, (ticker, data) in enumerate(self.dotcom_stocks.items()):
            normalized = (data['Close'] / data['Close'].iloc[0]) * 100
            ax.plot(data.index, normalized.values, linewidth=2,
                   color=colors[i], label=ticker, alpha=0.8)

        ax.set_title('Dotcom Era Tech Stocks (Normalized to 100)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Stock Price (Base=100)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axvline(pd.Timestamp('2000-03-01'), color='red', linestyle='--', alpha=0.5, label='Bubble Peak')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/tech_stocks_dotcom.png', dpi=300, bbox_inches='tight')
        print("   -> tech_stocks_dotcom.png 저장 완료")
        plt.close()

    def plot_tech_stocks_ai(self):
        """AI 붐 시기 주요 기술주 비교"""
        print("\n4. AI 붐 시기 기술주 비교 차트 생성 중...")

        fig, ax = plt.subplots(figsize=(14, 8))

        colors = ['#76b900', '#3498db', '#e74c3c', '#1abc9c', '#f39c12', '#9b59b6']
        for i, (ticker, data) in enumerate(self.ai_stocks.items()):
            normalized = (data['Close'] / data['Close'].iloc[0]) * 100
            ax.plot(data.index, normalized.values, linewidth=2,
                   color=colors[i], label=ticker, alpha=0.8)

        ax.set_title('AI Boom Era Tech Stocks (Normalized to 100)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Stock Price (Base=100)', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.axvline(pd.Timestamp('2023-01-01'), color='green', linestyle='--', alpha=0.5, label='AI Boom Start')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/tech_stocks_ai.png', dpi=300, bbox_inches='tight')
        print("   -> tech_stocks_ai.png 저장 완료")
        plt.close()

    def plot_economic_indicators(self):
        """거시경제 지표 비교"""
        print("\n5. 거시경제 지표 비교 차트 생성 중...")

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle('Macroeconomic Indicators: Dotcom vs AI Boom', fontsize=16, fontweight='bold')

        # GDP 성장률
        ax = axes[0, 0]
        ax.plot(self.econ_dotcom['Year'], self.econ_dotcom['GDP_Growth'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(self.econ_ai['Year'], self.econ_ai['GDP_Growth'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('GDP Growth Rate (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Growth Rate (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        # 실업률
        ax = axes[0, 1]
        ax.plot(self.econ_dotcom['Year'], self.econ_dotcom['Unemployment'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(self.econ_ai['Year'], self.econ_ai['Unemployment'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('Unemployment Rate (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Unemployment (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # CPI 인플레이션
        ax = axes[0, 2]
        ax.plot(self.econ_dotcom['Year'], self.econ_dotcom['CPI_Inflation'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(self.econ_ai['Year'], self.econ_ai['CPI_Inflation'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('CPI Inflation (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Inflation (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=2, color='green', linestyle='--', alpha=0.5, linewidth=1)

        # 연방기금금리
        ax = axes[1, 0]
        ax.plot(self.econ_dotcom['Year'], self.econ_dotcom['Fed_Funds_Rate'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(self.econ_ai['Year'], self.econ_ai['Fed_Funds_Rate'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('Federal Funds Rate (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Interest Rate (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # M1 통화량 증가율
        ax = axes[1, 1]
        ax.plot(self.econ_dotcom['Year'], self.econ_dotcom['M1_Growth'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(self.econ_ai['Year'], self.econ_ai['M1_Growth'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('M1 Money Supply Growth (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('M1 Growth (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        # 국가 부채 대 GDP 비율
        ax = axes[1, 2]
        dotcom_debt = self.debt_gdp[self.debt_gdp['Year'] <= 2003]
        ai_debt = self.debt_gdp[self.debt_gdp['Year'] >= 2020]
        ax.plot(dotcom_debt['Year'], dotcom_debt['Debt_to_GDP'],
               marker='o', linewidth=2, color='#e74c3c', label='Dotcom Era')
        ax.plot(ai_debt['Year'], ai_debt['Debt_to_GDP'],
               marker='s', linewidth=2, color='#3498db', label='AI Era')
        ax.set_title('National Debt to GDP Ratio (%)', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Debt/GDP (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/economic_indicators.png', dpi=300, bbox_inches='tight')
        print("   -> economic_indicators.png 저장 완료")
        plt.close()

    def plot_pe_ratios(self):
        """P/E 비율 비교"""
        print("\n6. P/E 비율 비교 차트 생성 중...")

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        # 닷컴 시기 P/E
        ax1.plot(self.pe_dotcom['Year'], self.pe_dotcom['NASDAQ_PE'],
                marker='o', linewidth=2.5, color='#e74c3c', label='NASDAQ')
        ax1.plot(self.pe_dotcom['Year'], self.pe_dotcom['SP500_PE'],
                marker='s', linewidth=2.5, color='#3498db', label='S&P 500')
        ax1.set_title('P/E Ratios - Dotcom Era', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=11)
        ax1.set_ylabel('P/E Ratio', fontsize=11)
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=30, color='orange', linestyle='--', alpha=0.5, label='High Valuation')

        # AI 붐 시기 P/E
        ax2.plot(self.pe_ai['Year'], self.pe_ai['NASDAQ_PE'],
                marker='o', linewidth=2.5, color='#e74c3c', label='NASDAQ')
        ax2.plot(self.pe_ai['Year'], self.pe_ai['SP500_PE'],
                marker='s', linewidth=2.5, color='#3498db', label='S&P 500')
        ax2.plot(self.pe_ai['Year'], self.pe_ai['Mag7_PE'],
                marker='^', linewidth=2.5, color='#2ecc71', label='Magnificent 7')
        ax2.set_title('P/E Ratios - AI Boom Era', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=11)
        ax2.set_ylabel('P/E Ratio', fontsize=11)
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=30, color='orange', linestyle='--', alpha=0.5, label='High Valuation')

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/pe_ratios.png', dpi=300, bbox_inches='tight')
        print("   -> pe_ratios.png 저장 완료")
        plt.close()

    def plot_bubble_comparison_matrix(self):
        """버블 특성 비교 매트릭스"""
        print("\n7. 버블 특성 비교 매트릭스 생성 중...")

        # 비교 지표 설정
        metrics = ['Peak P/E', 'Peak Growth', 'Max Drawdown', 'Volatility', 'Bubble Duration']

        dotcom_scores = [120, 400, -78, 85, 60]  # 닷컴 버블
        ai_scores = [45, 200, -35, 65, 40]  # AI 붐 (현재까지)

        x = np.arange(len(metrics))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 7))

        bars1 = ax.bar(x - width/2, dotcom_scores, width, label='Dotcom Bubble',
                      color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, ai_scores, width, label='AI Boom',
                      color='#3498db', alpha=0.8)

        ax.set_title('Bubble Characteristics Comparison', fontsize=16, fontweight='bold')
        ax.set_ylabel('Score / Value', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

        # 값 표시
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.0f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/bubble_comparison_matrix.png', dpi=300, bbox_inches='tight')
        print("   -> bubble_comparison_matrix.png 저장 완료")
        plt.close()

    def plot_risk_assessment_radar(self):
        """리스크 평가 레이더 차트"""
        print("\n8. 리스크 평가 레이더 차트 생성 중...")

        categories = ['Valuation Risk', 'Liquidity Risk', 'Macro Risk',
                     'Earnings Quality', 'Market Sentiment', 'Policy Risk']

        dotcom_values = [95, 40, 30, 25, 90, 50]
        ai_values = [60, 85, 75, 70, 70, 80]

        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        dotcom_values += dotcom_values[:1]
        ai_values += ai_values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        ax.plot(angles, dotcom_values, 'o-', linewidth=2, label='Dotcom Bubble',
               color='#e74c3c', alpha=0.7)
        ax.fill(angles, dotcom_values, alpha=0.25, color='#e74c3c')

        ax.plot(angles, ai_values, 'o-', linewidth=2, label='AI Boom',
               color='#3498db', alpha=0.7)
        ax.fill(angles, ai_values, alpha=0.25, color='#3498db')

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.set_title('Risk Assessment: Dotcom vs AI Boom', fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/risk_assessment_radar.png', dpi=300, bbox_inches='tight')
        print("   -> risk_assessment_radar.png 저장 완료")
        plt.close()

    def create_all_visualizations(self):
        """모든 시각화 생성"""
        print("=" * 60)
        print("버블 분석 시각화 시작")
        print("=" * 60)

        self.plot_nasdaq_comparison()
        self.plot_nasdaq_overlay()
        self.plot_tech_stocks_dotcom()
        self.plot_tech_stocks_ai()
        self.plot_economic_indicators()
        self.plot_pe_ratios()
        self.plot_bubble_comparison_matrix()
        self.plot_risk_assessment_radar()

        print("\n" + "=" * 60)
        print("모든 시각화 생성 완료!")
        print("=" * 60)


if __name__ == "__main__":
    visualizer = BubbleAnalysisVisualizer()
    visualizer.create_all_visualizations()
