import streamlit as st
import pandas as pd
import os
from datetime import datetime

# === [설정] 파일 저장 경로 ===
DB_FILE = 'stock_diagnosis_history.csv'

# === [1] 화면 구성 (UI) ===
st.set_page_config(page_title="호동쌤의 탄탄 주식 진단기", page_icon="📈")

st.title("📈 호동쌤의 탄탄 주식 진단기")
st.markdown("종목을 분석하고 **진단하기** 버튼을 누르면 결과가 **엑셀(CSV)에 자동 저장**됩니다.")

# 사이드바: 종목 정보 입력
with st.sidebar:
    st.header("📝 종목 정보")
    stock_name = st.text_input("종목명", placeholder="예: 삼성전자")
    current_price = st.number_input("현재가", min_value=0, step=100)
    diagnosis_date = datetime.now().strftime("%Y-%m-%d")
    st.info(f"진단일: {diagnosis_date}")

# === [2] 질문 리스트 정의 ===
questions = {
    "1. 성장성 (Growth)": [
        "① 정부 정책의 수혜를 받는가? (P)",
        "② 대기업 투자가 진행 중인가? (C)",
        "③ 글로벌 확장성이 있는가? (G)"
    ],
    "2. 실적 (Fundamental)": [
        "① 매출액이 전년 대비 늘었는가?",
        "② 영업이익이 흑자(턴어라운드)인가?",
        "③ 영업이익률이 10% 이상(개선)인가?"
    ],
    "3. 수급 (Money)": [
        "① 외인/기관 양매수(쌍끌이)인가?",
        "② 3일 이상 연속 매수 중인가?",
        "③ 개인 투자자는 매도 중인가?"
    ],
    "4. 차트 (Trend)": [
        "① 정배열 (주가>20>60) 상태인가?",
        "② 신고가 혹은 눌림목 구간인가?",
        "③ 위쪽에 악성 매물대가 없는가?"
    ]
}

# === [3] 체크리스트 출력 및 입력 받기 ===
user_answers = {} # 답변 저장용 딕셔너리
score_per_q = 100 / 12 # 문항당 배점

col1, col2 = st.columns(2) # 화면을 2단으로 나눔

# 반복문으로 질문 뿌리기
idx = 0
for category, q_list in questions.items():
    # 왼쪽/오른쪽 단 번갈아 가며 배치
    target_col = col1 if idx < 2 else col2
    
    with target_col:
        st.subheader(category)
        for q in q_list:
            # 체크박스 생성 (key는 유니크해야 함)
            user_answers[q] = st.checkbox(q, key=q)
    idx += 1

st.markdown("---")

# === [4] 진단 버튼 및 로직 ===
if st.button("🚀 진단 결과 확인 및 저장", type="primary", use_container_width=True):
    if not stock_name:
        st.error("⚠️ 종목명을 입력해주세요!")
    else:
        # 점수 계산
        yes_count = sum(user_answers.values())
        total_score = int(yes_count * score_per_q)
        
        # 결과 메시지 판정
        if total_score >= 90:
            grade = "강력 매수"
            msg = "🚀 주도주 탄생 예감! 강력 추천합니다."
            color = "green"
        elif total_score >= 70:
            grade = "매수 고려"
            msg = "⚖️ 흐름이 양호합니다. 매수를 고려해보세요."
            color = "blue"
        elif total_score >= 50:
            grade = "관망"
            msg = "👀 조금 더 지켜볼 필요가 있습니다."
            color = "orange"
        else:
            grade = "위험"
            msg = "⚠️ 지금은 매수할 때가 아닙니다."
            color = "red"

        # 결과 화면 표시
        st.balloons() # 축하 효과
        st.success(f"[{stock_name}] 진단 완료!")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("총점", f"{total_score}점")
        c2.metric("등급", grade)
        c3.metric("체크 항목", f"{yes_count} / 12")
        
        st.markdown(f"### 💡 호동쌤의 한마디")
        st.markdown(f":{color}[**{msg}**]")

        # === [5] 엑셀(CSV) 저장 로직 ===
        new_data = {
            "진단일": diagnosis_date,
            "종목명": stock_name,
            "현재가": current_price,
            "점수": total_score,
            "등급": grade,
            "상세_성장성": sum([user_answers[q] for q in questions["1. 성장성 (Growth)"]]),
            "상세_실적": sum([user_answers[q] for q in questions["2. 실적 (Fundamental)"]]),
            "상세_수급": sum([user_answers[q] for q in questions["3. 수급 (Money)"]]),
            "상세_차트": sum([user_answers[q] for q in questions["4. 차트 (Trend)"]])
        }
        
        df_new = pd.DataFrame([new_data])

        # 파일이 없으면 새로 만들고, 있으면 이어붙이기
        if not os.path.exists(DB_FILE):
            df_new.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')
            
        st.toast(f"💾 '{DB_FILE}' 파일에 저장되었습니다!", icon="✅")

# === [6] 하단: 저장된 기록 보여주기 + 삭제 기능 ===
if os.path.exists(DB_FILE):
    with st.expander("📂 내 진단 기록 보기 (엑셀 데이터)"):
        # 1. 데이터 읽어서 보여주기
        history_df = pd.read_csv(DB_FILE)
        st.dataframe(history_df, use_container_width=True)
        
        st.markdown("---")
        
        # 2. 삭제 버튼 영역 (오른쪽 정렬을 위해 컬럼 나눔)
        c1, c2 = st.columns([3, 1]) 
        
        with c2:
            # 버튼을 누르면 파일 삭제
            if st.button("🗑️ 기록 전체 삭제", type="primary"):
                os.remove(DB_FILE) # 파일(DB)을 물리적으로 삭제
                st.rerun() # 화면을 즉시 새로고침해서 반영
        
        with c1:
            st.caption("⚠️ '삭제' 버튼을 누르면 모든 진단 기록이 영구적으로 사라집니다.")