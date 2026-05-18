import pandas as pd
import plotly.express as px
import streamlit as st


SHEET_ID = "1PuybSaaC423UwRtGp3B9PsaZU1czqJj0A936l1I9bdM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
CHART_BG = "rgba(0,0,0,0)"
TEXT_COLOR = "#2C2C2A"
TICK_COLOR = "#888780"
GRID_COLOR = "#EEEEEE"
TOOLTIP_BG = "#FFFFFF"
BAR_HIGH = "#0F6E56"
BAR_LOW = "#9FE1CB"
BORDER_COLOR = "#1D9E75"
PPC_BUDGET_RANGE_ORDER = [
    "0",
    "1-500",
    "501-1,000",
    "1,001-2,500",
    "2,501-5,000",
    "5,001-10,000",
    "10,001+",
]


@st.cache_data(ttl=600)
def load_google_sheet():
    return pd.read_csv(SHEET_CSV_URL)


def prepare_data(data):
    data = data.copy()

    for column in data.columns:
        if "date" in column.lower():
            data[column] = pd.to_datetime(data[column], errors="coerce")

    for column in data.select_dtypes(include="object").columns:
        if column == "PPC budget USD":
            continue

        cleaned = data[column].str.replace(",", "", regex=False)
        converted = pd.to_numeric(cleaned, errors="coerce")
        if converted.notna().sum() > 0:
            data[column] = converted

    return data


def normalize_ppc_budget_range(value):
    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)):
        return numeric_ppc_budget_range(value)

    cleaned = str(value).strip().replace("$", "").replace(",", "").replace(" ", "")
    mapped_ranges = {
        "0": "0",
        "0-500": "1-500",
        "1-500": "1-500",
        "500-1000": "501-1,000",
        "501-1000": "501-1,000",
        "1000-2000": "1,001-2,500",
        "1001-2500": "1,001-2,500",
        "2000-5000": "2,501-5,000",
        "2501-5000": "2,501-5,000",
        "5000-10000": "5,001-10,000",
        "5001-10000": "5,001-10,000",
        "20000+": "10,001+",
        "10001+": "10,001+",
    }
    if cleaned in mapped_ranges:
        return mapped_ranges[cleaned]

    numeric_value = pd.to_numeric(cleaned.replace("+", ""), errors="coerce")
    if pd.notna(numeric_value):
        return numeric_ppc_budget_range(numeric_value)

    return pd.NA


def numeric_ppc_budget_range(value):
    if value == 0:
        return "0"
    if value <= 500:
        return "1-500"
    if value <= 1000:
        return "501-1,000"
    if value <= 2500:
        return "1,001-2,500"
    if value <= 5000:
        return "2,501-5,000"
    if value <= 10000:
        return "5,001-10,000"
    return "10,001+"


def country_code(country):
    if pd.isna(country):
        return "Unknown"
    return str(country).strip().split(" ")[0]


def polished_bar_chart(
    data,
    x,
    y,
    title,
    is_percent=False,
    custom_data=None,
    hovertemplate=None,
):
    chart_data = data.sort_values(y, ascending=False).copy()
    fig = px.bar(
        chart_data,
        x=x,
        y=y,
        color=y,
        color_continuous_scale=[BAR_LOW, BAR_HIGH],
        custom_data=custom_data,
    )
    fig.update_traces(marker_line_width=0)
    if hovertemplate:
        fig.update_traces(hovertemplate=hovertemplate)

    fig.update_layout(
        bargap=0.35,
        coloraxis_showscale=False,
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        margin=dict(t=50, b=80, l=60, r=30),
        paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,
        title=dict(
            text=title,
            x=0,
            xanchor="left",
            font=dict(size=15, color=TEXT_COLOR, family="Inter, sans-serif", weight=500),
        ),
        hoverlabel=dict(
            bgcolor=TOOLTIP_BG,
            bordercolor=BORDER_COLOR,
            font=dict(family="Inter, sans-serif", color=TEXT_COLOR, size=12),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        title_text=None,
        tickangle=-40,
        tickfont=dict(size=12, color=TICK_COLOR, family="Inter, sans-serif"),
    )
    fig.update_yaxes(
        gridcolor=GRID_COLOR,
        showgrid=True,
        showline=False,
        zeroline=False,
        title_text=None,
        tickfont=dict(size=12, color=TICK_COLOR, family="Inter, sans-serif"),
    )
    if is_percent:
        fig.update_yaxes(tickformat=".0%")

    return fig


def inject_dashboard_styles():
    st.markdown(
        """
        <style>
        .stApp {
            font-family: Inter, sans-serif;
        }
        div[data-testid="stMetric"],
        .metric-card {
            border: 1px solid #1D9E75;
            border-radius: 10px;
            padding: 18px 20px;
            background: rgba(0,0,0,0);
            box-shadow: 0 8px 24px rgba(15, 110, 86, 0.08);
        }
        .metric-label {
            color: #888780;
            font-family: Inter, sans-serif;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0;
            margin-bottom: 8px;
        }
        .metric-value {
            color: #2C2C2A;
            font-family: Inter, sans-serif;
            font-size: 28px;
            font-weight: 600;
            line-height: 1.1;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #1D9E75;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(15, 110, 86, 0.08);
        }
        div[data-testid="stDataFrame"] * {
            font-family: Inter, sans-serif;
        }
        h1, h2, h3, .stMarkdown, .stCaption {
            color: #2C2C2A;
            font-family: Inter, sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def add_sidebar_filters(data):
    filtered = data.copy()

    countries = sorted(data["Client country"].dropna().unique().tolist())
    selected_countries = st.sidebar.multiselect(
        "Client country", countries, default=countries
    )
    if selected_countries:
        filtered = filtered[filtered["Client country"].isin(selected_countries)]

    crms = sorted(data["Client CRM"].dropna().unique().tolist())
    selected_crms = st.sidebar.multiselect("Client CRM", crms, default=crms)
    if selected_crms:
        filtered = filtered[filtered["Client CRM"].isin(selected_crms)]

    dates = data["AQL date"].dropna()
    if not dates.empty:
        min_date = dates.min().date()
        max_date = dates.max().date()
        selected_date_range = st.sidebar.date_input(
            "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
            filtered = filtered[
                (filtered["AQL date"].dt.date >= start_date)
                & (filtered["AQL date"].dt.date <= end_date)
            ]

    return filtered


def win_rate_by(data, group_column):
    closed = data[data["Stage"].isin(["Closed Won", "Closed Lost"])].copy()
    if closed.empty:
        return pd.DataFrame(columns=[group_column, "won_deals", "closed_deals", "win_rate"])

    summary = (
        closed.assign(won_deals=closed["Stage"].eq("Closed Won").astype(int))
        .groupby(group_column, dropna=False)
        .agg(won_deals=("won_deals", "sum"), closed_deals=("Stage", "size"))
        .reset_index()
    )
    summary["win_rate"] = summary["won_deals"] / summary["closed_deals"]
    return summary.sort_values("win_rate", ascending=False)


def win_rate_by_ppc_budget_range(data):
    closed = data[data["Stage"].isin(["Closed Won", "Closed Lost"])].copy()
    if closed.empty:
        return pd.DataFrame(
            columns=["PPC budget range", "won_deals", "closed_deals", "win_rate"]
        )

    closed["PPC budget range"] = closed["PPC budget USD"].apply(normalize_ppc_budget_range)
    closed["PPC budget range"] = pd.Categorical(
        closed["PPC budget range"],
        categories=PPC_BUDGET_RANGE_ORDER,
        ordered=True,
    )

    summary = (
        closed.dropna(subset=["PPC budget range"])
        .assign(won_deals=closed["Stage"].eq("Closed Won").astype(int))
        .groupby("PPC budget range", observed=False)
        .agg(won_deals=("won_deals", "sum"), closed_deals=("Stage", "size"))
        .reset_index()
    )
    summary["win_rate"] = summary["won_deals"] / summary["closed_deals"]
    summary["win_rate"] = summary["win_rate"].fillna(0)
    summary["PPC budget range"] = summary["PPC budget range"].astype(str)
    return summary


def is_empty_value(series):
    return series.isna() | series.astype(str).str.strip().eq("")


def add_quality_issue(issues, data, mask, issue):
    if mask.any():
        issue_rows = data.loc[mask].copy()
        issue_rows.insert(0, "Record row", issue_rows.index + 1)
        issue_rows.insert(0, "Data issue", issue)
        issues.append(issue_rows)


def data_quality_issues(data):
    issues = []
    closed_stages = ["Closed Won", "Closed Lost"]

    if "AQL date" in data.columns:
        add_quality_issue(
            issues,
            data,
            data["AQL date"].isna(),
            "AQL date is missing",
        )
        add_quality_issue(
            issues,
            data,
            data["AQL date"] > pd.Timestamp.today().normalize(),
            "AQL date is in the future",
        )

    if "Source" in data.columns:
        add_quality_issue(
            issues,
            data,
            is_empty_value(data["Source"]),
            "Source is empty or missing",
        )

    if "Client country" in data.columns:
        add_quality_issue(
            issues,
            data,
            is_empty_value(data["Client country"]),
            "Client country is missing",
        )

    if "Stage" in data.columns and "Closing Date" in data.columns:
        closed_without_closing_date = (
            data["Stage"].isin(closed_stages)
            & data["Closing Date"].isna()
        )
        add_quality_issue(
            issues,
            data,
            closed_without_closing_date,
            "Missing Closing Date for closed deal",
        )

        intermediate_with_closing_date = (
            ~data["Stage"].isin(closed_stages)
            & data["Closing Date"].notna()
        )
        add_quality_issue(
            issues,
            data,
            intermediate_with_closing_date,
            "Intermediate-stage deal has Closing Date set",
        )

    if "AQL date" in data.columns and "Closing Date" in data.columns:
        add_quality_issue(
            issues,
            data,
            data["Closing Date"].notna()
            & data["AQL date"].notna()
            & (data["Closing Date"] < data["AQL date"]),
            "Closing Date is earlier than AQL date",
        )

    if (
        "Stage" in data.columns
        and "Subscription period" in data.columns
    ):
        subscription_period = pd.to_numeric(
            data["Subscription period"], errors="coerce"
        )
        add_quality_issue(
            issues,
            data,
            data["Stage"].eq("Closed Won")
            & (subscription_period.isna() | subscription_period.eq(0)),
            "Closed Won deal has missing or zero Subscription period",
        )

        subscription_std = subscription_period.std()
        subscription_mean = subscription_period.mean()
        if pd.notna(subscription_std) and subscription_std > 0:
            add_quality_issue(
                issues,
                data,
                subscription_period.notna()
                & (
                    (subscription_period - subscription_mean).abs()
                    > 3 * subscription_std
                ),
                "Subscription period is an extreme outlier",
            )

    if "PPC budget USD" in data.columns:
        normalized_budget = data["PPC budget USD"].apply(normalize_ppc_budget_range)
        add_quality_issue(
            issues,
            data,
            is_empty_value(data["PPC budget USD"]) | normalized_budget.isna(),
            "PPC budget USD is missing or does not match a known range",
        )

    if "Number of sales reps" in data.columns:
        sales_reps = pd.to_numeric(data["Number of sales reps"], errors="coerce")
        add_quality_issue(
            issues,
            data,
            sales_reps.notna() & sales_reps.le(0),
            "Number of sales reps is zero or negative",
        )

    client_column = next(
        (
            column
            for column in ["Client", "Client name", "Client Name", "Company", "Client company"]
            if column in data.columns
        ),
        None,
    )
    if client_column and "Client CRM" in data.columns:
        crm_counts = (
            data.dropna(subset=[client_column, "Client CRM"])
            .assign(
                client_key=lambda frame: frame[client_column].astype(str).str.strip(),
                crm_key=lambda frame: frame["Client CRM"].astype(str).str.strip(),
            )
            .query("client_key != '' and crm_key != ''")
            .groupby("client_key")["crm_key"]
            .nunique()
        )
        conflicting_clients = crm_counts[crm_counts > 1].index
        add_quality_issue(
            issues,
            data,
            data[client_column].astype(str).str.strip().isin(conflicting_clients),
            "Same client has conflicting Client CRM values",
        )

    if not issues:
        return pd.DataFrame()

    return pd.concat(issues, ignore_index=True)


def data_quality_summary(data, issues):
    total_records = len(data)
    issue_count = len(issues)
    if total_records == 0:
        return "100% clean — 0 issues found across 0 records"

    issue_record_count = (
        issues["Record row"].nunique()
        if not issues.empty and "Record row" in issues.columns
        else issue_count
    )
    clean_score = max(0, (total_records - issue_record_count) / total_records)
    return (
        f"{clean_score:.0%} clean — "
        f"{issue_count:,} issues found across {total_records:,} records"
    )


st.set_page_config(page_title="Analytical Dashboard", layout="wide")

st.title("Analytical Dashboard")

inject_dashboard_styles()

uploaded_file = st.sidebar.file_uploader("Upload CSV data", type=["csv"])

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    data_source = "Uploaded CSV"
else:
    data = load_google_sheet()
    data_source = "Google Sheet"

data = prepare_data(data)
filtered_data = add_sidebar_filters(data)

st.sidebar.caption("Upload a CSV to temporarily replace the Google Sheet data.")
st.caption(f"Data source: {data_source}")

metric_cols = st.columns(3)
with metric_cols[0]:
    metric_card("Deals", f"{len(filtered_data):,}")
with metric_cols[1]:
    closed_deals = filtered_data["Stage"].isin(["Closed Won", "Closed Lost"]).sum()
    metric_card("Closed deals", f"{closed_deals:,}")
with metric_cols[2]:
    won_deals = filtered_data["Stage"].eq("Closed Won").sum()
    win_rate = won_deals / closed_deals if closed_deals else 0
    metric_card("Win rate", f"{win_rate:.1%}")

st.subheader("Data Preview")
st.dataframe(filtered_data, width="stretch")

if filtered_data.empty:
    st.info("No deals match the selected filters.")
else:
    country_data = filtered_data.copy()
    country_data["Country"] = country_data["Client country"].apply(country_code)
    country_win_rate = win_rate_by(country_data, "Country")
    crm_win_rate = win_rate_by(filtered_data, "Client CRM")
    source_win_rate = win_rate_by(filtered_data, "Source")
    country_win_rate = country_win_rate[country_win_rate["win_rate"] > 0]
    crm_win_rate = crm_win_rate[crm_win_rate["win_rate"] > 0]
    source_win_rate = source_win_rate[source_win_rate["win_rate"] > 0]
    country_win_rate_min_5 = country_win_rate[
        country_win_rate["closed_deals"] >= 5
    ]
    crm_win_rate_min_5 = crm_win_rate[crm_win_rate["closed_deals"] >= 5]
    stage_counts = (
        filtered_data["Stage"].value_counts(dropna=False).rename_axis("Stage").reset_index(name="deals")
    )
    source_counts = (
        filtered_data["Source"].value_counts(dropna=False).rename_axis("Source").reset_index(name="deals")
    )
    budget_win_rate = win_rate_by_ppc_budget_range(filtered_data)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            polished_bar_chart(
                country_win_rate,
                x="Country",
                y="win_rate",
                title="Win Rate by Countries",
                is_percent=True,
                custom_data=["closed_deals"],
                hovertemplate=(
                    "%{x}<br>Win rate: %{y:.1%}<br>"
                    "Closed deals: %{customdata[0]:,}<extra></extra>"
                ),
            ),
            width="stretch",
        )

    with right:
        st.plotly_chart(
            polished_bar_chart(
                crm_win_rate,
                x="Client CRM",
                y="win_rate",
                title="Win Rate by CRM",
                is_percent=True,
                custom_data=["closed_deals"],
                hovertemplate=(
                    "%{x}<br>Win rate: %{y:.1%}<br>"
                    "Closed deals: %{customdata[0]:,}<extra></extra>"
                ),
            ),
            width="stretch",
        )

    source_win_rate_chart = polished_bar_chart(
        source_win_rate,
        x="Source",
        y="win_rate",
        title="Win Rate by Source",
        is_percent=True,
        custom_data=["closed_deals"],
        hovertemplate=(
            "%{x}<br>Win rate: %{y:.1%}<br>"
            "Closed deals: %{customdata[0]:,}<extra></extra>"
        ),
    )
    st.plotly_chart(source_win_rate_chart, width="stretch")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            polished_bar_chart(
                country_win_rate_min_5,
                x="Country",
                y="win_rate",
                title="Win Rate by Countries (5+ Closed Deals)",
                is_percent=True,
                custom_data=["closed_deals"],
                hovertemplate=(
                    "%{x}<br>Win rate: %{y:.1%}<br>"
                    "Closed deals: %{customdata[0]:,}<extra></extra>"
                ),
            ),
            width="stretch",
        )

    with right:
        st.plotly_chart(
            polished_bar_chart(
                crm_win_rate_min_5,
                x="Client CRM",
                y="win_rate",
                title="Win Rate by CRM (5+ Closed Deals)",
                is_percent=True,
                custom_data=["closed_deals"],
                hovertemplate=(
                    "%{x}<br>Win rate: %{y:.1%}<br>"
                    "Closed deals: %{customdata[0]:,}<extra></extra>"
                ),
            ),
            width="stretch",
        )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            polished_bar_chart(
                stage_counts,
                x="Stage",
                y="deals",
                title="Number of Deals by Stage",
                hovertemplate="%{x}<br>Deals: %{y:,}<extra></extra>",
            ),
            width="stretch",
        )

    with right:
        st.plotly_chart(
            polished_bar_chart(
                source_counts,
                x="Source",
                y="deals",
                title="Number of Deals by Source",
                hovertemplate="%{x}<br>Deals: %{y:,}<extra></extra>",
            ),
            width="stretch",
        )

    budget_chart = polished_bar_chart(
        budget_win_rate,
        x="PPC budget range",
        y="win_rate",
        title="Win Rate vs PPC Budget",
        is_percent=True,
        custom_data=["closed_deals"],
        hovertemplate=(
            "%{x}<br>Win rate: %{y:.1%}<br>"
            "Closed deals: %{customdata[0]:,}<extra></extra>"
        ),
    )
    st.plotly_chart(budget_chart, width="stretch")

st.subheader("Data Quality Check")
quality_issues = data_quality_issues(filtered_data)
metric_card("Overall data quality score", data_quality_summary(filtered_data, quality_issues))
if quality_issues.empty:
    st.success("No data quality issues found.")
else:
    st.warning(f"{len(quality_issues):,} data issue(s) found.")
    st.dataframe(quality_issues, width="stretch")
