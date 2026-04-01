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
                
                chapters[c_name].append({
                    "id": m_id,
                    "chats": chat_list,
                    "q": str(row['pertanyaan']),
                    "a": str(row['jawaban']).lower().strip()
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
        st.error(f"Gagal memuat token dari cloud: {e}")
        return []

# --- INITIAL STATE ---
if 'level' not in st.session_state: st.session_state.level = -1 
if 'chapters' not in st.session_state: st.session_state.chapters = load_cloud_data()
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

# **LEVEL -1: HALAMAN AKSES TOKEN CLOUD**
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
            # Refresh token list pas login
            st.session_state.active_tokens_list = get_active_tokens()
            if token_input.strip() in st.session_state.active_tokens_list:
                st.session_state.level = 0
                st.success("Akses Diterima!")
                time.sleep(1)
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
        
        if st.button("✅ Tambah Misi ke List"):
            if new_q and new_a and st.session_state.temp_chats:
                st.session_state.temp_missions.append({
                    "id": m_id_input, "chats": st.session_state.temp_chats, "q": new_q, "a": new_a.lower().strip()
                })
                st.session_state.temp_chats = []
                st.success("Misi masuk list!")
                st.rerun()

        if st.session_state.temp_missions:
            st.write("---")
            st.subheader("📋 Step 3: Copy ke Sheets")
            for m in st.session_state.temp_missions:
                st.write(f"**Sheet AP:**")
                st.code(f"{m['id']}\t{c_name}\t{m['q']}\t{m['a']}")
                st.write(f"**Sheet AP2:**")
                for chat in m['chats']: st.code(f"{m['id']}\t{chat['agent']}\t{chat['msg']}")

    with tab2:
        # --- FITUR RESET & REFRESH TOKEN ---
        st.subheader("🔑 Token & Cloud Manager")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Sync & Refresh Token dari Sheets"):
                st.session_state.active_tokens_list = get_active_tokens()
                st.success("Token List Updated!")
        with col2:
            if st.button("🗑 Reset Session Token (Logout Semu)"):
                st.session_state.active_tokens_list = []
                st.warning("Token list dikosongkan di RAM.")

        st.write("Daftar Token Aktif (RAM):", st.session_state.active_tokens_list)
        
        st.write("---")
        if st.button("🔄 Tarik Data Chapter (Refresh Cloud)"):
            st.session_state.chapters = load_cloud_data()
            st.success("Chapters Synced!")
            st.rerun()
            
    if st.button("Selesai & Kembali"):
        st.session_state.level = 0
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# **LEVEL 0: INTRO**
elif st.session_state.level == 0:
    st.header("📂 Berkas Kasus: Pilih Chapter")
    if st.button("🔎 Sinkronisasi Memori (Refresh Cloud)"):
        st.session_state.chapters = load_cloud_data()
        st.rerun()

    st.markdown('<div class="case-card"><b>CHAPTER 1</b><br>Memori Dasar</div>', unsafe_allow_html=True)
    if st.button("MULAI CHAPTER 1 🔎"): st.session_state.level = 1; st.rerun()

    for i, c_name in enumerate(st.session_state.chapters.keys()):
        num = len(st.session_state.chapters[c_name])
        st.markdown(f'<div class="case-card" style="border-left-color: #4CAF50;"><b>{c_name.upper()}</b><br>{num} Misi Terdeteksi</div>', unsafe_allow_html=True)
        if st.button(f"BUKA BERKAS {i+1} 🚀", key=f"btn_{i}"):
            st.session_state.current_chapter_name = c_name
            st.session_state.current_mission_idx = 0
            st.session_state.level = 50 
            st.rerun()
            
    if st.button("Keluar Sistem 🚪"):
        st.session_state.level = -1
        st.rerun()

# --- CHAPTER 1 ---
elif st.session_state.level == 1:
    st.subheader("KASUS #01: Titik Koordinat Pertama")
    show_chat("Zaki", "Di mana titik pertama kali kita bertemu?")
    show_chat("Dhini", "Hmm, kalau tidak salah itu momen yang sangat grogi buatku.")
    ans = st.text_input("Jawaban:", key="l1")
    if st.button("Verifikasi Lokasi"):
        check_backdoor(ans)
        if "uii" in ans.lower() or "kampus" in ans.lower(): next_level()
        else: st.error("❌ Salah!")

elif 2 <= st.session_state.level <= 9:
    st.write(f"Misi Level {st.session_state.level}"); ans = st.text_input("Jawaban:", key=f"l{st.session_state.level}")
    if st.button("Verifikasi"): check_backdoor(ans); next_level()

# **LEVEL 50: DYNAMIC CHAPTER**
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
        st.header(f"🎉 {c_name} SELESAI!")
        if st.button("Balik ke Menu Utama"): st.session_state.level = 0; st.rerun()

# **LEVEL 10: SURPRISE**
else:
    st.balloons(); st.header("🎉 KASUS TERPECAHKAN! 🎉")
    show_chat("Zaki", "DATABASE PULIH 100%. CEK LACI MEJA KERJAMU! ❤️")
    if st.button("Ulangi"): st.session_state.level = 0; st.rerun()