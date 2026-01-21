import urllib.parse
import base64
import streamlit as st
import OtpMigration_pb2
import pyotp
import qrcode
from PIL import Image
from pyzbar.pyzbar import decode as decode_qr
import io

# 页面基础配置
st.set_page_config(
    page_title="Google Authenticator 解析工具",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Google Authenticator 导出数据解析工具")
st.divider()

# ---------------------- 新增函数1：解析二维码图片，提取URL ----------------------
def parse_qr_image(image_file):
    """
    解析上传的二维码图片，提取Google Authenticator导出的URL
    :param image_file: Streamlit上传的图片文件
    :return: 解析出的URL（失败返回None）
    """
    try:
        # 读取图片并解析二维码
        img = Image.open(image_file)
        qr_results = decode_qr(img)
        if not qr_results:
            st.error("❌ 未识别到二维码，请确认图片包含有效二维码！")
            return None
        
        # 提取二维码内容（GA导出的URL）
        qr_content = qr_results[0].data.decode('utf-8')
        # 验证是否为GA导出URL
        if not qr_content.startswith("otpauth-migration://offline?data="):
            st.error("❌ 二维码内容非Google Authenticator导出URL，请确认图片正确！")
            return None
        
        return qr_content
    except Exception as e:
        st.error(f"❌ 解析二维码图片失败：{str(e)}")
        return None

# ---------------------- 新增函数2：生成OTP账户的二维码（用于导入其他验证器） ----------------------
def generate_otp_qr(account_info):
    """
    根据解析出的OTP账户信息，生成标准OTP二维码（兼容所有验证器）
    :param account_info: 解析后的账户信息字典
    :return: 二维码图片的BytesIO对象
    """
    # 构建标准OTP Auth URL（兼容所有OTP验证器）
    otp_type = account_info["验证类型 (Type)"].lower()
    issuer = urllib.parse.quote(account_info["发行方 (Issuer)"])
    name = urllib.parse.quote(account_info["账号名称 (Name)"])
    secret = account_info["OTP密钥 (Base32)"]
    algorithm = account_info["加密算法 (Algorithm)"].lower()
    digits = account_info["验证码位数 (Digits)"]
    period = account_info["TOTP周期 (Period)"]

    # 拼接OTP Auth URL
    if otp_type == "totp":
        otp_url = (
            f"otpauth://{otp_type}/{issuer}:{name}?"
            f"secret={secret}&issuer={issuer}&algorithm={algorithm}"
            f"&digits={digits}&period={period}"
        )
    else:  # HOTP
        counter = account_info["HOTP计数器 (Counter)"]
        otp_url = (
            f"otpauth://{otp_type}/{issuer}:{name}?"
            f"secret={secret}&issuer={issuer}&algorithm={algorithm}"
            f"&digits={digits}&counter={counter}"
        )
    
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(otp_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 转为BytesIO对象（方便Streamlit显示）
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

# ---------------------- 原有解析函数（复用） ----------------------
def parse_ga_export_url(export_url):
    try:
        parsed_url = urllib.parse.urlparse(export_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'data' not in query_params:
            return {"status": "error", "msg": "URL中未找到data参数，请确认是Google Authenticator导出的有效URL"}
        
        data_base64 = query_params['data'][0]
        data_base64 = urllib.parse.unquote(data_base64)
        padding = 4 - (len(data_base64) % 4)
        if padding != 4:
            data_base64 += '=' * padding
        
        binary_data = base64.b64decode(data_base64)
        migration_payload = OtpMigration_pb2.MigrationPayload()
        migration_payload.ParseFromString(binary_data)
        
        type_mapping = {1: "HOTP", 2: "TOTP"}
        algorithm_mapping = {1: "SHA1", 2: "SHA256", 3: "SHA512"}
        otp_accounts = []
        
        for param in migration_payload.otp_parameters:
            account_info = {
                "发行方 (Issuer)": param.issuer,
                "账号名称 (Name)": param.name,
                "OTP密钥 (Base32)": base64.b32encode(param.secret).decode('utf-8'),
                "验证类型 (Type)": type_mapping.get(param.type, "未知"),
                "加密算法 (Algorithm)": algorithm_mapping.get(param.algorithm, "SHA1"),
                "验证码位数 (Digits)": param.digits if param.digits else 6,
                "TOTP周期 (Period)": param.period if param.period else 30,
                "HOTP计数器 (Counter)": param.counter if param.type == 1 else "无（TOTP类型）"
            }
            otp_accounts.append(account_info)
        
        return {"status": "success", "data": otp_accounts}
    
    except base64.binascii.Error as e:
        return {"status": "error", "msg": f"Base64解码失败：{str(e)}"}
    except Exception as e:
        return {"status": "error", "msg": f"解析失败：{str(e)}"}

# ---------------------- 网页交互区域（新增上传功能） ----------------------
tab1, tab2 = st.tabs(["📋 粘贴URL解析", "🖼️ 上传二维码解析"])
export_url = ""

# 标签1：原有粘贴URL功能
with tab1:
    export_url = st.text_area(
        label="请粘贴Google Authenticator导出的二维码URL",
        placeholder="示例：otpauth-migration://offline?data=xxxxxx...",
        height=150
    )

# 标签2：新增上传二维码图片功能
with tab2:
    uploaded_file = st.file_uploader(
        "上传Google Authenticator导出的二维码图片",
        type=["png", "jpg", "jpeg", "webp"],
        help="支持PNG/JPG/WebP格式，请确保图片清晰、无遮挡"
    )
    if uploaded_file is not None:
        # 显示上传的图片预览
        st.image(uploaded_file, caption="上传的二维码预览", width=300)
        # 解析二维码并填充到URL输入框
        with st.spinner("正在解析二维码..."):
            parsed_url = parse_qr_image(uploaded_file)
            if parsed_url:
                export_url = parsed_url
                st.success("✅ 二维码解析成功！已自动填充URL到「粘贴URL解析」标签页")
                # 切换到标签1，方便用户直接解析
                st.session_state.active_tab = 0

# 统一的解析按钮
parse_btn = st.button("开始解析", type="primary")
st.divider()

# ---------------------- 解析逻辑 + 新增二维码生成展示 ----------------------
if parse_btn:
    if not export_url:
        st.error("❌ 请输入有效的Google Authenticator导出URL（或上传二维码图片）！")
    else:
        with st.spinner("正在解析数据..."):
            result = parse_ga_export_url(export_url)
            if result["status"] == "success":
                st.success("✅ 解析成功！以下是提取的账户信息（二维码可直接扫描导入其他验证器）：")
                # 展示每个账户的信息 + 生成的二维码
                for idx, account in enumerate(result["data"], 1):
                    col_left, col_right = st.columns([2, 1])
                    with col_left:
                        with st.expander(f"账户 {idx} 详情", expanded=True):
                            for key, value in account.items():
                                st.write(f"**{key}**：{value}")
                            # 生成测试验证码
                            if account["验证类型 (Type)"] == "TOTP":
                                totp = pyotp.TOTP(account["OTP密钥 (Base32)"])
                                st.write(f"**测试验证码（实时）**：{totp.now()}")
                    with col_right:
                        # 生成并显示OTP二维码
                        qr_img = generate_otp_qr(account)
                        st.image(qr_img, caption=f"账户 {idx} 导入二维码", width=200)
                        # 新增二维码下载按钮
                        st.download_button(
                            label=f"下载账户 {idx} 二维码",
                            data=qr_img,
                            file_name=f"GA_账户{idx}_{account['发行方 (Issuer)']}.png",
                            mime="image/png"
                        )
            else:
                st.error(f"❌ 解析失败：{result['msg']}")

# 侧边栏说明
with st.sidebar:
    st.header("📌 使用说明")
    st.markdown("""
    ### 方式1：粘贴URL解析
    1. 打开Google Authenticator → 导出账户 → 扫描导出二维码（用二维码解析工具）
    2. 复制解析后的URL，粘贴到「粘贴URL解析」标签页
    3. 点击「开始解析」
    
    ### 方式2：上传二维码解析
    1. 截图/保存Google Authenticator导出的二维码图片
    2. 上传到「上传二维码解析」标签页，自动解析URL
    3. 点击「开始解析」
    
    ### 导出二维码使用
    解析后每个账户的二维码可直接扫描导入：
    - 微软验证器、Authy、1Password等OTP工具
    - 支持标准OTP Auth协议的所有验证器
    """)