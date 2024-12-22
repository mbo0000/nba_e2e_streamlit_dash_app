# Streamlit NBA Statistic Dashboard

## Introduction
This Streamlit app is the BI component of an [end-to-end data pipeline project](https://github.com/mbo0000/nba_e2e_data_pipeline), offering a digestible view of NBA teams' key advanced statistics. This dashboard aims to provide the average NBA fan with insights into overall team performance through a comprehensive flow.

[Live Dashboard URL](https://mbo-nba-stats.streamlit.app/)

## Project Design
### Scopes:
- Team statistics:
    - Season standing
    - Topline traditional stats
    - Boxscore advanced stats
    - Games played stats

- Roster statistics:
    - Players season stats

- Season 2024 and onward

## Installation & Setup
### Prerequisites
- Python 3.10+
- Streamlit account
- Snowflake account

### Installation
1. Clone the project repo:
    ```
    git clone https://github.com/mbo0000/nba_e2e_streamlit_dash_app
    cd streamlit-nba-web-dash
    ```
2. Installing required packages:
    ```
    pip install -r requirements.txt
    ```
3. Create Snowflake connection:
    Create a secrets.toml file for Snowflake credentials. For more information, visit Streamlit's [documentation](https://docs.streamlit.io/develop/tutorials/databases/snowflake).
    ```
    mkdir .streamlit
    touch .streamlit/secrets.toml
    ```

    Provide your Snowflake credentials(Snowflake [Management and Config
](https://github.com/mbo0000/nba_e2e_data_pipeline?tab=readme-ov-file#1-snowflake-management-and-config)).
    ```
    [connections.snowflake]
    account = "xxxxxxx-xxxxxxx"
    user = "xxx"
    private_key_file = "../xxx/xxx.p8"
    role = "xxx"
    warehouse = "xxx"
    database = "xxx"
    schema = "xxx"
    ```

4. Locally run Streamlit app:
    ```
    streamlit run app.py
    ```
## Future Work & Improvement
- Create a player stats focused page
- Adding shots selection chart