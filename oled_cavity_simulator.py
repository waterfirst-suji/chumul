"""
OLED 2차 공진구조 각도 의존성 시뮬레이터

물리적 원리:
1. Fabry-Perot 공진기 모델
   - OLED의 2차 공진구조는 하부 반사전극과 상부 반투명 전극 사이의 광학 공진 구조
   - 공진 조건: m * λ = 2 * n_eff * d * cos(θ_internal)

2. 각도에 따른 Blue Shift 원인:
   - 관찰 각도가 증가하면 공진기 내부 각도도 증가 (Snell's law)
   - cos(θ)가 감소하므로, 같은 차수(m)에서 공진하는 파장(λ)이 감소
   - 따라서 스펙트럼이 짧은 파장으로 이동 (blue shift)

3. Intensity 감소 원인:
   - Lambertian 발광 특성: I(θ) = I₀ * cos(θ)
   - 공진 조건 이탈로 인한 발광 효율 감소
   - Fresnel 계수의 각도 의존성
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, List


@dataclass
class OLEDParams:
    """OLED 공진구조 파라미터"""
    # 중심 파장 (nm)
    lambda_0: float
    # 유효 굴절률
    n_eff: float
    # 공진 길이 (nm)
    cavity_length: float
    # 공진 차수
    order: int = 2
    # 스펙트럼 폭 (FWHM, nm)
    fwhm: float = 30.0
    # Peak intensity
    peak_intensity: float = 1.0


class OLEDCavitySimulator:
    """OLED 2차 공진구조 시뮬레이터"""

    def __init__(self):
        # 외부 굴절률 (공기)
        self.n_air = 1.0
        # 기판 굴절률 (유리)
        self.n_substrate = 1.5

    def snells_law(self, theta_external: float, n1: float, n2: float) -> float:
        """
        Snell's law를 이용한 내부 각도 계산

        Args:
            theta_external: 외부 각도 (degrees)
            n1: 외부 매질 굴절률
            n2: 내부 매질 굴절률

        Returns:
            내부 각도 (degrees)
        """
        theta_rad = np.radians(theta_external)
        sin_theta_internal = (n1 / n2) * np.sin(theta_rad)

        # 전반사 조건 체크
        if sin_theta_internal > 1.0:
            return 90.0

        theta_internal = np.arcsin(sin_theta_internal)
        return np.degrees(theta_internal)

    def resonance_wavelength(self, params: OLEDParams, theta_internal: float) -> float:
        """
        공진 파장 계산

        공진 조건: m * λ = 2 * n_eff * d * cos(θ)
        따라서: λ(θ) = (2 * n_eff * d * cos(θ)) / m

        Args:
            params: OLED 파라미터
            theta_internal: 내부 각도 (degrees)

        Returns:
            공진 파장 (nm)
        """
        theta_rad = np.radians(theta_internal)
        lambda_res = (2 * params.n_eff * params.cavity_length * np.cos(theta_rad)) / params.order
        return lambda_res

    def gaussian_spectrum(self, wavelengths: np.ndarray, center: float, fwhm: float, amplitude: float) -> np.ndarray:
        """
        Gaussian 스펙트럼 생성

        Args:
            wavelengths: 파장 배열 (nm)
            center: 중심 파장 (nm)
            fwhm: Full Width at Half Maximum (nm)
            amplitude: Peak amplitude

        Returns:
            스펙트럼 강도 배열
        """
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        spectrum = amplitude * np.exp(-((wavelengths - center) ** 2) / (2 * sigma ** 2))
        return spectrum

    def lambertian_factor(self, theta_external: float) -> float:
        """
        Lambertian 발광 특성에 의한 강도 감소

        Args:
            theta_external: 외부 각도 (degrees)

        Returns:
            강도 비율
        """
        theta_rad = np.radians(theta_external)
        return np.cos(theta_rad)

    def cavity_enhancement_factor(self, wavelength: float, resonance_wavelength: float, fwhm: float) -> float:
        """
        공진기 증강 효과

        공진 파장에서 최대, 멀어질수록 감소

        Args:
            wavelength: 현재 파장 (nm)
            resonance_wavelength: 공진 파장 (nm)
            fwhm: 공진 폭 (nm)

        Returns:
            증강 계수
        """
        # Lorentzian 형태의 공진기 응답
        gamma = fwhm / 2
        enhancement = 1 / (1 + ((wavelength - resonance_wavelength) / gamma) ** 2)
        return enhancement

    def simulate_spectrum_at_angle(
        self,
        params: OLEDParams,
        theta_external: float,
        wavelength_range: Tuple[float, float] = (400, 700),
        num_points: int = 300
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        특정 각도에서의 발광 스펙트럼 시뮬레이션

        Args:
            params: OLED 파라미터
            theta_external: 외부 관찰 각도 (degrees)
            wavelength_range: 파장 범위 (nm)
            num_points: 스펙트럼 포인트 수

        Returns:
            (wavelengths, intensities) 튜플
        """
        # 파장 배열 생성
        wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], num_points)

        # 내부 각도 계산
        theta_internal = self.snells_law(theta_external, self.n_air, params.n_eff)

        # 각도에 따른 공진 파장 계산
        lambda_resonance = self.resonance_wavelength(params, theta_internal)

        # 기본 Gaussian 스펙트럼
        spectrum = self.gaussian_spectrum(wavelengths, lambda_resonance, params.fwhm, params.peak_intensity)

        # Lambertian 감쇠 적용
        lambertian = self.lambertian_factor(theta_external)

        # 공진기 증강 효과
        for i, wl in enumerate(wavelengths):
            cavity_factor = self.cavity_enhancement_factor(wl, lambda_resonance, params.fwhm)
            spectrum[i] *= cavity_factor

        # 최종 강도 = 기본 스펙트럼 × Lambertian 감쇠
        intensities = spectrum * lambertian

        return wavelengths, intensities

    def find_peak_wavelength(self, wavelengths: np.ndarray, intensities: np.ndarray) -> float:
        """
        스펙트럼에서 피크 파장 찾기

        Args:
            wavelengths: 파장 배열
            intensities: 강도 배열

        Returns:
            피크 파장 (nm)
        """
        peak_idx = np.argmax(intensities)
        return wavelengths[peak_idx]

    def find_peak_intensity(self, intensities: np.ndarray) -> float:
        """
        스펙트럼에서 피크 강도 찾기

        Args:
            intensities: 강도 배열

        Returns:
            피크 강도
        """
        return np.max(intensities)

    def simulate_angular_dependence(
        self,
        params: OLEDParams,
        angles: np.ndarray,
        wavelength_range: Tuple[float, float] = (400, 700)
    ) -> dict:
        """
        각도별 스펙트럼 변화 시뮬레이션

        Args:
            params: OLED 파라미터
            angles: 각도 배열 (degrees)
            wavelength_range: 파장 범위 (nm)

        Returns:
            시뮬레이션 결과 딕셔너리
        """
        results = {
            'angles': angles,
            'peak_wavelengths': [],
            'peak_intensities': [],
            'spectra': [],
            'wavelength_axis': None
        }

        for angle in angles:
            wavelengths, intensities = self.simulate_spectrum_at_angle(
                params, angle, wavelength_range
            )

            if results['wavelength_axis'] is None:
                results['wavelength_axis'] = wavelengths

            peak_wl = self.find_peak_wavelength(wavelengths, intensities)
            peak_int = self.find_peak_intensity(intensities)

            results['peak_wavelengths'].append(peak_wl)
            results['peak_intensities'].append(peak_int)
            results['spectra'].append(intensities)

        results['peak_wavelengths'] = np.array(results['peak_wavelengths'])
        results['peak_intensities'] = np.array(results['peak_intensities'])
        results['spectra'] = np.array(results['spectra'])

        return results

    def calculate_cavity_length_from_wavelength(
        self,
        lambda_0: float,
        n_eff: float,
        order: int = 2
    ) -> float:
        """
        원하는 공진 파장으로부터 공진 길이 역계산

        m * λ₀ = 2 * n_eff * d
        d = (m * λ₀) / (2 * n_eff)

        Args:
            lambda_0: 목표 공진 파장 (nm)
            n_eff: 유효 굴절률
            order: 공진 차수

        Returns:
            공진 길이 (nm)
        """
        cavity_length = (order * lambda_0) / (2 * n_eff)
        return cavity_length


def create_rgb_oled_params() -> dict:
    """
    실측 데이터 기반 RGB OLED 파라미터 생성

    실측 데이터:
    - Red: 625nm (0°) → 620nm (60°)
    - Green: 543nm (0°) → 521nm (60°)
    - Blue: 461nm (0°) → 459nm (60°)

    Returns:
        RGB 파라미터 딕셔너리
    """
    simulator = OLEDCavitySimulator()

    # Red OLED
    # 유효 굴절률 추정 (일반적인 유기물: 1.7-1.9)
    n_eff_red = 1.8
    cavity_length_red = simulator.calculate_cavity_length_from_wavelength(625, n_eff_red, order=2)

    red_params = OLEDParams(
        lambda_0=625,
        n_eff=n_eff_red,
        cavity_length=cavity_length_red,
        order=2,
        fwhm=25.0,
        peak_intensity=1.0
    )

    # Green OLED
    n_eff_green = 1.8
    cavity_length_green = simulator.calculate_cavity_length_from_wavelength(543, n_eff_green, order=2)

    green_params = OLEDParams(
        lambda_0=543,
        n_eff=n_eff_green,
        cavity_length=cavity_length_green,
        order=2,
        fwhm=30.0,
        peak_intensity=1.0
    )

    # Blue OLED
    n_eff_blue = 1.8
    cavity_length_blue = simulator.calculate_cavity_length_from_wavelength(461, n_eff_blue, order=2)

    blue_params = OLEDParams(
        lambda_0=461,
        n_eff=n_eff_blue,
        cavity_length=cavity_length_blue,
        order=2,
        fwhm=35.0,
        peak_intensity=1.0
    )

    return {
        'red': red_params,
        'green': green_params,
        'blue': blue_params
    }


if __name__ == "__main__":
    # 테스트 코드
    simulator = OLEDCavitySimulator()
    rgb_params = create_rgb_oled_params()

    # 0도와 60도에서의 시뮬레이션
    angles = np.array([0, 10, 20, 30, 40, 50, 60])

    print("=" * 60)
    print("OLED 2차 공진구조 각도 의존성 시뮬레이션")
    print("=" * 60)

    for color, params in rgb_params.items():
        print(f"\n{color.upper()} OLED:")
        print(f"  유효 굴절률: {params.n_eff:.2f}")
        print(f"  공진 길이: {params.cavity_length:.2f} nm")
        print(f"  공진 차수: {params.order}")

        results = simulator.simulate_angular_dependence(params, angles)

        print(f"\n  각도별 피크 파장 변화:")
        for i, angle in enumerate(angles):
            wl = results['peak_wavelengths'][i]
            intensity = results['peak_intensities'][i]
            shift = wl - results['peak_wavelengths'][0]
            print(f"    {angle:2d}° → {wl:.1f} nm (shift: {shift:+.1f} nm, intensity: {intensity:.3f})")
