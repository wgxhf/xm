import streamlit as st
from app import app  # 导入刚才改好的 app 实例
import os

st.set_page_config(page_title="AI 旅游助手", layout="wide")

st.title("🗺️ AI 一日游助手")

# 侧边栏显示流程图
with st.sidebar:
    st.header("工作流逻辑")
    try:
        img_data = app.get_graph().draw_mermaid_png()
        st.image(img_data)
    except:
        st.write("流程图加载中...")

# 主界面输入
city = st.text_input("你想去哪个城市？", value="深圳")
interests_raw = st.text_area("你的爱好是什么？（请用逗号分隔）", value="看海, 逛公园")

if st.button("开始规划行程", type="primary"):
    if city and interests_raw:
        with st.spinner("AI 正在为您生成定制化行程..."):
            # 1. 按照 PlannerState 的结构打包数据
            inputs = {
                "city": city,
                "interests": [i.strip() for i in interests_raw.split(",")],
                "messages": []
            }
            
            # 2. 调用 LangGraph 工作流
            result = app.invoke(inputs)
            
            # 3. 展示结果
            st.success("行程生成成功！")
            st.divider()
            st.markdown(result["itinerary"])
    else:
        st.warning("请填入城市和爱好哦！")