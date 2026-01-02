import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
from datetime import date

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Tekaški Planer 2026", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- PODATKOVNE FUNKCIJE ---
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame(columns=['date', 'run', 'walk', 'elev', 'note'])

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

def get_settings():
    # Privzete vrednosti ciljev
    if 'yearly_goal' not in st.session_state: st.session_state['yearly_goal'] = 2500.0
    if 'strava_goal' not in st.session_state: st.session_state['strava_goal'] = 300.0
    if 'elev_goal' not in st.session_state: st.session_state['elev_goal'] = 80000.0
    
    # Privzete nastavitve prikaza (če še ne obstajajo)
    if 'show_daily_elev' not in st.session_state: st.session_state['show_daily_elev'] = True
    if 'show_run_dot' not in st.session_state: st.session_state['show_run_dot'] = True
    if 'bottom_bars' not in st.session_state: 
        st.session_state['bottom_bars'] = ["Mesečni cilj", "Strava Izziv", "Letni cilj"]

# --- GLAVNI VMESNIK ---
st.title("🏃‍♀️ Moj Tekaški Trener")
get_settings()

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Nastavitve"])

# --- 3. ZAVIHEK: NASTAVITVE ---
with tab3:
    st.header("Nastavitve Prikaza")
    
    st.subheader("👀 Prikaz na koledarju")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.session_state['show_run_dot'] = st.checkbox(
            "Dnevni tek (Modra pika)", 
            value=st.session_state['show_run_dot'],
            help="Prikaže modro piko in kljukico, če si pretekla vsaj 1.6 km."
        )
    with col_v2:
        st.session_state['show_daily_elev'] = st.checkbox(
            "Dnevni višinci (Številka)", 
            value=st.session_state['show_daily_elev'],
            help="Prikaže vijolično številko višincev za vsak dan."
        )

    st.write("---")
    st.subheader("📊 Spodnji stolpci (Cilji)")
    st.info("Izberi, katere napredke želiš spremljati na dnu zaslona.")
    
    options = ["Mesečni cilj", "Strava Izziv", "Letni cilj", "Letni Višinci"]
    st.session_state['bottom_bars'] = st.multiselect(
        "Aktivni stolpci:", 
        options, 
        default=st.session_state['bottom_bars']
    )
    
    st.write("---")
    st.subheader("Vrednosti ciljev")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state['yearly_goal'] = st.number_input("Letni cilj (km)", value=st.session_state['yearly_goal'], step=50.0)
        st.session_state['strava_goal'] = st.number_input("Strava Jan (km)", value=st.session_state['strava_goal'], step=10.0)
    with c2:
        st.session_state['elev_goal'] = st.number_input("Letni višinci (m)", value=st.session_state['elev_goal'], step=1000.0)

# --- 2. ZAVIHEK: VNOS ---
with tab2:
    st.header("Zabeleži aktivnost")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        run = st.number_input("Tek (km)", min_value=0.0, step=0.1, format="%.2f")
        elev = st.number_input("Višinci (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani Aktivnost"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.success(f"Posodobljeno za {d_str}!")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                df = pd.concat([df, new], ignore_index=True)
                st.success(f"Dodano za {d_str}!")
            save_data(df)

# --- 1. ZAVIHEK: VIZUALIZACIJA ---
with tab1:
    df = load_data()
    df['dt'] = pd.to_datetime(df['date'])
    df_jan = df[(df['dt'].dt.year == 2026) & (df['dt'].dt.month == 1)]
    
    data = {}
    for _, row in df_jan.iterrows():
        is_today = (row['dt'].date() == date.today())
        data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': is_today}

    # Cilji
    YEAR_GOAL = st.session_state['yearly_goal']
    STRAVA_GOAL = st.session_state['strava_goal']
    ELEV_GOAL = st.session_state['elev_goal']
    DAILY_QUOTA = YEAR_GOAL / 365.0
    STRAVA_DAILY = STRAVA_GOAL / 31.0
    MONTHLY_GOAL = DAILY_QUOTA * 31
    
    # Nastavitve prikaza
    show_run_dot = st.session_state['show_run_dot']
    show_elev_daily = st.session_state['show_daily_elev']
    active_bars = st.session_state['bottom_bars']

    # --- RISANJE GRAFA ---
    C_RUN = '#3498db'; C_QUOTA = '#f1c40f'; C_STRAVA = '#FC4C02'; C_ELEV = '#8e44ad'
    C_BG = '#ecf0f1'; C_SUCCESS = '#2ecc71'; C_FAIL = '#e74c3c'; C_PENDING = '#e67e22'
    
    # Višina grafa glede na število stolpcev
    bars_count = len(active_bars)
    fig_height = 13 + (bars_count * 1)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.set_xlim(0, 8); ax.set_ylim(-2 - bars_count, 7.5); ax.axis('off')

    # Naslov
    ax.text(4, 7.2, 'JANUAR 2026', fontsize=24, fontweight='bold', ha='center', color='#2c3e50')
    
    # Legenda (Dinamična)
    leg_y = 6.7
    if show_run_dot:
        ax.add_patch(patches.Circle((1.0, leg_y), 0.15, color=C_RUN)); ax.text(1.3, leg_y, 'Tek', va='center', fontsize=12)
    
    # Kvota in Strava sta vezana na spodnje stolpce? 
    # Logično je: če spremljam letni cilj, želim videti rumene pike.
    if "Letni cilj" in active_bars:
        ax.add_patch(patches.Circle((3.0, leg_y), 0.15, color=C_QUOTA)); ax.text(3.3, leg_y, 'Kvota', va='center', fontsize=12)
    
    if "Strava Izziv" in active_bars:
        ax.add_patch(patches.Circle((5.0, leg_y), 0.15, color=C_STRAVA)); ax.text(5.3, leg_y, 'Strava', va='center', fontsize=12)
        
    if show_elev_daily: # Legenda za višince, če so vklopljeni na koledarju
        ax.add_patch(patches.Circle((7
