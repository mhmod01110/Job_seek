import dash
import math
import re
import os
import ast
import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Input, Output, State
from datetime import datetime, timedelta

linkedin_path = "Processed_Data/linkedin_processed_data"
telegram_path = "Processed_Data/telegram_processed_data"
emails_path = "Processed_Data/emails_database"

def load_and_concat_csvs(directory_path):
    # Get a list of all CSV files in the specified directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    # If no CSV files are found, return an empty DataFrame
    if not csv_files:
        return pd.DataFrame()

    # Read each CSV file and store DataFrames in a list
    dataframes = [pd.read_csv(os.path.join(directory_path, f)) for f in csv_files]
    
    # Concatenate all DataFrames along the rows (axis=0)
    concatenated_df = pd.concat(dataframes, axis=0, ignore_index=True)
    
    
    return concatenated_df

df = load_and_concat_csvs(linkedin_path)
df['post_time'] = pd.to_datetime(df['postTime'])
df['scraping_date'] = pd.to_datetime(df['scrappingDate'])


t_df = load_and_concat_csvs(telegram_path)
t_df['post_time'] = pd.to_datetime(t_df['postTime'])

e_df = load_and_concat_csvs(emails_path)
e_df["sectors"] = e_df["sectors"].apply(ast.literal_eval)

# Valid credentials
VALID_CREDENTIALS = {
    "user1": "12345",
    "admin": "admin"
}

RECORDS_PER_PAGE = 10

# Dash app initialization
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUMEN], suppress_callback_exceptions=True)

class DataFilter:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def filter_by_date(self, start_date, end_date):
        if start_date is None and end_date is None:
            # If both dates are None, return the original dataframe
            return self.dataframe
        elif start_date is None:
            # If only start_date is None, filter up to end_date
            return self.dataframe[self.dataframe['post_time'] <= end_date]
        elif end_date is None:
            # If only end_date is None, filter from start_date onwards
            return self.dataframe[self.dataframe['post_time'] >= start_date]
        else:
            # If both dates are provided, filter between them
            return self.dataframe[(self.dataframe['post_time'] >= start_date) & (self.dataframe['post_time'] <= end_date)]

    def filter_by_recent_days(self, days):
        cutoff_date = (datetime.now() - timedelta(days=days)).replace(microsecond=0)
        return self.dataframe[self.dataframe['scraping_date'] >= cutoff_date]

    def filter_by_search(self, df, search_value):
        if search_value:
            return df[df['text'].str.contains(search_value.strip(), case=False, na=False)]
        return df

    def filter_by_email_count(self, df):
        return df[df['email_count'] > 0]

    def filter_by_link_count(self, df):
        return df[df['link_count'] > 0]

    def highlight_search(self, text, search_value):
        if search_value:
            highlighted_text = re.sub(f"({search_value})", r'⏪⏪\1⏩⏩', text, flags=re.IGNORECASE)
            return html.Span(dcc.Markdown(highlighted_text))
        return text


class E_DataFilter:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def filter_by_recent_days(self, days):
        if days is not None:
            cutoff_date = (datetime.now() - timedelta(days=days)).replace(microsecond=0)
            return self.dataframe[self.dataframe['date'] >= cutoff_date]
        return self.dataframe

    def filter_by_city(self, cities):
        if cities:
            return self.dataframe[self.dataframe['city'].isin(cities)]
        return self.dataframe

    def filter_by_region(self, regions):
        if regions:
            return self.dataframe[self.dataframe['region'].isin(regions)]
        return self.dataframe

    def filter_by_sector(self, sectors):
        if sectors:
            return self.dataframe[self.dataframe['sectors'].apply(lambda x: any(sector in x for sector in sectors))]
        return self.dataframe

    def filter_by_specialization(self, specializations):
        if specializations:
            return self.dataframe[self.dataframe['specialization'].isin(specializations)]
        return self.dataframe

    def apply_filters(self, recent_days=None, cities=None, regions=None, sectors=None, specializations=None):
        filtered_df = self.filter_by_recent_days(recent_days)
        filtered_df = filtered_df[filtered_df['city'].isin(cities)] if cities else filtered_df
        filtered_df = filtered_df[filtered_df['region'].isin(regions)] if regions else filtered_df
        filtered_df = filtered_df[filtered_df['sectors'].isin(sectors)] if sectors else filtered_df
        filtered_df = filtered_df[filtered_df['specialization'].isin(specializations)] if specializations else filtered_df
        return filtered_df
    

    
    
class DataVisualizer:
    def __init__(self, filtered_df, active_page, records_per_page):
        self.filtered_df = filtered_df
        self.active_page = active_page
        self.records_per_page = records_per_page
        self.total_pages = math.ceil(len(filtered_df) / records_per_page)
        self.start_idx = (active_page - 1) * records_per_page
        self.end_idx = self.start_idx + records_per_page
        self.paginated_df = filtered_df.iloc[self.start_idx:self.end_idx].copy()

    def generate_table(self, search_value):
        hide_columns = ["email_count", "link_count", "postedAtISO", "source_file", "title"]

        ordered_columns = [
            "Index",
            "authorName",
            "authorHeadline",
            "text",
            "post_time",
            "emails",
            "links"
        ]

        other_columns = [col for col in self.paginated_df.columns if col not in ordered_columns + hide_columns]
        columns_to_display = ordered_columns + other_columns

        rows = []
        for i in range(len(self.paginated_df)):
            row = []
            for col in columns_to_display:
                if col == 'text':
                    cell = DataFilter(df).highlight_search(self.paginated_df.iloc[i][col], search_value)
                else:
                    cell = self.paginated_df.iloc[i][col]
                row.append(html.Td(cell))
            rows.append(html.Tr(row))

        return dbc.Table(
            [html.Thead(html.Tr([html.Th(col) for col in columns_to_display])),
             html.Tbody(rows)],
            striped=True, bordered=True, hover=True
        )

    def generate_pagination(self):
        return dbc.Pagination(
            max_value=self.total_pages,
            active_page=self.active_page,
            first_last=True,
            previous_next=True,
            fully_expanded=False,
            id='pagination-component'
        )

class T_DataVisualizer:
    def __init__(self, filtered_df, active_page, records_per_page):
        self.filtered_df = filtered_df
        self.active_page = active_page
        self.records_per_page = records_per_page
        self.total_pages = math.ceil(len(filtered_df) / records_per_page)
        self.start_idx = (active_page - 1) * records_per_page
        self.end_idx = self.start_idx + records_per_page
        self.paginated_df = filtered_df.iloc[self.start_idx:self.end_idx].copy()

    def generate_table(self, search_value):
        hide_columns = ["email_count", "link_count", "date", "source_file"]

        ordered_columns = [
            "Index",
            "channelName",
            "text",
            "post_time",
            "scrappingDate",
            "emails",
            "links"
        ]

        other_columns = [col for col in self.paginated_df.columns if col not in ordered_columns + hide_columns]
        columns_to_display = ordered_columns + other_columns

        rows = []
        for i in range(len(self.paginated_df)):
            row = []
            for col in columns_to_display:
                if col == 'text':
                    cell = DataFilter(t_df).highlight_search(self.paginated_df.iloc[i][col], search_value)
                else:
                    cell = self.paginated_df.iloc[i][col]
                row.append(html.Td(cell))
            rows.append(html.Tr(row))

        return dbc.Table(
            [html.Thead(html.Tr([html.Th(col) for col in columns_to_display])),
             html.Tbody(rows)],
            striped=True, bordered=True, hover=True
        )

    def generate_pagination(self):
        return dbc.Pagination(
            max_value=self.total_pages,
            active_page=self.active_page,
            first_last=True,
            previous_next=True,
            fully_expanded=False,
            id='pagination-component-2'
        )

class E_DataVisualizer:
    def __init__(self, filtered_df, active_page, records_per_page):
        self.filtered_df = filtered_df
        self.active_page = active_page
        self.records_per_page = records_per_page
        self.total_pages = math.ceil(len(filtered_df) / records_per_page)
        self.start_idx = (active_page - 1) * records_per_page
        self.end_idx = self.start_idx + records_per_page
        self.paginated_df = filtered_df.iloc[self.start_idx:self.end_idx].copy()

    def generate_table(self):
        ordered_columns = [
            "city",
            "region",
            "sectors",
            "specialization",
            "date",
        ]

        other_columns = [col for col in self.paginated_df.columns if col not in ordered_columns]
        columns_to_display = ordered_columns + other_columns

        rows = []
        for i in range(len(self.paginated_df)):
            row = []
            for col in columns_to_display:
                cell = self.paginated_df.iloc[i][col]
                row.append(html.Td(cell))
            rows.append(html.Tr(row))

        return dbc.Table(
            [html.Thead(html.Tr([html.Th(col) for col in columns_to_display])),
             html.Tbody(rows)],
            striped=True, bordered=True, hover=True
        )

    def generate_pagination(self):
        return dbc.Pagination(
            max_value=self.total_pages,
            active_page=self.active_page,
            first_last=True,
            previous_next=True,
            fully_expanded=False,
            id='pagination-component-3'
        )
        
# LinkedIn posts tab content with all details
linkedin_posts_content = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                # Left panel for controllers and search (1/6 width)
                dbc.Col(
                    [
                        dbc.Label("Records per Page", className="mt-3"),
                        dcc.Dropdown(
                            id='records-per-page-dropdown',
                            options=[{'label': str(i), 'value': i} for i in range(5, 51, 5)],
                            value=RECORDS_PER_PAGE,
                            clearable=False,
                            className="mb-3"
                        ),
                        html.H2("Filters", className="text-center my-3"),

                        # Date Range Filter
                        dbc.Label("Select Date Range", className="mb-2"),
                        dcc.DatePickerRange(
                            id="date-picker-range",
                            display_format="YYYY-MM-DD",
                            min_date_allowed=df['post_time'].min(),
                            max_date_allowed=df['post_time'].max(),
                            clearable=True,
                            className="mb-3"
                        ),

                        # Filter and Clear Filter Buttons
                        dbc.Button("Filter", id="filter-button", color="primary", className="me-2 mb-3"),
                        dbc.Button("Clear Filter", id="clear-filter-button", color="secondary", className="mb-3"),

                        # Search Input
                        dbc.Label("Search Posts", className="mt-4"),
                        dbc.Input(type="text", id="search-input", placeholder="Search posts", className="mb-3"),

                        # Search and Download Buttons
                        dbc.Button("Search", id="search-button", color="primary", className="mb-3"),
                        dbc.Button("Download CSV", id="csv-export-button", color="info", className="mb-2"),
                        dbc.Button("Download Excel", id="excel-export-button", color="info"),

                        # Toggle Buttons
                        dbc.Button("Toggle Emails", id="toggle-emails", color="secondary", className="mt-4 mb-2"),
                        dbc.Button("Toggle Links", id="toggle-links", color="secondary"),

                        # Additional Inputs
                        dbc.Label("Recent Days", className="mt-4"),
                        dbc.Input(type="number", id="recent-days-input", placeholder="Enter recent days", className="mb-3"),


                    ],
                    width=2,  # Set to 1/6 of the page width
                    className="bg-light border-end pe-3"
                ),

                # Right panel for table and pagination (remaining width)
                dbc.Col(
                    [
                        html.H1("LinkedIn Posts with Details", className="text-center my-4"),

                        # Table container with overflow for responsive table
                        html.Div(
                            id='table-container',
                            style={"overflowX": "auto"},  # Enable horizontal scrolling
                            children=[
                                html.Table(
                                    # Add your table rows and columns here
                                    # e.g., generate the table dynamically with your data
                                    [
                                        html.Thead(
                                            html.Tr([html.Th("Column 1"), html.Th("Column 2"), html.Th("Column 3")])
                                        ),
                                        html.Tbody(
                                            [
                                                html.Tr([html.Td("Data 1"), html.Td("Data 2"), html.Td("Data 3")]),
                                                # Add more rows as needed
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            className="mt-3"  # Add margin-top for spacing
                        ),

                        # Pagination
                        html.Div(
                            dbc.Pagination(
                                id='pagination-component', max_value=1, active_page=1,
                                first_last=True, previous_next=True
                            ),
                            id='pagination-container',
                            className="mt-4 text-center"
                        ),

                        # Download Components
                        dcc.Download(id="download-dataframe-csv"),
                        dcc.Download(id="download-dataframe-xlsx"),
                    ],
                    width=10  # Set to remaining page width
                )
            ],
            className="mt-3"
        )
    )
)



# Telegram posts tab content (initially blank)
telegram_posts_content = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                # Left panel for controllers and search (1/6 width)
                dbc.Col(
                    [
                        dbc.Label("Records per Page", className="mt-3"),
                        dcc.Dropdown(
                            id='records-per-page-dropdown-2',
                            options=[{'label': str(i), 'value': i} for i in range(5, 51, 5)],
                            value=RECORDS_PER_PAGE,
                            clearable=False,
                            className="mb-3"
                        ),
                        html.H2("Filters", className="text-center my-3"),

                        # Date Range Filter
                        dbc.Label("Select Date Range", className="mb-2"),
                        dcc.DatePickerRange(
                            id="date-picker-range-2",
                            display_format="YYYY-MM-DD",
                            min_date_allowed=t_df['post_time'].min(),
                            max_date_allowed=t_df['post_time'].max(),
                            clearable=True,
                            className="mb-3"
                        ),

                        # Filter and Clear Filter Buttons
                        dbc.Button("Filter", id="filter-button-2", color="primary", className="me-2 mb-3"),
                        dbc.Button("Clear Filter", id="clear-filter-button-2", color="secondary", className="mb-3"),

                        # Search Input
                        dbc.Label("Search Posts", className="mt-4"),
                        dbc.Input(type="text", id="search-input-2", placeholder="Search posts", className="mb-3"),

                        # Search and Download Buttons
                        dbc.Button("Search", id="search-button-2", color="primary", className="mb-3"),
                        dbc.Button("Download CSV", id="csv-export-button-2", color="info", className="mb-2"),
                        dbc.Button("Download Excel", id="excel-export-button-2", color="info"),

                        # Toggle Buttons
                        dbc.Button("Toggle Emails", id="toggle-emails-2", color="secondary", className="mt-4 mb-2"),
                        dbc.Button("Toggle Links", id="toggle-links-2", color="secondary"),

                        # Additional Inputs
                        dbc.Label("Recent Days", className="mt-4"),
                        dbc.Input(type="number", id="recent-days-input-2", placeholder="Enter recent days", className="mb-3"),


                    ],
                    width=2,  # Set to 1/6 of the page width
                    className="bg-light border-end pe-3"
                ),

                # Right panel for table and pagination (remaining width)
                dbc.Col(
                    [
                        html.H1("Telegram Posts with Details", className="text-center my-4"),

                        # Table container with overflow for responsive table
                        html.Div(
                            id='table-container-2',
                            style={"overflowX": "auto"},  # Enable horizontal scrolling
                            children=[
                                html.Table(
                                    # Add your table rows and columns here
                                    # e.g., generate the table dynamically with your data
                                    [
                                        html.Thead(
                                            html.Tr([html.Th("Column 1"), html.Th("Column 2"), html.Th("Column 3")])
                                        ),
                                        html.Tbody(
                                            [
                                                html.Tr([html.Td("Data 1"), html.Td("Data 2"), html.Td("Data 3")]),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            className="mt-3"  # Add margin-top for spacing
                        ),

                        # Pagination
                        html.Div(
                            dbc.Pagination(
                                id='pagination-component-2', max_value=1, active_page=1,
                                first_last=True, previous_next=True
                            ),
                            id='pagination-container-2',
                            className="mt-4 text-center"
                        ),

                        # Download Components
                        dcc.Download(id="download-dataframe-csv-2"),
                        dcc.Download(id="download-dataframe-xlsx-2"),
                    ],
                    width=10  # Set to remaining page width
                )
            ],
            className="mt-3"
        )
    )
)
# Updated Emails Database tab content with Export Buttons
emails_database_content = dbc.Card(
    dbc.CardBody(
        dbc.Row(
            [
                # Left panel for controllers and filters (1/6 width)
                dbc.Col(
                    [
                        dbc.Label("Records per Page", className="mt-3"),
                        dcc.Dropdown(
                            id='records-per-page-dropdown-3',
                            options=[{'label': str(i), 'value': i} for i in range(5, 51, 5)],
                            value=RECORDS_PER_PAGE,
                            clearable=False,
                            className="mb-3"
                        ),
                        html.H2("Filters", className="text-center my-3"),

                        # Multi-option dropdowns
                        dbc.Label("City", className="mb-2"),
                        dcc.Dropdown(
                            id="city-dropdown",
                            options=[{'label': city, 'value': city} for city in e_df['city'].unique()],
                            multi=True,
                            className="mb-3"
                        ),

                        dbc.Label("Region", className="mb-2"),
                        dcc.Dropdown(
                            id="region-dropdown",
                            options=[{'label': region, 'value': region} for region in e_df['region'].unique()],
                            multi=True,
                            className="mb-3"
                        ),

                        dbc.Label("Sector", className="mb-2"),
                        dcc.Dropdown(
                            id="sector-dropdown",
                            options=[{'label': sector, 'value': sector} for sector in list(set([sector for sublist in e_df["sectors"] for sector in sublist]))],
                            multi=True,
                            className="mb-3"
                        ),

                        dbc.Label("Specialization", className="mb-2"),
                        dcc.Dropdown(
                            id="specialization-dropdown",
                            options=[{'label': specialization, 'value': specialization} for specialization in e_df['specialization'].unique()],
                            multi=True,
                            className="mb-3"
                        ),

                        # Filter and Clear Filter Buttons
                        dbc.Button("Filter", id="filter-button-3", color="primary", className="me-2 mb-3"),
                        dbc.Button("Clear Filter", id="clear-filter-button-3", color="secondary", className="mb-3"),

                        # Export Buttons for CSV and Excel
                        dbc.Button("Download CSV", id="csv-export-button-3", color="info", className="mb-2"),
                        dbc.Button("Download Excel", id="excel-export-button-3", color="info"),

                        # Additional Inputs
                        dbc.Label("Recent Days", className="mt-4"),
                        dbc.Input(type="number", id="recent-days-input-3", placeholder="Enter recent days", className="mb-3"),
                    ],
                    width=2,  # Set to 1/6 of the page width
                    className="bg-light border-end pe-3"
                ),

                # Right panel for table and pagination (remaining width)
                dbc.Col(
                    [
                        html.H1("Emails Database", className="text-center my-4"),

                        # Table container with overflow for responsive table
                        html.Div(
                            id='table-container-3',
                            style={"overflowX": "auto"},  # Enable horizontal scrolling
                            children=[
                                html.Table(
                                    [
                                        html.Thead(
                                            html.Tr([html.Th("Column 1"), html.Th("Column 2"), html.Th("Column 3")])
                                        ),
                                        html.Tbody(
                                            [
                                                html.Tr([html.Td("Data 1"), html.Td("Data 2"), html.Td("Data 3")]),
                                            ]
                                        ),
                                    ]
                                )
                            ],
                            className="mt-3"  # Add margin-top for spacing
                        ),

                        # Pagination
                        html.Div(
                            dbc.Pagination(
                                id='pagination-component-3', max_value=1, active_page=1,
                                first_last=True, previous_next=True
                            ),
                            id='pagination-container-3',
                            className="mt-4 text-center"
                        ),

                        # Download Components
                        dcc.Download(id="download-dataframe-csv-3"),
                        dcc.Download(id="download-dataframe-xlsx-3"),
                    ],
                    width=10  # Set to remaining page width
                )
            ],
            className="mt-3"
        )
    )
)


# Define the tabs layout
tabs = dbc.Tabs(
    [
        dbc.Tab(linkedin_posts_content, label="LinkedIn Posts"),
        dbc.Tab(telegram_posts_content, label="Telegram Posts"),
        dbc.Tab(emails_database_content, label="Emails Database"),
    ]
)

# Main layout with login form and tabs
app.layout = html.Div(
    [
        # Login form
        dbc.Container(
            dbc.Form(
                dbc.Row(
                    [
                        dbc.Label("Username", width="auto"),
                        dbc.Col(
                            dbc.Input(type="username", id="username-input", placeholder="Enter username"),
                            className="me-3",
                        ),
                        dbc.Label("Password", width="auto"),
                        dbc.Col(
                            dbc.Input(type="password", id="password-input", placeholder="Enter password"),
                            className="me-3",
                        ),
                        dbc.Col(dbc.Button("Submit", id="submit-button", color="primary"), width="auto"),
                    ],
                    className="g-2",
                ),
                id='login-form',
                style={'margin': '20px'}
            ),
            id='login-container'
        ),

        # Error message (initially hidden)
        dbc.Container(
            id='error-container',
            style={'display': 'none'},
            children=[dbc.Alert("Invalid credentials, please try again.", color="danger", id='error-message')]
        ),

        # Tabs (Dashboard) container
        dbc.Container(id='dashboard-container', style={'display': 'none'}, children=[tabs])
    ]
)

@app.callback(
    [Output('error-container', 'style'),
     Output('login-container', 'style'),
     Output('dashboard-container', 'style')],
    Input('submit-button', 'n_clicks'),
    State('username-input', 'value'),
    State('password-input', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password:
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    else:
        return {'display': 'block'}, {'display': 'block'}, {'display': 'none'}

@app.callback(
    [Output('table-container', 'children'),
     Output('pagination-container', 'children'),
     Output('toggle-emails', 'color'),
     Output('toggle-links', 'color')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('search-button', 'n_clicks'),
     Input('clear-filter-button', 'n_clicks'),
     Input('pagination-component', 'active_page'),
     Input('toggle-emails', 'n_clicks'),
     Input('toggle-links', 'n_clicks'),
     Input('recent-days-input', 'value'),
     Input('records-per-page-dropdown', 'value')],
    [State('search-input', 'value')]
)

def li_update_table(start_date, end_date, search_clicks, clear_filter_clicks, active_page, toggle_emails, toggle_links, recent_days, records_per_page, search_value):
    ctx = dash.callback_context

    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0] == 'clear-filter-button':
        active_page = 1
        filtered_df = df.copy()
        toggle_emails_active = False
        toggle_links_active = False
    else:
        active_page = active_page or 1
        data_filter = DataFilter(df)
        filtered_df = data_filter.filter_by_date(start_date, end_date)
        filtered_df = data_filter.filter_by_search(filtered_df, search_value)

        toggle_emails_active = toggle_emails and toggle_emails % 2 != 0
        toggle_links_active = toggle_links and toggle_links % 2 != 0

        if recent_days is not None:
            filtered_df = data_filter.filter_by_recent_days(recent_days)

        if toggle_emails_active:
            filtered_df = data_filter.filter_by_email_count(filtered_df)
        if toggle_links_active:
            filtered_df = data_filter.filter_by_link_count(filtered_df)

    emails_button_color = "success" if toggle_emails_active else "secondary"
    links_button_color = "success" if toggle_links_active else "secondary"

    data_visualizer = DataVisualizer(filtered_df, active_page or 1, records_per_page)
    table = data_visualizer.generate_table(search_value)
    pagination = data_visualizer.generate_pagination()

    return table, pagination, emails_button_color, links_button_color

@app.callback(
    [Output('table-container-2', 'children'),
     Output('pagination-container-2', 'children'),
     Output('toggle-emails-2', 'color'),
     Output('toggle-links-2', 'color')],
    [Input('date-picker-range-2', 'start_date'),
     Input('date-picker-range-2', 'end_date'),
     Input('search-button-2', 'n_clicks'),
     Input('clear-filter-button-2', 'n_clicks'),
     Input('pagination-component-2', 'active_page'),
     Input('toggle-emails-2', 'n_clicks'),
     Input('toggle-links-2', 'n_clicks'),
     Input('recent-days-input-2', 'value'),
     Input('records-per-page-dropdown-2', 'value')],
    [State('search-input-2', 'value')]
)
def t_update_table(start_date, end_date, search_clicks, clear_filter_clicks, active_page, toggle_emails, toggle_links, recent_days, records_per_page, search_value):
    ctx = dash.callback_context
    if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0] == 'clear-filter-button-2':
        active_page = 1
        filtered_df = t_df.copy()
        toggle_emails_active = False
        toggle_links_active = False
    else:
        active_page = active_page or 1
        data_filter = DataFilter(t_df)
        filtered_df = data_filter.filter_by_date(start_date, end_date)
        filtered_df = data_filter.filter_by_search(filtered_df, search_value)

        toggle_emails_active = toggle_emails and toggle_emails % 2 != 0
        toggle_links_active = toggle_links and toggle_links % 2 != 0

        if recent_days is not None:
            filtered_df = data_filter.filter_by_recent_days(recent_days)

        if toggle_emails_active:
            filtered_df = data_filter.filter_by_email_count(filtered_df)
        if toggle_links_active:
            filtered_df = data_filter.filter_by_link_count(filtered_df)

    emails_button_color = "success" if toggle_emails_active else "secondary"
    links_button_color = "success" if toggle_links_active else "secondary"

    data_visualizer = T_DataVisualizer(filtered_df, active_page or 1, records_per_page)
    table = data_visualizer.generate_table(search_value)
    pagination = data_visualizer.generate_pagination()

    return table, pagination, emails_button_color, links_button_color



@app.callback(
    [Output('table-container-3', 'children'),
     Output('pagination-container-3', 'children')],
    [Input('filter-button-3', 'n_clicks'),
     Input('clear-filter-button-3', 'n_clicks'),
     Input('pagination-component-3', 'active_page'),
     Input('recent-days-input-3', 'value'),
     Input('records-per-page-dropdown-3', 'value')],
    [State('city-dropdown', 'value'),
     State('region-dropdown', 'value'),
     State('sector-dropdown', 'value'),
     State('specialization-dropdown', 'value')]
)
def e_update_table(active_page, toggle_emails, toggle_links, recent_days, records_per_page, cities, regions, sectors, specializations):
    ctx = dash.callback_context
    # Determine which input triggered the callback
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    # Reset filters if "Clear Filter" button is clicked
    if trigger == 'clear-filter-button-3':
        active_page = 1
        filtered_df = e_df.copy()  # reset to original data
    else:
        # Apply filters
        data_filter = E_DataFilter(e_df)
        filtered_df = data_filter.apply_filters(
            recent_days=recent_days,
            cities=cities,
            regions=regions,
            sectors=sectors,
            specializations=specializations
        )
        
    # Visualize filtered data with pagination
    data_visualizer = E_DataVisualizer(filtered_df, active_page or 1, records_per_page)
    table = data_visualizer.generate_table()
    pagination = data_visualizer.generate_pagination()

    return table, pagination

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("csv-export-button", "n_clicks"),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('search-input', 'value'),
    State('toggle-emails', 'n_clicks'),
    State('toggle-links', 'n_clicks'),
    prevent_initial_call=True,
)
def export_csv(n_clicks, start_date, end_date, search_value, toggle_emails, toggle_links):
    data_filter = DataFilter(df)
    filtered_df = data_filter.filter_by_date(start_date, end_date)
    filtered_df = data_filter.filter_by_search(filtered_df, search_value)

    if toggle_emails and toggle_emails % 2 != 0:
        filtered_df = data_filter.filter_by_email_count(filtered_df)
    if toggle_links and toggle_links % 2 != 0:
        filtered_df = data_filter.filter_by_link_count(filtered_df)

    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")

@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("excel-export-button", "n_clicks"),
    State('date-picker-range', 'start_date'),
    State('date-picker-range', 'end_date'),
    State('search-input', 'value'),
    State('toggle-emails', 'n_clicks'),
    State('toggle-links', 'n_clicks'),
    prevent_initial_call=True,
)
def export_xlsx(n_clicks, start_date, end_date, search_value, toggle_emails, toggle_links):
    data_filter = DataFilter(df)
    filtered_df = data_filter.filter_by_date(start_date, end_date)
    filtered_df = data_filter.filter_by_search(filtered_df, search_value)

    if toggle_emails and toggle_emails % 2 != 0:
        filtered_df = data_filter.filter_by_email_count(filtered_df)
    if toggle_links and toggle_links % 2 != 0:
        filtered_df = data_filter.filter_by_link_count(filtered_df)

    return dcc.send_data_frame(filtered_df.to_excel, "filtered_data.xlsx", index=False)

@app.callback(
    Output("download-dataframe-csv-2", "data"),
    Input("csv-export-button-2", "n_clicks"),
    State('date-picker-range-2', 'start_date'),
    State('date-picker-range-2', 'end_date'),
    State('search-input-2', 'value'),
    State('toggle-emails-2', 'n_clicks'),
    State('toggle-links-2', 'n_clicks'),
    prevent_initial_call=True,
)
def export_csv(n_clicks, start_date, end_date, search_value, toggle_emails, toggle_links):
    data_filter = DataFilter(t_df)
    filtered_df = data_filter.filter_by_date(start_date, end_date)
    filtered_df = data_filter.filter_by_search(filtered_df, search_value)

    if toggle_emails and toggle_emails % 2 != 0:
        filtered_df = data_filter.filter_by_email_count(filtered_df)
    if toggle_links and toggle_links % 2 != 0:
        filtered_df = data_filter.filter_by_link_count(filtered_df)

    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")

@app.callback(
    Output("download-dataframe-xlsx-2", "data"),
    Input("excel-export-button-2", "n_clicks"),
    State('date-picker-range-2', 'start_date'),
    State('date-picker-range-2', 'end_date'),
    State('search-input-2', 'value'),
    State('toggle-emails-2', 'n_clicks'),
    State('toggle-links-2', 'n_clicks'),
    prevent_initial_call=True,
)
def export_xlsx(n_clicks, start_date, end_date, search_value, toggle_emails, toggle_links):
    data_filter = DataFilter(t_df)
    filtered_df = data_filter.filter_by_date(start_date, end_date)
    filtered_df = data_filter.filter_by_search(filtered_df, search_value)

    if toggle_emails and toggle_emails % 2 != 0:
        filtered_df = data_filter.filter_by_email_count(filtered_df)
    if toggle_links and toggle_links % 2 != 0:
        filtered_df = data_filter.filter_by_link_count(filtered_df)

    return dcc.send_data_frame(filtered_df.to_excel, "filtered_data.xlsx", index=False)


@app.callback(
    Output("download-dataframe-csv-3", "data"),
    Input("csv-export-button-3", "n_clicks"),
    State('recent-days-input-3', 'value'),
    State('city-dropdown', 'value'),
    State('region-dropdown', 'value'),
    State('sector-dropdown', 'value'),
    State('specialization-dropdown', 'value'),
    prevent_initial_call=True
)
def export_csv(n_clicks, recent_days, cities, regions, sectors, specializations):
    # Apply filters for export
    data_filter = E_DataFilter(e_df)
    filtered_df = data_filter.apply_filters(
        recent_days=recent_days,
        cities=cities,
        regions=regions,
        sectors=sectors,
        specializations=specializations
    )

    return dcc.send_data_frame(filtered_df.to_csv, "filtered_data.csv")


if __name__ == '__main__':
    app.run_server(debug=True)