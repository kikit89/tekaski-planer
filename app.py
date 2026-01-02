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

# --- FUNKCIJE ---
def load_data():
    if os.path.exists(FILE_NAME):
        return pd.read_csv(FILE_NAME)
    else:
        return pd.DataFrame(columns=['date', 'run', 'walk', 'elev', 'note'])

def save_data(df):
    df.to_csv(FILE_NAME, index=False)

def get_settings():
    if 'yearly_goal' not in st.session_state: st.session_state['yearly_goal'] = 2500.0
    if 'strava_goal' not in st.session_state: st.session_state['strava_goal'] = 300.0
    if 'elev_goal' not in st.session_state: st.session_state['elev_goal'] = 80000.0

# --- APLIKACIJA ---
st.title("🏃‍♀️ Moj Tekaški Trener")
get_settings()

tab1, tab2, tab3 = st.tabs(["📊 Pregled", "➕ Vnos", "⚙️ Cilji"])

# ZAVIHEK 3: NASTAVITVE
with tab3:
    st.header("Moji Cilji")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['yearly_goal'] = st.number_input("Letni cilj (km)", value=st.session_state['yearly_goal'], step=50.0)
        st.session_state['strava_goal'] = st.number_input("Strava Jan (km)", value=st.session_state['strava_goal'], step=10.0)
    with col2:
        st.session_state['elev_goal'] = st.number_input("Letni višinci (m)", value=st.session_state['elev_goal'], step=1000.0)
    
    DAILY_QUOTA = st.session_state['yearly_goal'] / 365.0
    st.caption(f"Dnevna kvota: {DAILY_QUOTA:.2f} km")

# ZAVIHEK 2: VNOS
with tab2:
    st.header("Nov vnos")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        run = st.number_input("Tek (km)", min_value=0.0, step=0.1, format="%.2f")
        elev = st.number_input("Višinci (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            
            # Posodobi ali dodaj
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.success(f"Posodobljeno: {d_str}")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                df = pd.concat([df, new], ignore_index=True)
                st.success(f"Dodano: {d_str}")
            save_data(df)

# ZAVIHEK 1: GRAF
with tab1:
    df = load_data()
    # Priprava podatkov
    df['dt'] = pd.to_datetime(df['date'])
    df_jan = df[(df['dt'].dt.year == 2026) & (df['dt'].dt.month == 1)]
    
    total_run = df_jan['run'].sum()
    # Banking logic
    day_year = date.today().timetuple().tm_yday
    surplus = df[df['dt'].dt.year == 2026]['run'].sum() - (DAILY_QUOTA * day_year)
    
    c1, c2 = st.columns(2)
    c1.metric("Januar", f"{total_run:.1f} km")
    c2.metric("Stanje", f"{surplus:+.1f} km", delta_color="normal" if surplus>=0 else "inverse")
    
    # Risanje
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.set_xlim(0, 8); ax.set_ylim(-1, 8); ax.axis('off')
    
    # Legenda
    ax.text(4, 7.5, 'JANUAR 2026', ha='center', fontsize=16, fontweight='bold')
    colors = {'run': '#3498db', 'quota': '#f1c40f', 'strava': '#FC4C02'}
    
    cal = calendar.monthcalendar(2026, 1)
    d_map = df_jan.set_index(df_jan['dt'].dt.day)['run'].to_dict()
    
    for w_i, week in enumerate(cal):
        for d_i, day in enumerate(week):
            if day == 0: continue
            x, y = d_i, 6 - w_i
            ax.add_patch(patches.Rectangle((x, y), 1, 1, fc='white', ec='#ecf0f1'))
            ax.text(x+0.1, y+0.8, str(day), color='gray')
            
            if day in d_map:
                km = d_map[day]
                if km >= 1.6: ax.add_patch(patches.Circle((x+0.5, y+0.5), 0.15, color=colors['run']))
                if km >= DAILY_QUOTA: ax.add_patch(patches.Circle((x+0.8, y+0.5), 0.1, color=colors['quota']))
                if km >= st.session_state['strava_goal']/31: ax.add_patch(patches.Circle((x+0.2, y+0.3), 0.1, color=colors['strava']))
                ax.text(x+0.5, y+0.1, f"{km:.1f}", ha='center', fontsize=8)

    st.pyplot(fig)
