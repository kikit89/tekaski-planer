import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import calendar
import os
import uuid
from datetime import date, datetime

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Tekaški Planer", layout="centered", page_icon="🏃‍♀️")
FILE_NAME = 'teki_data.csv'

# --- PODATKI ---
def load_data():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        df['dt'] = pd.to_datetime(df['date'])
        return df
    else:
        # Začetni podatki
        data = {
            'date': ['2026-01-01', '2026-01-02'],
            'run': [6.93, 8.34],
            'walk': [1.6, 1.6],
            'elev': [76, 57],
            'note': ['Začetek', 'Nadaljevanje']
        }
        df = pd.DataFrame(data)
        df['dt'] = pd.to_datetime(df['date'])
        return df

def save_data(df):
    df_save = df.drop(columns=['dt'])
    df_save.to_csv(FILE_NAME, index=False)

def init_settings():
    # Inicializacija seznama ciljev
    if 'goals_list' not in st.session_state:
        st.session_state['goals_list'] = [
            {'id': 'g1', 'name': 'Letni Plan', 'color': '#f1c40f', 'goal': 2500.0, 'type': 'Letni', 'unit': 'km', 'active': True},
            {'id': 'g2', 'name': 'Strava Izziv', 'color': '#FC4C02', 'goal': 300.0, 'type': 'Mesečni', 'unit': 'km', 'active': True},
            {'id': 'g3', 'name': 'Hribi', 'color': '#8e44ad', 'goal': 80000.0, 'type': 'Letni', 'unit': 'm', 'active': True},
        ]
    
    # Ali prikažemo podrobno razčlenitev (teden/mesec) pod glavnim stolpcem?
    if 'show_breakdown' not in st.session_state: st.session_state['show_breakdown'] = True

# --- APLIKACIJA ---
init_settings()
st.title("🏃‍♀️ Moj Planer")

tab1, tab2, tab3 = st.tabs(["📊 Koledar & Analiza", "➕ Vnos", "⚙️ Nastavitve"])

# ==============================================================================
# ZAVIHEK 3: NASTAVITVE (DODAJANJE/BRISANJE)
# ==============================================================================
with tab3:
    st.header("📋 Urejanje Ciljev")
    
    st.subheader("Splošne nastavitve")
    st.session_state['show_breakdown'] = st.checkbox("Prikaži podrobno razčlenitev (Mesečno/Tedensko) pod vsakim ciljem", 
                                                     value=st.session_state['show_breakdown'])
    st.write("---")

    # SEZNAM CILJEV
    goals_to_remove = []
    for i, g in enumerate(st.session_state['goals_list']):
        with st.expander(f"{g['name']} ({g['type']})", expanded=False):
            c1, c2 = st.columns([1, 3])
            with c1: g['color'] = st.color_picker("Barva", g['color'], key=f"c_{g['id']}")
            with c2: g['name'] = st.text_input("Ime", g['name'], key=f"n_{g['id']}")
            
            c3, c4, c5 = st.columns(3)
            with c3: g['goal'] = st.number_input("Cilj", value=float(g['goal']), key=f"g_{g['id']}")
            with c4: g['type'] = st.selectbox("Tip", ["Letni", "Mesečni"], index=0 if g['type']=="Letni" else 1, key=f"t_{g['id']}")
            with c5: g['unit'] = st.selectbox("Enota", ["km", "m"], index=0 if g.get('unit','km')=="km" else 1, key=f"u_{g['id']}")
            
            g['active'] = st.checkbox("Prikaži na koledarju", value=g['active'], key=f"a_{g['id']}")
            
            if st.button(f"Izbriši {g['name']}", key=f"del_{g['id']}"):
                goals_to_remove.append(i)

    if goals_to_remove:
        for index in sorted(goals_to_remove, reverse=True):
            del st.session_state['goals_list'][index]
        st.rerun()

    st.write("---")
    st.subheader("➕ Nov Cilj")
    with st.form("new_goal"):
        n_name = st.text_input("Ime")
        c1, c2 = st.columns(2)
        with c1: n_goal = st.number_input("Vrednost", value=100.0)
        with c2: n_unit = st.selectbox("Enota", ["km", "m"])
        n_type = st.selectbox("Tip", ["Mesečni", "Letni"])
        n_color = st.color_picker("Barva", "#00ff00")
        
        if st.form_submit_button("Dodaj"):
            new_id = str(uuid.uuid4())[:8]
            st.session_state['goals_list'].append({
                'id': new_id, 'name': n_name, 'color': n_color, 'goal': n_goal, 
                'type': n_type, 'unit': n_unit, 'active': True
            })
            st.rerun()

# ==============================================================================
# ZAVIHEK 2: VNOS
# ==============================================================================
with tab2:
    st.header("Nov vnos")
    with st.form("entry"):
        d_date = st.date_input("Datum", value=date.today())
        run = st.number_input("Razdalja (km)", min_value=0.0, step=0.1, format="%.2f")
        elev = st.number_input("Višina (m)", min_value=0, step=10)
        note = st.text_input("Opomba")
        
        if st.form_submit_button("Shrani"):
            df = load_data()
            d_str = d_date.strftime("%Y-%m-%d")
            if d_str in df['date'].values:
                df.loc[df['date'] == d_str, ['run', 'elev', 'note']] = [run, elev, note]
                st.toast(f"Posodobljeno!")
            else:
                new = pd.DataFrame({'date': [d_str], 'run': [run], 'walk': [0], 'elev': [elev], 'note': [note]})
                new['dt'] = pd.to_datetime(new['date'])
                df = pd.concat([df, new], ignore_index=True)
                st.toast(f"Shranjeno!")
            save_data(df)

# ==============================================================================
# ZAVIHEK 1: VIZUALIZACIJA
# ==============================================================================
with tab1:
    df = load_data()
    if 'dt' not in df.columns: df['dt'] = pd.to_datetime(df['date'])
    
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # Filtriranje za koledar (samo trenutni mesec)
    df_month_view = df[(df['dt'].dt.year == current_year) & (df['dt'].dt.month == current_month)]
    
    # Podatki po dnevih za hitro iskanje
    day_data = {}
    for _, row in df_month_view.iterrows():
        day_data[row['dt'].day] = {'run': row['run'], 'elev': row['elev'], 'is_today': (row['dt'].date() == today)}

    # Priprava globalnih spremenljivk
    day_of_year = today.timetuple().tm_yday
    day_of_month = today.day
    days_in_year = 366 if calendar.isleap(current_year) else 365
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    
    current_week_num = today.isocalendar()[1]
    # Popravek za teden: koliko dni je minilo v tem tednu?
    current_weekday_iso = today.isocalendar()[2] # 1=Pon
    
    # --- PRIPRAVA PODATKOV ZA CILJE ---
    active_goals_calendar = [g for g in st.session_state['goals_list'] if g['active']]
    
    # -----------------------------------------------------------
    # 1. RISANJE KOLEDARJA
    # -----------------------------------------------------------
    C_BG = '#ecf0f1'; C_PENDING = '#e67e22'; C_TEXT = '#2c3e50'; C_GOOD = '#27ae60'; C_BAD = '#c0392b'
    
    # Dinamična višina glede na število ciljev spodaj
    # Vsak cilj vzame nekaj prostora + če je breakdown vklopljen, vzame še več
    bars_height_est = 0
    for g in st.session_state['goals_list']:
        bars_height_est += 1.2
        if st.session_state['show_breakdown']:
            if g['type'] == 'Letni': bars_height_est += 2.0 # mesec + teden
            else: bars_height_est += 1.0 # samo teden

    fig_height = 10 + bars_height_est
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    # Y limit moramo prilagoditi, da gre dovolj globoko za vse stolpce
    ax.set_xlim(0, 8); ax.set_ylim(-2 - bars_height_est, 7.5); ax.axis('off')

    # Naslov
    SLO_MONTHS = {1:"JANUAR", 2:"FEBRUAR", 3:"MAREC", 4:"APRIL", 5:"MAJ", 6:"JUNIJ", 7:"JULIJ", 8:"AVGUST", 9:"SEPTEMBER", 10:"OKTOBER", 11:"NOVEMBER", 12:"DECEMBER"}
    ax.text(4, 7.2, f'{SLO_MONTHS.get(current_month, "")} {current_year}', fontsize=24, fontweight='bold', ha='center', color=C_TEXT)
    
    # Legenda
    leg_y = 6.7
    num_leg = len(active_goals_calendar)
    if num_leg > 0:
        step = 8 / (num_leg + 1)
        for i, g in enumerate(active_goals_calendar):
            px = step * (i + 1)
            ax.add_patch(patches.Circle((px, leg_y), 0.15, color=g['color']))
            ax.text(px + 0.3, leg_y, g['name'], va='center', fontsize=11)

    ax.plot([0, 8], [6.4, 6.4], color='#bdc3c7', lw=2)

    # Dnevi
    cal = calendar.monthcalendar(current_year, current_month)
    days_of_week = ['Pon', 'Tor', 'Sre', 'Čet', 'Pet', 'Sob', 'Ned', 'Vsota']
    for i, dname in enumerate(days_of_week):
        ax.text(i + 0.5, 6.1, dname, ha='center', va='center', fontsize=14, fontweight='bold', color='#34495e')

    # Grid in Pike
    for week_idx, week in enumerate(cal):
        w_sum_dist = 0; w_sum_elev = 0
        for day_idx, day in enumerate(week):
            x = day_idx; y = 5 - week_idx
            # Okvirček
            rect = patches.Rectangle((x, y), 1, 1, fill=True, facecolor='white', edgecolor='#ecf0f1', linewidth=2)
            ax.add_patch(rect)
            
            if day == 0: continue
            
            ax.text(x + 0.05, y + 0.85, str(day), fontsize=14, fontweight='bold', color='#7f8c8d')
            
            # --- POPRAVLJENA LOGIKA POZICIJ PIK ---
            # Pike morajo biti znotraj (x, y) do (x+1, y+1)
            # Y gre od spodaj navzgor.
            # Začnemo pri y + 0.7 in gremo dol
            
            if num_leg > 0:
                # Koliko prostora ima ena pika?
                space = 0.6 / num_leg 
                start_y_dots = y + 0.75
                
                # Pridobi podatke za ta dan
                daily_vals = day_data.get(day, {'run':0, 'elev':0, 'is_today':False})
                val_km = daily_vals['run']
                val_m = daily_vals['elev']
                is_today = daily_vals['is_today']
                
                w_sum_dist += val_km
                w_sum_elev += val_m
                
                for i, g in enumerate(active_goals_calendar):
                    dot_y = start_y_dots - (i * space)
                    
                    # Izračun cilja za ta dan (povprečje)
                    target_val = g['goal'] / (days_in_year if g['type']=='Letni' else days_in_month)
                    
                    current_val = val_m if g['unit']=='m' else val_km
                    
                    # Risanje pike (Če je podatek > 0 ali če je danes)
                    has_data = current_val > 0
                    
                    if has_data or is_today:
                        ok = current_val >= target_val
                        col = g['color'] if ok else (C_PENDING if is_today else 'salmon')
                        
                        if ok:
                            ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, color=col))
                            # Kljukica samo če ni gneče
                            if num_leg <= 3: ax.text(x+0.25, dot_y, '✓', ha='center', va='center', color='white', fontsize=7, fontweight='bold')
                        else:
                            ax.add_patch(patches.Circle((x+0.25, dot_y), 0.07, fill=False, edgecolor=col, lw=2))
                        
                        # Tekst zraven (samo za prvi cilj ali če je malo ciljev)
                        if num_leg <= 2 or i == 0 or g['unit']=='m':
                            txt = f"{int(current_val)}" if g['unit']=='m' else f"{current_val:.1f}"
                            ax.text(x+0.4, dot_y, txt, va='center', fontsize=8, color='black')

        # Tedenska vsota
        if w_sum_dist > 0:
            ax.text(7.5, 5 - week_idx + 0.5, f"{w_sum_dist:.1f}", ha='center', va='center', fontsize=10, fontweight='bold', color='#555')

    # -----------------------------------------------------------
    # 2. RISANJE STOLPCEV SPODAJ (PAMETNA RAZČLENITEV)
    # -----------------------------------------------------------
    ax.plot([0, 8], [-0.2, -0.2], color='#bdc3c7', lw=2) 
    ax.text(4, -0.8, 'NAPREDEK', fontsize=18, fontweight='bold', ha='center', color='#2c3e50')
    
    bar_x = 0.5; bar_width = 7; bar_height = 0.6; y_cursor = -2.0
    
    # Pomožna funkcija za risanje enega traku
    def draw_single_bar(y, val, goal, color, label, target_val=None, unit='km', is_sub=False):
        # Če je pod-trak (sub), ga malo zamaknemo in pomanjšamo
        bx = bar_x + 0.5 if is_sub else bar_x
        bw = bar_width - 0.5 if is_sub else bar_width
        
        # Ozadje
        ax.add_patch(patches.Rectangle((bx, y), bw, bar_height, facecolor=C_BG, edgecolor='none'))
        # Polnilo
        pct = val / goal if goal > 0 else 0
        if pct > 1: pct = 1
        ax.add_patch(patches.Rectangle((bx, y), bw * pct, bar_height, facecolor=color, edgecolor='none'))
        
        # Status (Semafor)
        status_txt = ""
        status_col = 'black'
        if target_val is not None:
            diff = val - target_val
            status_col = C_GOOD if diff >= 0 else C_BAD
            status_txt = f"{diff:+.1f}"
            
            # Marker
            tpct = target_val / goal if goal > 0 else 0
            if tpct > 1: tpct = 1
            tpos = bx + (bw * tpct)
            ax.plot([tpos, tpos], [y, y+bar_height], color='black', alpha=0.6, linestyle=':')

        # Tekst
        font_w = 'normal' if is_sub else 'bold'
        ax.text(bx, y + 0.7, label, fontsize=11, fontweight=font_w, color='#555')
        
        # Desni izpis: Vrednost in Status
        right_txt = f"{val:.1f}/{goal:.0f} {unit}"
        if status_txt:
            right_txt += f" ({status_txt})"
        
        ax.text(bx + bw, y + 0.7, right_txt, fontsize=11, fontweight='bold', color=status_col if status_txt else 'black', ha='right')

    # GLAVNA ZANKA ČEZ VSE CILJE
    for g in st.session_state['goals_list']:
        # 1. Priprava podatkov za GLAVNI trak
        g_val = g['goal']
        g_col = g['color']
        g_unit = g['unit']
        
        # Accum: Koliko smo naredili?
        # Če je Letni cilj -> vsota celega leta
        # Če je Mesečni cilj -> vsota meseca
        if g['type'] == 'Letni':
            main_accum = df[df['dt'].dt.year == current_year]['run' if g_unit=='km' else 'elev'].sum()
            # Target do danes: (Cilj / Dni v letu) * Današnji dan
            main_target = (g_val / days_in_year) * day_of_year
            main_label = f"{g['name']} (Letni)"
        else:
            main_accum = df_month_view['run' if g_unit=='km' else 'elev'].sum()
            main_target = (g_val / days_in_month) * day_of_month
            main_label = f"{g['name']} (Mesečni)"
            
        # Nariši GLAVNI trak
        draw_single_bar(y_cursor, main_accum, g_val, g_col, main_label, target_val=main_target, unit=g_unit)
        y_cursor -= 1.2
        
        # 2. RAZČLENITEV (Če je vklopljeno)
        if st.session_state['show_breakdown']:
            
            # A) Mesečni del (Samo za Letne cilje)
            if g['type'] == 'Letni':
                # Cilj za ta mesec = dnevno povprečje * dni v mesecu
                sub_goal = (g_val / days_in_year) * days_in_month
                sub_accum = df_month_view['run' if g_unit=='km' else 'elev'].sum()
                sub_target = (g_val / days_in_year) * day_of_month
                
                draw_single_bar(y_cursor, sub_accum, sub_goal, g_col, f"↳ {SLO_MONTHS.get(current_month)} (Del letnega plana)", 
                                target_val=sub_target, unit=g_unit, is_sub=True)
                y_cursor -= 1.0

            # B) Tedenski del (Za Letne in Mesečne)
            # Cilj za teden = dnevno povprečje * 7
            daily_avg = (g_val / days_in_year) if g['type'] == 'Letni' else (g_val / days_in_month)
            sub_goal_week = daily_avg * 7
            
            # Izračun tedenske vsote
            df['week_num'] = df['dt'].dt.isocalendar().week
            week_accum = df[(df['dt'].dt.year == current_year) & (df['week_num'] == current_week_num)]['run' if g_unit=='km' else 'elev'].sum()
            
            # Target do danes v tednu
            active_days_week = current_weekday_iso 
            # (Tukaj bi lahko dodali fix za prvi teden, a za preprostost pustimo standard)
            sub_target_week = daily_avg * active_days_week
            
            draw_single_bar(y_cursor, week_accum, sub_goal_week, g_col, f"↳ Trenutni teden", 
                            target_val=sub_target_week, unit=g_unit, is_sub=True)
            y_cursor -= 1.2 # Malo večji razmik do naslednjega cilja

    st.pyplot(fig)
