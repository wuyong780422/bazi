import streamlit as st

# 页面基础配置
st.set_page_config(page_title="系统维护", layout="centered")

# 居中展示维护提示
st.markdown("""
<div style="text-align:center;margin-top:120px;">
    <h2 style="color:#666;">🔧 正在维护中，请稍候……</h2>
    <p style="font-size:16px;color:#888;margin-top:20px;">系统升级优化，暂时无法使用，敬请谅解</p >
</div>
""", unsafe_allow_html=True)

# 终止页面后续所有代码运行
st.stop()
