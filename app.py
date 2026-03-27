import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# Configuración general
# =========================
st.set_page_config(
    page_title="ENKO Solutions | Dashboard de Aliados",
    page_icon="📊",
    layout="wide"
)

# Paleta inspirada en el logo compartido
ENKO_PURPLE = "#6F35A5"
ENKO_PURPLE_DARK = "#4C2373"
ENKO_PURPLE_LIGHT = "#8E52C4"
ENKO_ORANGE = "#F29A38"
ENKO_BG = "#F7F4FB"
ENKO_WHITE = "#FFFFFF"
ENKO_TEXT = "#2D1E3F"
ENKO_MUTED = "#8B7FA3"

DATA_PATH = os.getenv("ENKO_DATA_PATH", "data/dashboard_usuarios.xlsx")
ACCESS_PATH = os.getenv("ENKO_ACCESS_PATH", "config/accesos_ejemplo.csv")
SHEET_NAME = os.getenv("ENKO_SHEET_NAME", "Reporte Detallado de Usuarios")
LOGO_PATH = os.getenv("ENKO_LOGO_PATH", "assets/logo_enko.png")

# =========================
# Estilos
# =========================
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {ENKO_BG};
            color: {ENKO_TEXT};
        }}
        .main .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}
        /* Fuerza contraste adecuado en textos generales de Streamlit */
        .stApp, .stApp p, .stApp span, .stApp label,
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
            color: {ENKO_TEXT} !important;
        }}
        .enko-header, .enko-header * {{
            color: #FFFFFF !important;
        }}
        .small-note {{
            color: {ENKO_MUTED} !important;
        }}
        /* Ajustes visuales para widgets */
        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {{
            border-radius: 12px !important;
        }}
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stDateInput"] label,
        div[data-testid="stMultiSelect"] label {{
            color: {ENKO_TEXT} !important;
            font-weight: 600 !important;
        }}
        .enko-header {{
            background: linear-gradient(135deg, {ENKO_PURPLE_LIGHT} 0%, {ENKO_PURPLE_DARK} 100%);
            border-radius: 18px;
            padding: 22px 28px;
            margin-bottom: 1rem;
            color: white;
        }}
        .enko-title {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.1rem;
        }}
        .enko-subtitle {{
            font-size: 1rem;
            opacity: 0.95;
        }}
        .kpi-card {{
            background-color: white;
            border-radius: 16px;
            padding: 18px 20px;
            box-shadow: 0 2px 10px rgba(76, 35, 115, 0.08);
            border-left: 6px solid %s;
        }}
        .kpi-label {{
            color: %s;
            font-size: 0.92rem;
            margin-bottom: 0.35rem;
            font-weight: 600;
        }}
        .kpi-value {{
            color: %s;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.1;
        }}
        .section-card {{
            background-color: white;
            border-radius: 18px;
            padding: 18px 18px 8px 18px;
            box-shadow: 0 2px 10px rgba(76, 35, 115, 0.08);
            margin-bottom: 1rem;
        }}
        .filter-card {{
            background-color: white;
            border-radius: 16px;
            padding: 18px 18px 6px 18px;
            box-shadow: 0 2px 10px rgba(76, 35, 115, 0.08);
            margin-bottom: 1rem;
        }}
        div[data-testid="stMetric"] {{
            background-color: white;
            border-radius: 16px;
            padding: 14px;
            border: 1px solid #ECE6F5;
        }}
        .small-note {{
            color: %s;
            font-size: 0.88rem;
        }}
        .login-box {{
            background-color: white;
            padding: 24px;
            border-radius: 18px;
            box-shadow: 0 2px 10px rgba(76, 35, 115, 0.10);
            border-top: 6px solid %s;
        }}
    </style>
    """ % (ENKO_ORANGE, ENKO_MUTED, ENKO_TEXT, ENKO_MUTED, ENKO_ORANGE),
    unsafe_allow_html=True
)

# =========================
# Utilidades
# =========================
def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()

def format_int(value):
    try:
        return f"{int(round(float(value))):,}".replace(",", ",")
    except Exception:
        return "0"

def format_pct(value):
    try:
        return f"{value:.1%}"
    except Exception:
        return "0.0%"

def safe_parse_datetime(series):
    parsed = pd.to_datetime(series, format="%Y/%m/%d %H:%M", errors="coerce")
    if parsed.isna().all():
        parsed = pd.to_datetime(series, errors="coerce")
    return parsed

@st.cache_data(show_spinner=False)
def load_access_table(path):
    access = pd.read_csv(path)
    required = {"aliado", "clave"}
    missing = required - set(access.columns)
    if missing:
        raise ValueError(f"Faltan columnas en accesos: {', '.join(sorted(missing))}")
    access["aliado_norm"] = access["aliado"].map(normalize_text)
    if "activo" not in access.columns:
        access["activo"] = 1
    access = access[access["activo"].fillna(1).astype(int) == 1].copy()
    return access

@st.cache_data(show_spinner=False)
def load_data(path, sheet_name):
    xls = pd.ExcelFile(path)
    target_sheet = sheet_name if sheet_name in xls.sheet_names else xls.sheet_names[0]
    df = pd.read_excel(path, sheet_name=target_sheet)

    # Limpieza base
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").copy()

    required_cols = [
        "Aliado", "Nombre completo", "Lada", "Teléfono", "Correo usuario", "Género",
        "Sector", "Giro", "Lecciones completadas", "Fecha de registro", "Último acceso"
    ]
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA

    # Tipos y transformaciones
    df["Aliado"] = df["Aliado"].astype(str).str.strip()
    df = df[df["Aliado"].notna() & (df["Aliado"] != "nan") & (df["Aliado"] != "")].copy()
    df["aliado_norm"] = df["Aliado"].map(normalize_text)

    df["Nombre completo"] = df["Nombre completo"].fillna("Sin nombre").astype(str).str.strip()
    df["Lada"] = df["Lada"].fillna("").astype(str).str.replace(".0", "", regex=False).str.strip()
    df["Teléfono"] = df["Teléfono"].fillna("").astype(str).str.replace(".0", "", regex=False).str.strip()
    df["Correo usuario"] = df["Correo usuario"].fillna("Sin dato").astype(str).str.strip()
    df["Género"] = df["Género"].fillna("Sin dato").replace("", "Sin dato")
    df["Sector"] = df["Sector"].fillna("Sin dato").replace("", "Sin dato")
    df["Giro"] = df["Giro"].fillna("Sin dato").replace("", "Sin dato")

    df["Lecciones completadas"] = pd.to_numeric(df["Lecciones completadas"], errors="coerce").fillna(0)
    df["Fecha de registro_dt"] = safe_parse_datetime(df["Fecha de registro"])
    df["Último acceso_dt"] = safe_parse_datetime(df["Último acceso"])
    df["fecha_registro_dia"] = df["Fecha de registro_dt"].dt.date

    df["estatus_usuario"] = df["Lecciones completadas"].apply(
        lambda x: "Activo" if pd.notna(x) and x >= 1 else "Registrado"
    )

    # Columnas de salida legibles
    df["Fecha de registro_fmt"] = df["Fecha de registro_dt"].dt.strftime("%Y-%m-%d %H:%M").fillna("Sin dato")
    df["Último acceso_fmt"] = df["Último acceso_dt"].dt.strftime("%Y-%m-%d %H:%M").fillna("Sin dato")

    return df

def build_line_chart(data, x_col, y_col, title, color):
    fig = px.line(
        data,
        x=x_col,
        y=y_col,
        markers=True,
        title=title
    )
    fig.update_traces(line=dict(color=color, width=3), marker=dict(size=7))
    fig.update_layout(
        template="plotly_white",
        title_font=dict(size=18, color=ENKO_TEXT),
        plot_bgcolor=ENKO_WHITE,
        paper_bgcolor=ENKO_WHITE,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title="",
        yaxis_title="",
        font=dict(color=ENKO_TEXT),
        hovermode="x unified",
        legend_title_text=""
    )
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(color=ENKO_TEXT, size=13),
        title_font=dict(color=ENKO_TEXT)
    )
    fig.update_yaxes(
        gridcolor="#E6DDF2",
        tickfont=dict(color=ENKO_TEXT, size=13),
        title_font=dict(color=ENKO_TEXT)
    )
    return fig

def build_donut_chart(data, category_col, title):
    counts = (
        data[category_col]
        .fillna("Sin dato")
        .replace("", "Sin dato")
        .value_counts(dropna=False)
        .reset_index()
    )
    counts.columns = [category_col, "Usuarios"]

    palette = [ENKO_PURPLE, ENKO_ORANGE, ENKO_PURPLE_LIGHT, "#B08AD4", "#D4B7F0", "#FFD5A3", "#CFC6DA"]
    fig = px.pie(
        counts,
        names=category_col,
        values="Usuarios",
        hole=0.58,
        title=title,
        color_discrete_sequence=palette
    )
    fig.update_layout(
        template="plotly_white",
        title_font=dict(size=18, color=ENKO_TEXT),
        paper_bgcolor=ENKO_WHITE,
        plot_bgcolor=ENKO_WHITE,
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(color=ENKO_TEXT),
        legend_title_text="",
        legend=dict(font=dict(color=ENKO_TEXT))
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        textfont=dict(color="#FFFFFF", size=12)
    )
    return fig

def logout():
    st.session_state["authenticated"] = False
    st.session_state["current_ally"] = None

def render_header(current_ally):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(
            f"""
            <div class="enko-header">
                <div class="enko-title">Dashboard de Aliados | ENKO Solutions</div>
                <div class="enko-subtitle">Vista personalizada para <b>{current_ally}</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.write("")
        if st.button("Cerrar sesión", use_container_width=True):
            logout()
            st.rerun()

def render_login(access_df):
    st.markdown(
        """
        <div class="enko-header">
            <div class="enko-title">ENKO Solutions</div>
            <div class="enko-subtitle">Acceso al dashboard de aliados</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        left, center, right = st.columns([1, 1.4, 1])
        with center:
            st.markdown('<div class="login-box">', unsafe_allow_html=True)
            st.subheader("Ingresa con tu aliado y clave")
            ally = st.selectbox(
                "Aliado",
                options=access_df["aliado"].tolist(),
                index=None,
                placeholder="Selecciona tu aliado"
            )
            password = st.text_input("Clave", type="password", placeholder="Escribe tu clave")
            login_btn = st.button("Ingresar", use_container_width=True)

            st.markdown(
                '<div class="small-note">Para el MVP se incluyen credenciales de ejemplo. '
                'Después puedes sustituirlas por claves reales en el archivo de accesos.</div>',
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if login_btn:
                if not ally or not password:
                    st.warning("Selecciona un aliado y captura una clave.")
                    return

                match = access_df[
                    (access_df["aliado_norm"] == normalize_text(ally)) &
                    (access_df["clave"].astype(str) == str(password))
                ]

                if match.empty:
                    st.error("La combinación de aliado y clave no es válida.")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["current_ally"] = ally
                    st.rerun()

def render_filters(df_ally):
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    st.subheader("Filtros")

    min_date = df_ally["fecha_registro_dia"].dropna().min()
    max_date = df_ally["fecha_registro_dia"].dropna().max()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        default_dates = (min_date, max_date) if pd.notna(min_date) and pd.notna(max_date) else ()
        date_range = st.date_input(
            "Rango de fechas",
            value=default_dates,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        status = st.selectbox("Estatus", ["Todos", "Registrado", "Activo"])

    with col3:
        genero = st.multiselect(
            "Género",
            options=sorted(df_ally["Género"].fillna("Sin dato").astype(str).unique().tolist()),
            default=[]
        )

    with col4:
        sector = st.multiselect(
            "Sector",
            options=sorted(df_ally["Sector"].fillna("Sin dato").astype(str).unique().tolist()),
            default=[]
        )

    with col5:
        giro = st.multiselect(
            "Giro",
            options=sorted(df_ally["Giro"].fillna("Sin dato").astype(str).unique().tolist()),
            default=[]
        )

    st.markdown("</div>", unsafe_allow_html=True)

    filtered = df_ally.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered = filtered[
            (filtered["fecha_registro_dia"] >= start_date) &
            (filtered["fecha_registro_dia"] <= end_date)
        ]

    if status != "Todos":
        filtered = filtered[filtered["estatus_usuario"] == status]

    if genero:
        filtered = filtered[filtered["Género"].isin(genero)]

    if sector:
        filtered = filtered[filtered["Sector"].isin(sector)]

    if giro:
        filtered = filtered[filtered["Giro"].isin(giro)]

    return filtered

def render_kpis(filtered):
    total_registrados = len(filtered)
    total_activos = int((filtered["Lecciones completadas"] >= 1).sum())
    pct_activacion = (total_activos / total_registrados) if total_registrados > 0 else 0
    total_lecciones = filtered["Lecciones completadas"].sum()

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Usuarios registrados", format_int(total_registrados)),
        ("Usuarios activos", format_int(total_activos)),
        ("% de activación", format_pct(pct_activacion)),
        ("Lecciones completadas", format_int(total_lecciones))
    ]

    for col, (label, value) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

def render_time_series(filtered):
    daily = (
        filtered.groupby("fecha_registro_dia", dropna=False)
        .agg(
            registrados=("Nombre completo", "count"),
            activos=("estatus_usuario", lambda s: (s == "Activo").sum())
        )
        .reset_index()
        .sort_values("fecha_registro_dia")
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        fig1 = build_line_chart(daily, "fecha_registro_dia", "registrados", "Registros por día", ENKO_PURPLE)
        st.plotly_chart(fig1, use_container_width=True, theme=None)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        fig2 = build_line_chart(daily, "fecha_registro_dia", "activos", "Usuarios activos por día", ENKO_ORANGE)
        st.plotly_chart(fig2, use_container_width=True, theme=None)
        st.markdown("</div>", unsafe_allow_html=True)

def render_demographics(filtered):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        fig = build_donut_chart(filtered, "Género", "Distribución por género")
        st.plotly_chart(fig, use_container_width=True, theme=None)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        fig = build_donut_chart(filtered, "Sector", "Distribución por sector")
        st.plotly_chart(fig, use_container_width=True, theme=None)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        fig = build_donut_chart(filtered, "Giro", "Distribución por giro")
        st.plotly_chart(fig, use_container_width=True, theme=None)
        st.markdown("</div>", unsafe_allow_html=True)

def render_table(filtered):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Detalle de usuarios")

    table_cols = [
        "Nombre completo", "Lada", "Teléfono", "Correo usuario", "Género",
        "Sector", "Giro", "Lecciones completadas", "Fecha de registro_fmt", "Último acceso_fmt"
    ]
    table = filtered[table_cols].rename(
        columns={
            "Fecha de registro_fmt": "Fecha de registro",
            "Último acceso_fmt": "Último acceso"
        }
    ).copy()

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# App principal
# =========================
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "current_ally" not in st.session_state:
        st.session_state["current_ally"] = None

    if not Path(DATA_PATH).exists():
        st.error(f"No se encontró el archivo de datos en: {DATA_PATH}")
        st.info("Sube tu archivo a la ruta esperada o define la variable ENKO_DATA_PATH.")
        return

    if not Path(ACCESS_PATH).exists():
        st.error(f"No se encontró el archivo de accesos en: {ACCESS_PATH}")
        st.info("Crea el CSV de accesos o define la variable ENKO_ACCESS_PATH.")
        return

    try:
        access_df = load_access_table(ACCESS_PATH)
        df = load_data(DATA_PATH, SHEET_NAME)
    except Exception as e:
        st.error(f"Error al cargar la información: {e}")
        return

    if not st.session_state["authenticated"]:
        render_login(access_df)
        return

    current_ally = st.session_state["current_ally"]
    render_header(current_ally)

    ally_norm = normalize_text(current_ally)
    df_ally = df[df["aliado_norm"] == ally_norm].copy()

    if df_ally.empty:
        st.warning("No se encontraron registros para el aliado autenticado.")
        return

    filtered = render_filters(df_ally)
    render_kpis(filtered)

    if filtered.empty:
        st.warning("No hay datos para los filtros seleccionados.")
        return

    render_time_series(filtered)
    render_demographics(filtered)
    render_table(filtered)

if __name__ == "__main__":
    main()
