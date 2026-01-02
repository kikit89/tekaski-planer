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
    # Privzete vrednosti
    if 'yearly_goal' not in st.session_state: st.session_state['yearly_goal'] = 2500.0
    if 'strava_goal' not in st.session_state: st.session_state['strava_goal'] = 300.0
    if 'elev_goal' not in st.session_state: st.session_state['elev_goal'] = 80000.0
    # Katere cilje prikazati?
    if 'show_goals' not in st.session_state: 
        st.session_state['show_goals'] = ["Mesečni cilj", "Strava Izziv", "Letni cilj"]

# --- GLAVNI VMESNIK ---
st.title("🏃‍♀️ Moj Tekaški Trener")
get_settings()

tab1, tab2, tab3 = st.tabs(["📊 Koledar", "➕ Vnos", "⚙️ Nastavitve"])

# --- 3. ZAVIHEK: NASTAVITVE ---
with tab3:
    st.header("Nastavitve Ciljev")
    st.info("Tukaj izberi, katere cilje želiš spremljati na grafu.")
    
    # Izbira aktivnih ciljev
    options = ["Mesečni cilj", "Strava Izziv", "Letni cilj", "Višinci"]
    st.session_state['show_goals'] = st.multiselect(
        "Prikaži cilje:", 
        options, 
        default=st.session_state['show_goals']
    )
    
    st.write("---")
    st.subheader("Vrednosti ciljev")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['yearly_goal'] = st.number_input("Letni cilj (km)", value=st.session_state['yearly_goal'], step=50.0)
        st.session_state['strava_goal'] = st.number_input("Strava Jan (km)", value=st.session_state['strava_goal'], step=10.0)
    with col2:
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

# --- 1. ZAVIHEK: VIZUALIZACIJA (Originalni Dizajn) ---
with tab1:
    df = load_data()
    df['dt'] = pd.to_datetime(df['date'])
    df_jan = df[(df['dt'].dt.year == 2026) & (df['dt'].dt.month == 1)]
    
    # Priprava podatkov
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
    
    # Seznam aktivnih ciljev
    active_goals = st.session_state['show_goals']

    # --- RISANJE GRAFA (Matplotlib) ---
    C_RUN = '#3498db'; C_QUOTA = '#f1c40f'; C_STRAVA = '#FC4C02'; C_ELEV = '#8e44ad'
    C_BG = '#ecf0f1'; C_SUCCESS = '#2ecc71'; C_FAIL = '#e74c3c'; C_PENDING = '#e67e22'
    
    # Prilagodi višino grafa glede na število ciljev
    fig_height = 14 + (len(active_goals) * 1)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.set_xlim(0, 8); ax.set_ylim(-2 - len(active_goals), 7.5); ax.axis('off')

    # Naslov
    ax.text(4, 7.2, 'JANUAR 2026', fontsize=24, fontweight='bold', ha='center', color='#2c3e50')
    
    # Legenda (Dinamična)
    leg_y = 6.7
    ax.add_patch(patches.Circle((1.0, leg_y), 0.15, color=C_RUN)); ax.text(1.3, leg_y, 'Tek', va='center', fontsize=12)
    ax.add_patch(patches.Circle((3.0, leg_y), 0.15, color=C_QUOTA)); ax.text(3.3, leg_y, 'Kvota', va='center', fontsize=12)
    ax.add_patch(patches.Circle((5.0, leg_y), 0.15, color=C_STRAVA)); ax.text(5.3, leg_y, 'Strava', va='center', fontsize=12)
    if "Višinci" in active_goals:
        ax.add_patch(patches.Circle((7.0, leg_y), 0.15, color=C_ELEV)); ax.text(7.3, leg_y, 'Višinci', va='center', fontsize=12)

    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    # Koledar
    cal = calendar.monthcalendar(2026, 1)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned', 'Vsota']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=14, fontweight='bold', color='#34495e')

    for week_idx, week in enumerate(cal):
        w_sum = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=14, fontweight='bold', color='#7f8c8d')
            
            pos_run = (x + 0.25, y + 0.72); pos_quota = (x + 0.25, y + 0.56)
            pos_strava = (x + 0.25, y + 0.40); pos_elev = (x + 0.25, y + 0.24)
            text_off_x = 0.15
            
            if day in data:
                d = data[day]; run_km = d['run']; elev = d['elev']; is_today = d['is_today']
                w_sum += run_km
                
                # Logic: Run OK?
                run_ok = run_km >= 1.6
                quota_ok = run_km >= DAILY_QUOTA
                strava_ok = run_km >= STRAVA_DAILY
                
                # 1. RUN
                if run_ok: 
                    ax.add_patch(patches.Circle(pos_run, 0.07, color=C_RUN))
                    ax.text(pos_run[0], pos_run[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                else: 
                    col = C_PENDING if is_today else C_BG
                    ax.add_patch(patches.Circle(pos_run, 0.07, fill=False, edgecolor=col, lw=2))
                ax.text(pos_run[0]+text_off_x, pos_run[1], f"{run_km:.1f} km", va='center', fontsize=9, fontweight='bold', color=C_SUCCESS if run_ok else C_FAIL)
                
                # 2. QUOTA
                if quota_ok: 
                    ax.add_patch(patches.Circle(pos_quota, 0.07, color=C_QUOTA))
                    ax.text(pos_quota[0], pos_quota[1], '✓', ha='center', va='center', color='white', fontweight='bold', fontsize=9)
                else:
                    col = C_PENDING if is_today else 'salmon'
                    ax.add_patch(patches.Circle(pos_quota, 0.07, fill=False, edgecolor=col, lw=2))
                    ax.text(pos_quota[0], pos_quota[1], '!', ha='center', va='center', color=col, fontweight='bold', fontsize=9)
                ax.text(pos_quota[0]+text_off_x, pos_quota[1], f"{run_km:.1f}/{DAILY_QUOTA:.1f}", va='center', fontsize=8, color='black')

                # 3. STRAVA
                if strava_ok: 
                    ax.add_patch(patches.Circle(pos_strava, 0.07, color=C_STRAVA))
                else:
                    col = C_PENDING if is_today else 'salmon'
                    ax.add_patch(patches.Circle(pos_strava, 0.07, fill=False, edgecolor=col, lw=2))
                ax.text(pos_strava[0]+text_off_x, pos_strava[1], f"{run_km:.1f}/{STRAVA_DAILY:.1f}", va='center', fontsize=8, color='black')
                
                # 4. ELEV (Samo če je vklopljeno)
                if "Višinci" in active_goals and elev > 0:
                     ax.add_patch(patches.Circle(pos_elev, 0.07, color=C_ELEV))
                     ax.text(pos_elev[0]+text_off_x, pos_elev[1], f"+{int(elev)} m", va='center', fontsize=9, color=C_ELEV)
        
        # Tedenska vsota
        if w_sum > 0:
            ax.text(7.5, 5 - week_idx + 0.5, f"{w_sum:.1f}", ha='center', va='center', fontsize=12, fontweight='bold')

    # SPODNJI STOLPCI (Dinamični)
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'NAPREDEK DO CILJA', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.6; y_start = -1.8
    
    total_run_so_far = df_jan['run'].sum()
    total_elev_so_far = df_jan['elev'].sum()
    total_run_year = df[df['dt'].dt.year == 2026]['run'].sum()
    
    # Funkcija za risanje
    def draw_bar(y, val, goal, color, label, unit='km'):
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width, bar_height, facecolor=C_BG, edgecolor='none'))
        pct = val / goal if goal > 0 else 0
        pct = 1 if pct > 1 else pct
        ax.add_patch(patches.Rectangle((bar_x, y), bar_width * pct, bar_height, facecolor=color, edgecolor='none'))
        ax.text(bar_x, y + 0.7, f"{label}", fontsize=12, fontweight='bold', color='#555')
        ax.text(bar_x + bar_width, y + 0.7, f"{val:.1f} / {goal:.0f} {unit}", fontsize=12, fontweight='bold', color='black', ha='right')
        # Manjka
        ax.text(bar_x + bar_width, y + 0.1, f"Manjka: {goal - val:.1f}", fontsize=10, color='red', ha='right')

    current_y = y_start
    if "Mesečni cilj" in active_goals:
        draw_bar(current_y, total_run_so_far, MONTHLY_GOAL, C_RUN, "MESEČNI CILJ"); current_y -= 1.2
    if "Strava Izziv" in active_goals:
        draw_bar(current_y, total_run_so_far, STRAVA_GOAL, C_STRAVA, "STRAVA IZZIV"); current_y -= 1.2
    if "Letni cilj" in active_goals:
        draw_bar(current_y, total_run_year, YEAR_GOAL, C_QUOTA, "LETNI CILJ"); current_y -= 1.2
    if "Višinci" in active_goals:
        draw_bar(current_y, total_elev_so_far, ELEV_GOAL, C_ELEV, "VIŠINSKI METRI", "m"); current_y -= 1.2

    st.pyplot(fig)
