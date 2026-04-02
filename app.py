import streamlit as st
import time
import json
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Z&D Case Files: The Ultimate Memory",
    page_icon="🕵️‍♂️",
    layout="centered"
)

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    input, textarea { background-color: #1c1e26 !important; color: white !important; border: 1px solid #3e4149 !important; }
    .chat-zaki {
        background-color: #1E88E5; color: white; padding: 15px; 
        border-radius: 15px 15px 15px 5px; margin-bottom: 15px; max-width: 85%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3); line-height: 1.5;
    }
    .chat-dhini {
        background-color: #2D2D2D; color: white; padding: 15px; 
        border-radius: 15px 15px 5px 15px; margin-bottom: 15px; 
        max-width: 85%; margin-left: auto; text-align: right; border: 1px solid #444;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.3); line-height: 1.5;
    }
    .agent-header { font-weight: bold; font-size: 0.8rem; margin-bottom: 5px; color: #888; }
    .case-card { background: #161b22; padding: 20px; border-left: 5px solid #ff4b4b; border-radius: 10px; margin: 20px 0; }
    .admin-card { background: #1a1c24; padding: 25px; border: 2px dashed #4CAF50; border-radius: 15px; margin-bottom: 20px; }
    .access-card { background: #1a1c24; padding: 30px; border: 1px solid #3e4149; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- LINK SPREADSHEET ---
URL_AP = "https://docs.google.com/spreadsheets/d/1T_18ejVziKwyn6IH7xXDLyMb9KAy7zO2JZsrpailWrw/edit?usp=sharing"
URL_AP2 = "https://docs.google.com/spreadsheets/d/1I_fqFNA_FFsruL7JtLPN4f6kfNwl2-xK8v_V31v241Q/edit?usp=sharing"
URL_AP3 = "https://docs.google.com/spreadsheets/d/1chIInTQ4CnPd0ulxvCo0va9yteyiZev9Z7-s4Yp8yi4/edit?usp=sharing"

def load_cloud_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_misi = conn.read(spreadsheet=URL_AP, ttl="0")
        df_chats = conn.read(spreadsheet=URL_AP2, ttl="0")
        
        chapters = {}
        if not df_misi.empty:
            for _, row in df_misi.iterrows():
                c_name = str(row['nama_chapter'])
                m_id = row['id_misi']
                if c_name not in chapters: chapters[c_name] = []
                
                related_chats = df_chats[df_chats['id_misi'] == m_id] if not df_chats.empty else pd.DataFrame()
                chat_list = []
                for _, c_row in related_chats.iterrows():
                    chat_list.append({"agent": c_row['agent'], "msg": str(c_row['pesan'])})
                
                p_selesai = str(row['pesan_selesai']) if 'pesan_selesai' in df_misi.columns and not pd.isna(row['pesan_selesai']) else "KASUS TERPECAHKAN! ❤️"

                chapters[c_name].append({
                    "id": m_id,
                    "chats": chat_list,
                    "q": str(row['pertanyaan']),
                    "a": str(row['jawaban']).lower().strip(),
                    "finish_msg": p_selesai
                })
        return chapters
    except Exception as e:
        st.error(f"Gagal Sinkronisasi Cloud: {e}")
        return {}

def get_active_tokens():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df_tokens = conn.read(spreadsheet=URL_AP3, ttl="0")
        active_tokens = df_tokens[df_tokens['status'].str.lower() == 'aktif']['token_key'].tolist()
        return [str(t).strip() for t in active_tokens]
    except Exception as e:
        return []

# --- PESAN SELAMAT KHUSUS CHAPTER 1 ---
CHAPTER_1_FINISH_MSG = """Hi adek.

Waw waw, yang ini ditunggu karena ada salah paham dari abang ya hahaha😭, maafkan abang sayaaang ngga bermaksud gitu.

Kalau adek nyelsain semua misi berarti adek udah nyampe sini. Selamat udah nyelsainnya, adek juga sekarang di kondisi yang tidak okay kan. 

Semangat ya adek, terimakasih telah dan selalu menjadi penyemangat abang, ketika ngga ada orang sekitar yang peduli dan peka dengan perasaan abang. Disana adek selalu muncul, abang salah ketika adek sedih abang malah ngga selalu muncul. 

Adek kita harus menjalani ini bersama yaaa, semoga abang lulus tahun ini dan kita bisa ketemu. Main bareng senyum bareng, ketawa bareng, dan bahagia bareng hehe. Ini aja kali dek

I love u moree adek❤️"""

# --- INITIAL STATE ---
if 'level' not in st.session_state: st.session_state.level = -1 
if 'chapters' not in st.session_state: 
    st.session_state.chapters = load_cloud_data()
    
    # TAMBAHKAN CHAPTER 1 LANGSUNG DI CODE DENGAN PESAN BARU
    st.session_state.chapters["Chapter 1"] = [
        {
            "id": 101,
            "chats": [
                {"agent": "Zaki", "msg": "Dhini, inget gak hari pertama kita beneran tatap muka?"},
                {"agent": "Dhini", "msg": "Inget banget! Aku sampe deg-degan parah waktu itu."},
                {"agent": "Zaki", "msg": "Coba tebak, di gedung mana kita pertama kali berdiri di titik yang sama?"}
            ],
            "q": "Di mana titik pertama kali kita bertemu?",
            "a": "terminal leuwi panjang",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 102,
            "chats": [
                {"agent": "Zaki", "msg": "Setelah dari situ, kita gak langsung pulang kan?"},
                {"agent": "Dhini", "msg": "Iya, kita jalan-jalan dulu! Itu kencan pertama yang paling berkesan."},
                {"agent": "Zaki", "msg": "Tempat mana yang pertama kali banget kita datengin?"}
            ],
            "q": "Tempat pertama kali dikunjungi setelah bertemu?",
            "a": "taman maluku",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 103,
            "chats": [
                {"agent": "Zaki", "msg": "Terus pas kita habis mesen makan... ada kejadian tragis."},
                {"agent": "Dhini", "msg": "WKWK sumpah itu memalukan tapi lucu banget!"},
                {"agent": "Zaki", "msg": "Padahal lagi enak-enaknya ngobrol, eh tiba-tiba... apa yang jatuh?"}
            ],
            "q": "Makanan apa yang jatuh (tragis!) saat di motor?",
            "a": "mcd",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 104,
            "chats": [
                {"agent": "Zaki", "msg": "Adek, kalau lagi pengen yang asem dan dingin waktu itu adek suka makan apa?."},
                {"agent": "Dhini", "msg": "Dingin, bikin mood naik!"}
            ],
            "q": "Rasa ice cream apa yang paling adek suka?",
            "a": "yogurt",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 105,
            "chats": [
                {"agent": "Zaki", "msg": "Kita punya tempat makan 'legend' yang kalo bingung mau ke mana, pasti ujungnya ke sini."},
                {"agent": "Dhini", "msg": "Tempat sejuta umat, tapi memori kita paling banyak di sana."},
                {"agent": "Zaki", "msg": "Apalagi lagi kalau pengen yang simpel."}
            ],
            "q": "Tempat makan yang selalu kita kunjungi berdua?",
            "a": "ramen",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 106,
            "chats": [
                {"agent": "Zaki", "msg": "Kalo soal makanan luar negeri, kita paling semangat makan ini."},
                {"agent": "Dhini", "msg": "Pokoknya yang ada nasi gulung atau ikan mentahnya!"}
            ],
            "q": "Makanan Jepang apa yang paling kamu suka?",
            "a": "sushi",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 107,
            "chats": [
                {"agent": "Zaki", "msg": "DANGER! DECODE THE MEMORY."},
                {"agent": "Zaki", "msg": "LOG: Film rilis 2022. GENRE: Horror. STATUS: Pertama kali nonton bareng."},
                {"agent": "Dhini", "msg": "Aduhh aku inget! Yang ada loncengnya dan 'Ibu' datang lagi kan?"}
            ],
            "q": "DECODE: Judul film horror rilis 2022 yang kita tonton bareng pertama kali?",
            "a": "ivanna",
            "finish_msg": CHAPTER_1_FINISH_MSG
        },
        {
            "id": 108,
            "chats": [
                {"agent": "Zaki", "msg": "Inget gak pas kita di Jogja, Maps-nya bikin pusing?"},
                {"agent": "Dhini", "msg": "Bukan Maps-nya, adeknya yang salah baca arah!"},
                {"agent": "Zaki", "msg": "Waktu itu kita harusnya ke UGM, tapi malah nyasar ke arah mana?"}
            ],
            "q": "Salah jalan saat di Jogja, kita malah ambil arah ke mana?",
            "a": "kulonprogo",
            "finish_msg": CHAPTER_1_FINISH_MSG
        }
    ]

if 'current_chapter_name' not in st.session_state: st.session_state.current_chapter_name = ""
if 'current_mission_idx' not in st.session_state: st.session_state.current_mission_idx = 0
if 'temp_missions' not in st.session_state: st.session_state.temp_missions = []
if 'temp_chats' not in st.session_state: st.session_state.temp_chats = []
if 'active_tokens_list' not in st.session_state: st.session_state.active_tokens_list = get_active_tokens()

# --- FUNGSI HELPER ---
def show_chat(agent, message):
    if not message or message == "nan": return
    if agent == "Zaki":
        st.markdown(f'<div class="agent-header">🕵️‍♂️ Agent Zaki</div><div class="chat-zaki">{message}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="agent-header" style="text-align:right;">🕵️‍♀️ Agent Dhini</div><div class="chat-dhini">{message}</div>', unsafe_allow_html=True)

def check_backdoor(user_input):
    if user_input.lower().strip() == "rahasia":
        st.session_state.level = 100 
        st.rerun()

def next_level():
    st.session_state.level += 1
    st.balloons()
    st.rerun()

# --- ALUR GAME ---
st.title("🕵️‍♂️ Z&D Detective Agency")

# **LEVEL -1: HALAMAN AKSES**
if st.session_state.level == -1:
    st.markdown('<div class="access-card">', unsafe_allow_html=True)
    st.subheader("🔐 Cloud Restricted Access")
    st.write("Sistem terenkripsi. Masukkan token dari database.")
    token_input = st.text_input("Access Token:", type="password", key="gate_token")
    if st.button("Verifikasi Identitas 🚀"):
        if token_input.lower().strip() == "rahasia":
            st.session_state.level = 100
            st.rerun()
        else:
            st.session_state.active_tokens_list = get_active_tokens()
            if token_input.strip() in st.session_state.active_tokens_list:
                st.session_state.level = 0
                st.rerun()
            else:
                st.error("Token Tidak Dikenali atau Nonaktif!")
    st.markdown('</div>', unsafe_allow_html=True)

# **LEVEL 100: ADMIN MODE**
elif st.session_state.level == 100:
    st.markdown('<div class="admin-card">', unsafe_allow_html=True)
    st.header("🛠 Admin System: Builder")
    tab1, tab2 = st.tabs(["Manual Input", "JSON & Token Control"])
    with tab1:
        st.subheader("Buat Chapter & Misi")
        c_name = st.text_input("Nama Chapter:", placeholder="Contoh: Chapter 2")
        m_id_input = st.number_input("ID Misi:", min_value=1, step=1)
        st.write("---")
        st.write("**Step 1: Obrolan**")
        col_a, col_b = st.columns([1, 4])
        with col_a: char_opt = st.selectbox("Siapa?", ["Zaki", "Dhini"])
        with col_b: msg_input = st.text_input("Isi Chat:")
        if st.button("➕ Tambah Chat"):
            if msg_input:
                st.session_state.temp_chats.append({"agent": char_opt, "msg": msg_input})
                st.rerun()
        for c in st.session_state.temp_chats: st.text(f"[{c['agent']}]: {c['msg']}")
        if st.button("🗑 Reset Obrolan Misi Ini"):
            st.session_state.temp_chats = []
            st.rerun()
        st.write("---")
        st.write("**Step 2: Detail**")
        new_q = st.text_input("Pertanyaan:")
        new_a = st.text_input("Jawaban:")
        finish_msg_input = st.text_area("Pesan Selesai Chapter (Costume):", placeholder="Muncul saat chapter selesai")
        if st.button("✅ Tambah Misi ke List"):
            if new_q and new_a and st.session_state.temp_chats:
                st.session_state.temp_missions.append({
                    "id": m_id_input, 
                    "chats": st.session_state.temp_chats, 
                    "q": new_q, 
                    "a": new_a.lower().strip(),
                    "finish_msg": finish_msg_input if finish_msg_input else "KASUS TERPECAHKAN! ❤️"
                })
                st.session_state.temp_chats = []
                st.success("Misi masuk list!")
                st.rerun()
        if st.session_state.temp_missions:
            st.write("---")
            st.subheader("📋 Step 3: Copy ke Sheets")
            for m in st.session_state.temp_missions:
                st.write(f"**Sheet AP:**")
                st.code(f"{m['id']}\t{c_name}\t{m['q']}\t{m['a']}\t{m['finish_msg']}")
                st.write(f"**Sheet AP2:**")
                for chat in m['chats']: st.code(f"{m['id']}\t{chat['agent']}\t{chat['msg']}")
    with tab2:
        st.subheader("🔑 Token & Cloud Manager")
        if st.button("🔄 Sync & Refresh Cloud"):
            st.session_state.chapters = load_cloud_data()
            st.session_state.active_tokens_list = get_active_tokens()
            st.success("Data Updated!")
    if st.button("Selesai & Kembali"):
        st.session_state.level = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# **LEVEL 0: INTRO**
elif st.session_state.level == 0:
    st.header("📂 Berkas Kasus: Pilih Chapter")
    if st.button("🔎 Refresh Cloud"):
        st.session_state.chapters = load_cloud_data()
        st.rerun()
    for i, c_name in enumerate(st.session_state.chapters.keys()):
        num = len(st.session_state.chapters[c_name])
        border_color = "#ff4b4b" if c_name == "Chapter 1" else "#4CAF50"
        st.markdown(f'<div class="case-card" style="border-left-color: {border_color};"><b>{c_name.upper()}</b><br>{num} Misi Terdeteksi</div>', unsafe_allow_html=True)
        if st.button(f"BUKA BERKAS {i+1} 🚀", key=f"btn_{i}"):
            st.session_state.current_chapter_name = c_name
            st.session_state.current_mission_idx = 0
            st.session_state.level = 50 
            st.rerun()
    if st.button("Keluar Sistem 🚪"):
        st.session_state.level = -1
        st.rerun()

# **LEVEL 50: DYNAMIC CHAPTER ENGINE**
elif st.session_state.level == 50:
    c_name = st.session_state.current_chapter_name
    missions = st.session_state.chapters.get(c_name, [])
    idx = st.session_state.current_mission_idx
    if idx < len(missions):
        st.header(f"🕵️‍♀️ {c_name}")
        for chat in missions[idx]["chats"]: show_chat(chat["agent"], chat["msg"])
        st.markdown(f'<div class="case-card"><b>MISI:</b> {missions[idx]["q"]}</div>', unsafe_allow_html=True)
        ans_dyn = st.text_input("Jawaban Dhini:", key=f"dyn_{idx}")
        if st.button("Verifikasi Bukti"):
            check_backdoor(ans_dyn)
            if ans_dyn.lower().strip() == missions[idx]["a"]:
                st.session_state.current_mission_idx += 1; st.balloons(); st.rerun()
            else: st.error("Gagal! Coba ingat lagi.")
    else:
        last_msg = missions[-1]["finish_msg"] if missions else "KASUS TERPECAHKAN! ❤️"
        st.session_state.last_finish_msg = last_msg
        st.session_state.level = 10 
        st.rerun()

# **LEVEL 10: SURPRISE**
else:
    st.balloons()
    st.header("🎉 BERKAS SELESAI! 🎉")
    msg = st.session_state.get('last_finish_msg', "DATABASE PULIH 100% ❤️")
    # Tampilan pesan panjang dengan line breaks yang benar
    st.markdown(f'<div class="chat-zaki" style="max-width:100%;">{msg.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
    if st.button("Kembali ke Menu Utama"): 
        st.session_state.level = 0
        st.rerun()