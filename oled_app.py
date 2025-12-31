"""
OLED 2차 공진구조 각도 의존성 시뮬레이터 - Streamlit App
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from oled_cavity_simulator import (
    OLEDCavitySimulator,
    OLEDParams,
    create_rgb_oled_params
)


def plot_spectrum_at_angles(simulator, params, angles, color_name):
    """특정 각도들에서의 스펙트럼 플롯"""
    fig = go.Figure()

    # 색상 매핑
    color_map = {
        'red': 'rgba(255, 0, 0, {})',
        'green': 'rgba(0, 255, 0, {})',
        'blue': 'rgba(0, 0, 255, {})'
    }
    base_color = color_map.get(color_name.lower(), 'rgba(128, 128, 128, {})')

    for i, angle in enumerate(angles):
        wavelengths, intensities = simulator.simulate_spectrum_at_angle(
            params, angle, wavelength_range=(400, 700)
        )

        # 투명도 조절 (각도가 클수록 투명)
        alpha = 1.0 - (i / len(angles)) * 0.7

        fig.add_trace(go.Scatter(
            x=wavelengths,
            y=intensities,
            mode='lines',
            name=f'{angle}°',
            line=dict(color=base_color.format(alpha), width=2)
        ))

    fig.update_layout(
        title=f'{color_name.upper()} OLED 각도별 발광 스펙트럼',
        xaxis_title='파장 (nm)',
        yaxis_title='상대 강도',
        hovermode='x unified',
        height=500
    )

    return fig


def plot_peak_wavelength_shift(results_dict):
    """각도별 피크 파장 변화 플롯"""
    fig = go.Figure()

    color_map = {
        'red': 'red',
        'green': 'green',
        'blue': 'blue'
    }

    for color_name, results in results_dict.items():
        angles = results['angles']
        peak_wls = results['peak_wavelengths']

        fig.add_trace(go.Scatter(
            x=angles,
            y=peak_wls,
            mode='lines+markers',
            name=color_name.upper(),
            line=dict(color=color_map.get(color_name, 'gray'), width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title='각도에 따른 피크 파장 변화 (Blue Shift)',
        xaxis_title='관찰 각도 (degrees)',
        yaxis_title='피크 파장 (nm)',
        hovermode='x unified',
        height=500
    )

    return fig


def plot_intensity_change(results_dict):
    """각도별 강도 변화 플롯"""
    fig = go.Figure()

    color_map = {
        'red': 'red',
        'green': 'green',
        'blue': 'blue'
    }

    for color_name, results in results_dict.items():
        angles = results['angles']
        peak_intensities = results['peak_intensities']

        # 0도 대비 상대 강도로 정규화
        normalized_intensities = peak_intensities / peak_intensities[0]

        fig.add_trace(go.Scatter(
            x=angles,
            y=normalized_intensities,
            mode='lines+markers',
            name=color_name.upper(),
            line=dict(color=color_map.get(color_name, 'gray'), width=3),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title='각도에 따른 발광 강도 변화',
        xaxis_title='관찰 각도 (degrees)',
        yaxis_title='상대 강도 (0° = 1.0)',
        hovermode='x unified',
        height=500
    )

    return fig


def plot_2d_spectrum_map(simulator, params, color_name):
    """2D 스펙트럼 맵 (각도 vs 파장)"""
    angles = np.linspace(0, 60, 61)
    results = simulator.simulate_angular_dependence(params, angles)

    wavelengths = results['wavelength_axis']
    spectra = results['spectra']

    fig = go.Figure(data=go.Heatmap(
        z=spectra.T,
        x=angles,
        y=wavelengths,
        colorscale='Hot',
        colorbar=dict(title='상대 강도')
    ))

    fig.update_layout(
        title=f'{color_name.upper()} OLED 2D 스펙트럼 맵',
        xaxis_title='관찰 각도 (degrees)',
        yaxis_title='파장 (nm)',
        height=500
    )

    return fig


def plot_comparison_with_measured(results_dict, measured_data):
    """시뮬레이션과 실측 데이터 비교"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('피크 파장 비교', '강도 비교')
    )

    color_map = {
        'red': 'red',
        'green': 'green',
        'blue': 'blue'
    }

    for color_name, results in results_dict.items():
        if color_name not in measured_data:
            continue

        measured = measured_data[color_name]
        angles = results['angles']
        peak_wls = results['peak_wavelengths']
        peak_intensities = results['peak_intensities'] / results['peak_intensities'][0]

        # 시뮬레이션
        fig.add_trace(go.Scatter(
            x=angles,
            y=peak_wls,
            mode='lines',
            name=f'{color_name.upper()} (Sim)',
            line=dict(color=color_map[color_name], width=2),
            legendgroup=color_name
        ), row=1, col=1)

        # 실측
        fig.add_trace(go.Scatter(
            x=measured['angles'],
            y=measured['wavelengths'],
            mode='markers',
            name=f'{color_name.upper()} (Meas)',
            marker=dict(color=color_map[color_name], size=10, symbol='x'),
            legendgroup=color_name
        ), row=1, col=1)

        # 강도 - 시뮬레이션
        fig.add_trace(go.Scatter(
            x=angles,
            y=peak_intensities,
            mode='lines',
            name=f'{color_name.upper()} (Sim)',
            line=dict(color=color_map[color_name], width=2),
            legendgroup=color_name,
            showlegend=False
        ), row=1, col=2)

    fig.update_xaxes(title_text='각도 (degrees)', row=1, col=1)
    fig.update_xaxes(title_text='각도 (degrees)', row=1, col=2)
    fig.update_yaxes(title_text='파장 (nm)', row=1, col=1)
    fig.update_yaxes(title_text='상대 강도', row=1, col=2)

    fig.update_layout(height=500, hovermode='x unified')

    return fig


def main():
    st.set_page_config(
        page_title="OLED 공진구조 시뮬레이터",
        page_icon="🔬",
        layout="wide"
    )

    st.title("🔬 OLED 2차 공진구조 각도 의존성 시뮬레이터")

    st.markdown("""
    ### 물리적 원리

    OLED의 2차 공진구조에서 관찰 각도가 증가하면 발광 스펙트럼이 짧은 파장으로 이동(Blue Shift)하고
    강도가 감소하는 현상을 시뮬레이션합니다.

    **주요 원리:**
    1. **Fabry-Perot 공진 조건**: m × λ = 2 × n_eff × d × cos(θ)
    2. **Blue Shift 원인**: 각도 증가 → cos(θ) 감소 → 공진 파장(λ) 감소
    3. **강도 감소 원인**: Lambertian 발광 특성 (I ∝ cos(θ)) + 공진 조건 이탈
    """)

    # 사이드바 - 파라미터 설정
    st.sidebar.header("⚙️ 시뮬레이션 설정")

    # 실측 데이터
    measured_data = {
        'red': {
            'angles': np.array([0, 10, 20, 30, 40, 50, 60]),
            'wavelengths': np.array([625, 624, 623, 622, 621, 620.5, 620])
        },
        'green': {
            'angles': np.array([0, 10, 20, 30, 40, 50, 60]),
            'wavelengths': np.array([543, 540, 536, 532, 528, 525, 521])
        },
        'blue': {
            'angles': np.array([0, 10, 20, 30, 40, 50, 60]),
            'wavelengths': np.array([461, 460.7, 460.3, 460, 459.7, 459.3, 459])
        }
    }

    mode = st.sidebar.radio(
        "모드 선택",
        ["기본 시뮬레이션", "고급 설정", "실측 데이터 비교"]
    )

    simulator = OLEDCavitySimulator()

    if mode == "기본 시뮬레이션":
        st.header("📊 기본 시뮬레이션")

        # 기본 RGB 파라미터 사용
        rgb_params = create_rgb_oled_params()

        # 각도 범위 설정
        angle_step = st.sidebar.slider("각도 간격 (degrees)", 5, 15, 10)
        angles = np.arange(0, 61, angle_step)

        # 시뮬레이션 실행
        results_dict = {}
        for color_name, params in rgb_params.items():
            results = simulator.simulate_angular_dependence(params, angles)
            results_dict[color_name] = results

        # 탭으로 구분된 결과 표시
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 피크 파장 변화",
            "📉 강도 변화",
            "🌈 개별 스펙트럼",
            "🗺️ 2D 맵"
        ])

        with tab1:
            st.plotly_chart(plot_peak_wavelength_shift(results_dict), use_container_width=True)

            # 수치 데이터 표시
            st.subheader("수치 데이터")
            for color_name, results in results_dict.items():
                with st.expander(f"{color_name.upper()} OLED 상세 데이터"):
                    data = {
                        '각도 (°)': results['angles'],
                        '피크 파장 (nm)': np.round(results['peak_wavelengths'], 2),
                        '파장 변화 (nm)': np.round(
                            results['peak_wavelengths'] - results['peak_wavelengths'][0], 2
                        ),
                        '상대 강도': np.round(
                            results['peak_intensities'] / results['peak_intensities'][0], 3
                        )
                    }
                    st.dataframe(data, use_container_width=True)

        with tab2:
            st.plotly_chart(plot_intensity_change(results_dict), use_container_width=True)

        with tab3:
            color_choice = st.selectbox(
                "색상 선택",
                ["red", "green", "blue"],
                format_func=lambda x: x.upper()
            )

            display_angles = st.multiselect(
                "표시할 각도 선택",
                angles.tolist(),
                default=[0, 20, 40, 60]
            )

            if display_angles:
                fig = plot_spectrum_at_angles(
                    simulator,
                    rgb_params[color_choice],
                    display_angles,
                    color_choice
                )
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            color_choice_2d = st.selectbox(
                "2D 맵 색상 선택",
                ["red", "green", "blue"],
                format_func=lambda x: x.upper(),
                key='2d_color'
            )

            fig_2d = plot_2d_spectrum_map(
                simulator,
                rgb_params[color_choice_2d],
                color_choice_2d
            )
            st.plotly_chart(fig_2d, use_container_width=True)

    elif mode == "고급 설정":
        st.header("🔧 고급 설정")

        color_choice = st.sidebar.selectbox(
            "색상 선택",
            ["red", "green", "blue"],
            format_func=lambda x: x.upper()
        )

        st.sidebar.subheader("파라미터 조정")

        lambda_0 = st.sidebar.number_input(
            "중심 파장 (nm)",
            400.0, 700.0,
            625.0 if color_choice == 'red' else (543.0 if color_choice == 'green' else 461.0),
            1.0
        )

        n_eff = st.sidebar.slider(
            "유효 굴절률",
            1.5, 2.0, 1.8, 0.05
        )

        order = st.sidebar.selectbox(
            "공진 차수",
            [1, 2, 3],
            index=1
        )

        fwhm = st.sidebar.slider(
            "스펙트럼 폭 FWHM (nm)",
            10.0, 60.0, 30.0, 5.0
        )

        # 공진 길이 자동 계산
        cavity_length = simulator.calculate_cavity_length_from_wavelength(lambda_0, n_eff, order)

        st.sidebar.info(f"계산된 공진 길이: {cavity_length:.2f} nm")

        # 커스텀 파라미터 생성
        custom_params = OLEDParams(
            lambda_0=lambda_0,
            n_eff=n_eff,
            cavity_length=cavity_length,
            order=order,
            fwhm=fwhm,
            peak_intensity=1.0
        )

        angles = np.arange(0, 61, 10)
        results = simulator.simulate_angular_dependence(custom_params, angles)

        col1, col2 = st.columns(2)

        with col1:
            # 피크 파장 변화
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=results['angles'],
                y=results['peak_wavelengths'],
                mode='lines+markers',
                line=dict(width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title='피크 파장 변화',
                xaxis_title='각도 (degrees)',
                yaxis_title='파장 (nm)',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 강도 변화
            fig = go.Figure()
            normalized_int = results['peak_intensities'] / results['peak_intensities'][0]
            fig.add_trace(go.Scatter(
                x=results['angles'],
                y=normalized_int,
                mode='lines+markers',
                line=dict(width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title='강도 변화',
                xaxis_title='각도 (degrees)',
                yaxis_title='상대 강도',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

        # 스펙트럼 플롯
        display_angles = st.multiselect(
            "표시할 각도",
            angles.tolist(),
            default=[0, 20, 40, 60]
        )

        if display_angles:
            fig = plot_spectrum_at_angles(
                simulator,
                custom_params,
                display_angles,
                color_choice
            )
            st.plotly_chart(fig, use_container_width=True)

    else:  # 실측 데이터 비교
        st.header("📊 실측 데이터 비교")

        st.info("""
        **실측 데이터:**
        - Red: 625nm (0°) → 620nm (60°)
        - Green: 543nm (0°) → 521nm (60°)
        - Blue: 461nm (0°) → 459nm (60°)
        """)

        # 파라미터 피팅 옵션
        st.sidebar.subheader("파라미터 피팅")

        fit_params = {}
        for color in ['red', 'green', 'blue']:
            with st.sidebar.expander(f"{color.upper()} 파라미터"):
                n_eff = st.slider(
                    f"유효 굴절률",
                    1.5, 2.0, 1.8, 0.01,
                    key=f'n_{color}'
                )
                fwhm = st.slider(
                    f"FWHM (nm)",
                    10.0, 60.0, 30.0, 1.0,
                    key=f'fwhm_{color}'
                )

                lambda_0 = measured_data[color]['wavelengths'][0]
                cavity_length = simulator.calculate_cavity_length_from_wavelength(
                    lambda_0, n_eff, order=2
                )

                fit_params[color] = OLEDParams(
                    lambda_0=lambda_0,
                    n_eff=n_eff,
                    cavity_length=cavity_length,
                    order=2,
                    fwhm=fwhm,
                    peak_intensity=1.0
                )

        # 시뮬레이션 실행
        angles = np.arange(0, 61, 1)
        results_dict = {}
        for color_name, params in fit_params.items():
            results = simulator.simulate_angular_dependence(params, angles)
            results_dict[color_name] = results

        # 비교 플롯
        fig = plot_comparison_with_measured(results_dict, measured_data)
        st.plotly_chart(fig, use_container_width=True)

        # RMSE 계산
        st.subheader("피팅 품질 평가")
        col1, col2, col3 = st.columns(3)

        for i, (color_name, results) in enumerate(results_dict.items()):
            measured = measured_data[color_name]

            # 실측 각도에서의 시뮬레이션 값 추출
            sim_at_measured = np.interp(
                measured['angles'],
                results['angles'],
                results['peak_wavelengths']
            )

            rmse = np.sqrt(np.mean((sim_at_measured - measured['wavelengths']) ** 2))

            cols = [col1, col2, col3]
            with cols[i]:
                st.metric(
                    f"{color_name.upper()} RMSE",
                    f"{rmse:.2f} nm"
                )


if __name__ == "__main__":
    main()
