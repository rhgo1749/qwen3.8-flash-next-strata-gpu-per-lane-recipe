# Independent GPU Lanes — 재현성·실험 기록

[English](README.md) | **한국어**

> **연구 기록용 저장소이며 일반 사용을 위한 배포 권장안이 아니다.**
>
> 이 저장소는 Strata-Lanes 연구 과정의 실험, 원시 측정값, 벤치 하네스, 버전 provenance를 보존한다. 일반적인 Strata 설치와 서빙에는 **[Niko1221/Strata](https://github.com/Niko1221/Strata)** 사용을 권장한다.
>
> ✅ 이 연구의 일부는 upstream에 채택됐습니다: `--shared-expert-arena`가 [Strata v0.1.30](https://github.com/Niko1221/Strata/releases/tag/v0.1.30)에 릴리스됨.

이 저장소는 원래 GPU마다 독립 Strata 엔진 하나를 두고 큰 host expert arena만 프로세스 사이에서 물리적으로 공유하는 GPU-per-lane 서빙 구성을 실사용 레시피 형태로 정리했다.

하지만 upstream Strata 0.1.39에서 batch slot, layer-split pipeline group, stage-weight trimming이 추가되면서 성능 구도가 크게 바뀌었다. 따라서 지금은 **사용 권장 레시피가 아니라 실험 기록과 재현성 저장소**로 유지한다.

## 현재 결론

기준 3×RTX 5070 Ti 호스트에서 현재 증거는 **workload-dependent topology crossover**다.

| 영역 | Independent lanes | Pipelined layer split |
| --- | ---: | ---: |
| M=1 fixed decode | 73.63 ± 1.67 tok/s | **120.62 ± 1.24 tok/s**¹ |
| M=2 fixed decode | 143.19 ± 3.06 tok/s | **147.84 ± 2.26 tok/s** |
| M=3 fixed decode | 192.16 ± 4.11 tok/s | **209.66 ± 4.02 tok/s** |
| ~15K cold prompt 3개 | **5901.34 ± 55.16 tok/s** | 3289.19 ± 18.83 tok/s |
| ~110K cold prompt 3개 | 5822.71 ± 4.49 tok/s | **6028.09 ± 14.50 tok/s** |

¹ M=1은 동일 0.1.39 binary의 기존 3-GPU layer-split single-request control이고, M=2/M=3은 exact fixed pipeline config 측정값이다.

따라서 이제 independent lanes를 Strata의 일반적인 상위호환 또는 기본 권장 배포 방식으로 제시하지 않는다.

- 중간 길이 cold prompt 여러 개가 동시에 들어올 때는 lanes가 크게 유리한 영역이 있다.
- decode M=2/M=3에서는 upstream pipelined layer split이 현재 측정에서 앞선다.
- 아주 긴 cold prefill에서는 layer split이 다시 근소하게 앞선다.
- isolation, session locality, failure boundary 같은 시스템 특성은 별도의 연구 가치가 남아 있다.

## 이 저장소에 남기는 것

- 버전별 benchmark contract
- retained raw JSON/JSONL
- 실제 벤치 harness/config
- independent-lane scaling
- shared expert arena 메모리 증거
- queue/oversubscription 및 scheduler 실험
- heterogeneous GPU / interference 실험
- conversation parking 실험
- independent lanes ↔ upstream layer split matched 비교
- 논문/revision evidence와 provenance

즉 **설치 가이드보다 재현·감사·향후 비교용 기록**이 중심이다.

## 현재 증거 보기

- [RESULTS.md](RESULTS.md) — 현재 핵심 결과와 과거 세대 기록
- [0.1.39 topology crossover](docs/strata-0.1.39-performance-crossover-20261005.md)
- [벤치/리포팅 계약](bench/README.md)
- [0.1.39 retained raw evidence](bench/raw/0.1.39-20261005/)
- [0.1.39 compact topology table](bench/layer-split-ab-0.1.39-20261005.csv)

구현 포크:

- [rhgo1749/Strata-Lanes](https://github.com/rhgo1749/Strata-Lanes)

upstream:

- [Niko1221/Strata](https://github.com/Niko1221/Strata)

## 증거 세대

측정값은 반드시 실제 측정에 사용한 engine/source generation에 귀속한다.

- **0.1.39** — M=1/M=2/M=3 decode와 15K/110K 3-request cold-prefill crossover
- **0.1.38** — full architecture campaign과 software-sync gate
- **0.1.31** — serving-control / lifecycle 검증
- **0.1.30** — retained full architecture matrix

upstream 변화로 과거 해석이 깨진 경우에도 원시 결과를 지우지 않고 새 증거가 해석을 supersede하도록 기록한다.

## 기준 호스트

    CPU                 Ryzen 9 9950X3D
    RAM                 128 GB DDR5
    primary GPUs        RTX 5070 Ti 16 GB ×3
    driver              NVIDIA 615.71.09
    CUDA                13.4
    model/quant         Qwen3.8-Flash-Next GSQ-RCO IQ3_S

이 값들은 실험 조건이지 다른 PC의 기본값이 아니다.

## 과거 Lanes 실험 재현

실행/config 자료는 계속 보존한다.

- [docs/USAGE.md](docs/USAGE.md)
- [recipe/launch-3lane.sh.example](recipe/launch-3lane.sh.example)

이 문서들은 이제 **reproduction instructions**이며 upstream Strata 대신 Lanes 사용을 권장하는 문서가 아니다.

## 저장소 상태

- **모드:** active experimental record / reproducibility archive
- **일반 사용자 권장:** upstream Strata
- **Lanes 코드·설정:** 재현을 위해 보존
- **향후 변경:** 증거 기반 비교, provenance 수정, 논문 revision 지원

## 라이선스

이 저장소의 recipe 문서와 helper material은 MIT 라이선스다. Strata, 모델 파일, third-party 구성요소는 각 원래 라이선스를 따른다.
