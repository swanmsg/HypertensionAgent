"""
Streamlit Web界面
高血压患者医嘱智能体平台前端
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional

# 配置页面
st.set_page_config(
    page_title="高血压患者医嘱智能体平台",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API配置
API_BASE_URL = "http://localhost:8000"

# 样式配置
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2e8b57;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff8dc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffa500;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe4e1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint: str, method: str = "GET", data: dict = None):
    """发送API请求"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API请求失败: {e}")
        return None

def display_blood_pressure_chart(records: List[Dict]):
    """显示血压趋势图"""
    if not records:
        st.info("暂无血压记录")
        return
    
    df = pd.DataFrame(records)
    df['measurement_time'] = pd.to_datetime(df['measurement_time'])
    df = df.sort_values('measurement_time')
    
    fig = go.Figure()
    
    # 收缩压线
    fig.add_trace(go.Scatter(
        x=df['measurement_time'],
        y=df['systolic_bp'],
        mode='lines+markers',
        name='收缩压',
        line=dict(color='red', width=2)
    ))
    
    # 舒张压线
    fig.add_trace(go.Scatter(
        x=df['measurement_time'],
        y=df['diastolic_bp'],
        mode='lines+markers',
        name='舒张压',
        line=dict(color='blue', width=2)
    ))
    
    # 参考线
    fig.add_hline(y=140, line_dash="dash", line_color="orange", annotation_text="收缩压正常上限(140)")
    fig.add_hline(y=90, line_dash="dash", line_color="orange", annotation_text="舒张压正常上限(90)")
    
    fig.update_layout(
        title="血压趋势图",
        xaxis_title="时间",
        yaxis_title="血压值 (mmHg)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    """主界面"""
    # 标题
    st.markdown('<div class="main-header">🏥 高血压患者医嘱智能体平台</div>', unsafe_allow_html=True)
    
    # 侧边栏导航
    st.sidebar.title("功能导航")
    page = st.sidebar.selectbox(
        "选择功能",
        ["🏠 首页", "👤 患者管理", "📊 血压监测", "🤖 AI智能咨询", "💊 药物建议", "📚 知识库"]
    )
    
    if page == "🏠 首页":
        show_home_page()
    elif page == "👤 患者管理":
        show_patient_management()
    elif page == "📊 血压监测":
        show_blood_pressure_monitoring()
    elif page == "🤖 AI智能咨询":
        show_ai_consultation()
    elif page == "💊 药物建议":
        show_medication_advice()
    elif page == "📚 知识库":
        show_knowledge_base()

def show_home_page():
    """首页"""
    st.markdown('<div class="sub-header">欢迎使用高血压患者医嘱智能体平台</div>', unsafe_allow_html=True)
    
    # 模型信息显示
    model_info = make_api_request("/ai/model-info")
    if model_info:
        if model_info.get('status') == 'online':
            st.success(f"🤖 AI模型: {model_info.get('description', '未知')} (在线)")
        else:
            st.warning("🤖 AI模型: 不可用")
    
    # 功能介绍
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="info-box">
            <h3>🏥 智能医嘱生成</h3>
            <p>基于患者信息生成个性化医疗建议，包括生活方式干预和药物治疗方案。</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h3>📊 血压趋势分析</h3>
            <p>记录和分析血压变化趋势，提供可视化图表和统计分析。</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-box">
            <h3>🤖 AI智能对话</h3>
            <p>与AI医疗助手对话，获取专业的高血压咨询和健康建议。</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 快速血压分析
    st.markdown('<div class="sub-header">快速血压分析</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        systolic = st.number_input("收缩压 (mmHg)", min_value=60, max_value=300, value=120)
    
    with col2:
        diastolic = st.number_input("舒张压 (mmHg)", min_value=40, max_value=200, value=80)
    
    with col3:
        if st.button("分析血压", type="primary"):
            result = make_api_request(f"/ai/analyze-blood-pressure?systolic={systolic}&diastolic={diastolic}", "POST")
            if result:
                st.success(f"血压分级: {result.get('classification', '未知')}")
                st.info(f"风险等级: {result.get('risk_level', '未知')}")
                
                if result.get('is_emergency'):
                    st.error("⚠️ 血压严重升高，建议立即就医！")
                
                if result.get('recommendations'):
                    st.write("**建议:**")
                    for rec in result['recommendations']:
                        st.write(f"• {rec}")
    
    # 免责声明
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ 重要提醒</h4>
        <p>本系统提供的建议仅供参考，不能替代专业医生的诊断和治疗。如有疑问或症状加重，请及时就医。</p>
    </div>
    """, unsafe_allow_html=True)

def show_patient_management():
    """患者管理"""
    st.markdown('<div class="sub-header">患者信息管理</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["新建患者", "患者列表", "患者详情"])
    
    with tab1:
        st.subheader("新建患者档案")
        
        with st.form("patient_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("姓名 *", help="患者姓名")
                age = st.number_input("年龄 *", min_value=0, max_value=150, value=50)
                gender = st.selectbox("性别 *", ["男", "女"])
                height = st.number_input("身高 (cm)", min_value=50.0, max_value=250.0, value=170.0)
                weight = st.number_input("体重 (kg)", min_value=20.0, max_value=300.0, value=70.0)
            
            with col2:
                phone = st.text_input("电话", help="联系电话")
                email = st.text_input("邮箱", help="电子邮箱")
                systolic_bp = st.number_input("收缩压 (mmHg)", min_value=60.0, max_value=300.0, value=120.0)
                diastolic_bp = st.number_input("舒张压 (mmHg)", min_value=40.0, max_value=200.0, value=80.0)
                hypertension_duration = st.number_input("高血压病程 (年)", min_value=0, value=0)
            
            st.subheader("病史信息")
            col3, col4 = st.columns(2)
            
            with col3:
                family_history = st.checkbox("家族史")
                smoking = st.checkbox("吸烟")
                drinking = st.checkbox("饮酒")
                diabetes = st.checkbox("糖尿病")
            
            with col4:
                heart_disease = st.checkbox("心脏病")
                kidney_disease = st.checkbox("肾脏疾病")
                stroke_history = st.checkbox("脑卒中史")
                exercise_frequency = st.selectbox("运动频率", ["从不运动", "偶尔运动", "有时运动", "经常运动", "每日运动"])
            
            current_medications = st.text_area("当前用药", help="请输入当前正在服用的药物")
            allergies = st.text_area("过敏史", help="请输入已知的药物或食物过敏")
            
            submitted = st.form_submit_button("创建患者", type="primary")
            
            if submitted:
                if not name:
                    st.error("请输入患者姓名")
                else:
                    patient_data = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "height": height,
                        "weight": weight,
                        "phone": phone or None,
                        "email": email or None,
                        "systolic_bp": systolic_bp,
                        "diastolic_bp": diastolic_bp,
                        "hypertension_duration": hypertension_duration,
                        "family_history": family_history,
                        "smoking": smoking,
                        "drinking": drinking,
                        "diabetes": diabetes,
                        "heart_disease": heart_disease,
                        "kidney_disease": kidney_disease,
                        "stroke_history": stroke_history,
                        "exercise_frequency": exercise_frequency,
                        "current_medications": current_medications or None,
                        "allergies": allergies or None
                    }
                    
                    result = make_api_request("/patients/", "POST", patient_data)
                    if result:
                        st.success(f"患者 {name} 创建成功！")
                        st.balloons()
    
    with tab2:
        st.subheader("患者列表")
        
        # 获取患者列表
        patients = make_api_request("/patients/")
        if patients:
            df = pd.DataFrame(patients)
            df['bmi'] = df.apply(lambda row: round(row['weight'] / (row['height']/100)**2, 2) if row['height'] and row['weight'] else None, axis=1)
            
            # 显示患者列表
            for _, patient in df.iterrows():
                with st.expander(f"{patient['name']} (ID: {patient['id']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**年龄:** {patient['age']} 岁")
                        st.write(f"**性别:** {patient['gender']}")
                        st.write(f"**BMI:** {patient['bmi']:.1f}" if patient['bmi'] else "**BMI:** 未知")
                    
                    with col2:
                        st.write(f"**血压:** {patient['systolic_bp']:.0f}/{patient['diastolic_bp']:.0f} mmHg")
                        st.write(f"**高血压病程:** {patient['hypertension_duration']} 年")
                    
                    with col3:
                        if st.button(f"查看详情", key=f"view_{patient['id']}"):
                            st.session_state.selected_patient_id = patient['id']
        else:
            st.info("暂无患者记录")
    
    with tab3:
        st.subheader("患者详情")
        
        if 'selected_patient_id' in st.session_state:
            patient_id = st.session_state.selected_patient_id
            patient = make_api_request(f"/patients/{patient_id}")
            
            if patient:
                # 基本信息
                st.write("### 基本信息")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**姓名:** {patient['name']}")
                    st.write(f"**年龄:** {patient['age']} 岁")
                    st.write(f"**性别:** {patient['gender']}")
                
                with col2:
                    st.write(f"**身高:** {patient['height']} cm")
                    st.write(f"**体重:** {patient['weight']} kg")
                    if patient['height'] and patient['weight']:
                        bmi = patient['weight'] / (patient['height']/100)**2
                        st.write(f"**BMI:** {bmi:.1f}")
                
                with col3:
                    st.write(f"**电话:** {patient['phone'] or '未填写'}")
                    st.write(f"**邮箱:** {patient['email'] or '未填写'}")
                
                # 血压信息
                st.write("### 血压信息")
                st.write(f"**当前血压:** {patient['systolic_bp']}/{patient['diastolic_bp']} mmHg")
                st.write(f"**测量时间:** {patient['bp_measurement_time']}")
                
                # 病史信息
                st.write("### 病史信息")
                risk_factors = []
                if patient['smoking']: risk_factors.append("吸烟")
                if patient['diabetes']: risk_factors.append("糖尿病")
                if patient['heart_disease']: risk_factors.append("心脏病")
                if patient['kidney_disease']: risk_factors.append("肾脏疾病")
                if patient['family_history']: risk_factors.append("家族史")
                
                st.write(f"**危险因素:** {', '.join(risk_factors) if risk_factors else '无'}")
                st.write(f"**当前用药:** {patient['current_medications'] or '无'}")
                st.write(f"**过敏史:** {patient['allergies'] or '无'}")
        else:
            st.info("请从患者列表中选择一个患者查看详情")

def show_blood_pressure_monitoring():
    """血压监测"""
    st.markdown('<div class="sub-header">血压监测管理</div>', unsafe_allow_html=True)
    
    # 患者选择
    patients = make_api_request("/patients/")
    if not patients:
        st.warning("请先创建患者档案")
        return
    
    patient_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients}
    selected_patient = st.selectbox("选择患者", list(patient_options.keys()))
    patient_id = patient_options[selected_patient]
    
    tab1, tab2, tab3 = st.tabs(["新增记录", "血压趋势", "统计分析"])
    
    with tab1:
        st.subheader("新增血压记录")
        
        # 显示当前选中的患者信息
        selected_patient_name = list(patient_options.keys())[list(patient_options.values()).index(patient_id)]
        st.info(f"👥 当前患者：{selected_patient_name}")
        
        with st.form("bp_record_form_unique"):
            st.write("📝 **输入血压数据**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                systolic = st.number_input("收缩压 (mmHg)", min_value=60.0, max_value=300.0, value=120.0, key="bp_systolic")
                diastolic = st.number_input("舒张压 (mmHg)", min_value=40.0, max_value=200.0, value=80.0, key="bp_diastolic")
            
            with col2:
                heart_rate = st.number_input("心率 (次/分)", min_value=30, max_value=200, value=70, key="bp_heart_rate")
                measurement_time = st.datetime_input("测量时间", value=datetime.now(), key="bp_measurement_time")
            
            st.write("📝 **详细信息（可选）**")
            measurement_location = st.text_input("测量位置", placeholder="如：左臂、右臂等", key="bp_measurement_location")
            notes = st.text_area("备注", placeholder="记录测量时的特殊情况", key="bp_notes")
            
            # 必须的提交按钮
            submitted = st.form_submit_button("新增血压记录")
        
        # 处理表单提交（在表单外部）
        if submitted:
            record_data = {
                "patient_id": patient_id,
                "systolic_bp": systolic,
                "diastolic_bp": diastolic,
                "heart_rate": heart_rate,
                "measurement_time": measurement_time.isoformat(),
                "measurement_location": measurement_location or "左臂",
                "notes": notes or None
            }
            
            result = make_api_request("/blood-pressure/", "POST", record_data)
            if result:
                st.success("✨ 新增记录成功！")
                st.balloons()
                
                # 快速分析
                analysis = make_api_request(f"/ai/analyze-blood-pressure?systolic={systolic}&diastolic={diastolic}", "POST")
                if analysis:
                    st.info(f"血压分级: {analysis.get('classification', '未知')}")
                    if analysis.get('is_emergency'):
                        st.error("⚠️ 血压异常升高，建议立即就医！")
    
    with tab2:
        st.subheader("血压趋势图")
        
        days = st.selectbox("时间范围", [7, 14, 30, 60, 90], index=2)
        records = make_api_request(f"/blood-pressure/patient/{patient_id}?days={days}")
        
        if records:
            display_blood_pressure_chart(records)
        else:
            st.info("暂无血压记录")
    
    with tab3:
        st.subheader("统计分析")
        
        days = st.selectbox("统计周期", [7, 14, 30, 60, 90], index=2, key="stats_days")
        stats = make_api_request(f"/blood-pressure/patient/{patient_id}/statistics?days={days}")
        
        if stats and stats.get('count', 0) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("记录数量", f"{stats['count']} 次")
                st.metric("平均收缩压", f"{stats['systolic']['avg']} mmHg")
            
            with col2:
                st.metric("最高收缩压", f"{stats['systolic']['max']} mmHg")
                st.metric("最低收缩压", f"{stats['systolic']['min']} mmHg")
            
            with col3:
                st.metric("平均舒张压", f"{stats['diastolic']['avg']} mmHg")
                st.metric("最高舒张压", f"{stats['diastolic']['max']} mmHg")
        else:
            st.info("暂无统计数据")

def show_ai_consultation():
    """AI智能咨询"""
    st.markdown('<div class="sub-header">AI智能医疗咨询</div>', unsafe_allow_html=True)
    
    # 初始化对话历史
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # 患者上下文选择
    patients = make_api_request("/patients/")
    if patients:
        patient_options = {"无选择": None}
        patient_options.update({f"{p['name']} (ID: {p['id']})": p for p in patients})
        
        selected_patient_key = st.selectbox("选择患者上下文（可选）", list(patient_options.keys()))
        patient_context = patient_options[selected_patient_key]
    else:
        patient_context = None
    
    # 显示对话历史
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
    
    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 添加用户消息到历史
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # 发送到AI
        with st.spinner("AI正在思考中..."):
            response = make_api_request("/ai/chat", "POST", {
                "message": user_input,
                "patient_context": patient_context
            })
        
        if response:
            ai_response = response.get('response', '抱歉，AI暂时无法回答您的问题。')
            
            # 添加AI回复到历史
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.chat_message("assistant").write(ai_response)
        else:
            st.error("AI服务暂时不可用，请稍后再试。")
    
    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("清除对话历史"):
            st.session_state.chat_history = []
            make_api_request("/ai/clear-memory", "POST")
            st.success("对话历史已清除")
            st.rerun()
    
    with col2:
        if st.button("获取对话记录"):
            history = make_api_request("/ai/conversation-history")
            if history:
                st.json(history)

def show_medication_advice():
    """药物建议"""
    st.markdown('<div class="sub-header">药物治疗建议</div>', unsafe_allow_html=True)
    
    # 患者选择
    patients = make_api_request("/patients/")
    if not patients:
        st.warning("请先创建患者档案")
        return
    
    patient_options = {f"{p['name']} (ID: {p['id']})": p for p in patients}
    selected_patient_key = st.selectbox("选择患者", list(patient_options.keys()))
    patient = patient_options[selected_patient_key]
    
    # 药物建议表单
    with st.form("药物建议_form"):
        st.write(f"当前选中患者：{patient['name']}")
        st.write(f"血压：{patient['systolic_bp']}/{patient['diastolic_bp']} mmHg")
        submitted = st.form_submit_button("生成药物建议", type="primary")
        
        if submitted:
            with st.spinner("正在分析患者信息并生成药物建议..."):
                # 准备患者数据
                patient_data = {
                    "age": patient['age'],
                    "gender": patient['gender'],
                    "systolic_bp": patient['systolic_bp'],
                    "diastolic_bp": patient['diastolic_bp'],
                    "diabetes": patient['diabetes'],
                    "heart_disease": patient['heart_disease'],
                    "kidney_disease": patient['kidney_disease'],
                    "allergies": patient['allergies']
                }
                
                advice = make_api_request("/ai/medication-advice", "POST", patient_data)
            
            if advice:
                st.subheader("药物治疗建议")
                
                # 是否需要药物治疗
                if advice.get('needs_medication'):
                    st.success("✅ 建议药物治疗")
                    
                    # 首选药物
                    if advice.get('primary_drugs'):
                        st.write("### 首选药物类型")
                        for drug in advice['primary_drugs']:
                            st.write(f"**{drug['type']}**")
                            st.write(f"代表药物: {', '.join(drug['examples'])}")
                            st.write(f"适应症: {drug['reason']}")
                            st.write("---")
                    
                    # 联合用药
                    if advice.get('combination_drugs'):
                        st.write("### 联合用药方案")
                        for combo in advice['combination_drugs']:
                            st.write(f"• {combo}")
                    
                    # 禁忌症
                    if advice.get('contraindications'):
                        st.write("### 注意事项")
                        for contra in advice['contraindications']:
                            st.warning(contra)
                else:
                    st.info("💡 " + advice.get('recommendation', '暂时不需要药物治疗'))
    
    # 生成完整医疗建议
    st.markdown("---")
    with st.form("完整医疗建议_form"):
        st.write("生成包含生活方式、药物治疗和随访计划的完整医疗建议")
        submitted = st.form_submit_button("生成完整医疗建议", type="secondary")
        
        if submitted:
            with st.spinner("正在生成完整医疗建议..."):
                patient_data = {
                    "patient_id": patient['id'],
                    "age": patient['age'],
                    "gender": patient['gender'],
                    "systolic_bp": patient['systolic_bp'],
                    "diastolic_bp": patient['diastolic_bp'],
                    "smoking": patient['smoking'],
                    "diabetes": patient['diabetes'],
                    "heart_disease": patient['heart_disease'],
                    "kidney_disease": patient['kidney_disease'],
                    "stroke_history": patient['stroke_history'],
                    "family_history": patient['family_history']
                }
                
                result = make_api_request("/ai/generate-advice", "POST", patient_data)
            
            if result:
                st.subheader("完整医疗建议")
                st.write(result['advice'])

def show_knowledge_base():
    """知识库"""
    st.markdown('<div class="sub-header">高血压医学知识库</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["知识搜索", "血压分类", "药物信息"])
    
    with tab1:
        st.subheader("知识搜索")
        
        with st.form("知识搜索_form"):
            query = st.text_input("请输入搜索关键词", placeholder="如：血压分类、危险因素、生活方式等")
            submitted = st.form_submit_button("搜索", type="primary")
            
            if submitted and query:
                result = make_api_request(f"/knowledge/search?query={query}")
                if result:
                    st.markdown(result['result'])
                elif query:
                    st.info("请输入搜索关键词")
    
    with tab2:
        st.subheader("血压分类标准")
        
        with st.form("血压分类_form"):
            st.write("点击按钮查看血压分类标准和相关信息")
            submitted = st.form_submit_button("查看血压分类", type="primary")
            
            if submitted:
                result = make_api_request("/knowledge/blood-pressure-classification")
                if result:
                    st.markdown(result['info'])
    
    with tab3:
        st.subheader("药物信息查询")
        
        with st.form("药物信息_form"):
            drug_type = st.selectbox(
                "选择药物类型",
                ["ACEI", "ARB", "CCB", "利尿剂", "β受体阻滞剂"]
            )
            
            submitted = st.form_submit_button("查看药物信息", type="primary")
            
            if submitted:
                result = make_api_request(f"/knowledge/medication/{drug_type}")
                if result:
                    st.markdown(result['info'])

if __name__ == "__main__":
    # 检查API连接
    try:
        health = make_api_request("/")
        if health:
            main()
        else:
            st.error("无法连接到后端API服务，请确保API服务正在运行。")
    except:
        st.error("无法连接到后端API服务，请确保API服务正在运行在 http://localhost:8000")
        st.info("启动API服务: `uvicorn app.main:app --reload`")