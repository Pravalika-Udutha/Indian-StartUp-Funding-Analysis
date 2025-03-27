import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(layout='wide',page_title='StartUp Analysis')

# Data Loading
df = pd.read_csv('startup_cleaned.csv')

# feature extraction
df['date'] = pd.to_datetime(df['date'],errors='coerce')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# Optional: Apply a global style (can be omitted if you prefer manual customization)
sns.set_style('whitegrid') # Enhances default aesthetics

# Define a purple-themed color palette
PURPLE_PALETTE = ['#800080', '#9B59B6', '#BCA0DC', '#D7BDE2', '#E6B0FA']  # Shades of purple
COMPLEMENTARY_COLOR = '#FFA500'  # Orange as a complementary accent

# overall analysis
def load_overall_analysis():
    st.title('Overall Analysis')

    # total invested amount
    total = round(df['amount'].sum())

    # max amount infused in a startup
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    
    # avg ticket size
    avg_funding = df.groupby('startup')['amount'].sum().mean()
    
    # total funded startups
    num_startups = df['startup'].nunique()

    col1,col2,col3,col4 = st.columns(4)

    with col1:
        st.metric('Total',str(total) + ' Cr')
    with col2:
        st.metric('Max', str(max_funding) + ' Cr')

    with col3:
        st.metric('Avg',str(round(avg_funding)) + ' Cr')

    with col4:
        st.metric('Funded Startups',num_startups)

    st.header('MoM graph')
    
    selected_option = st.selectbox('Select Type',['Total','Count'])
    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()

    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.plot(temp_df['x_axis'], temp_df['amount'], 
             marker='o', linewidth=2.5, color=PURPLE_PALETTE[0], 
             markersize=8, markerfacecolor=COMPLEMENTARY_COLOR, markeredgecolor='black')
    ax3.set_title(f'Month-over-Month {selected_option}', fontsize=16, fontweight='bold', color='#333333', pad=15)
    ax3.set_xlabel('Month-Year', fontsize=12)
    ax3.set_ylabel(f'{selected_option} (Cr)', fontsize=12)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.set_facecolor('#f9f9f9')  # Light background
    fig3.patch.set_facecolor('#ffffff')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    st.pyplot(fig3)


# Investor analysis
def load_investor_details(investor):
    st.title(investor)
    
    # load the recent 5 investments of the investor
    last5_df = df[df['investors'].str.contains(investor)].head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    
    st.subheader('Most Recent Investments')
    st.dataframe(last5_df)

    col1, col2 = st.columns(2)
    with col1:
        # biggest investments
        big_series = df[df['investors'].str.contains(investor)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investments')
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(big_series.index, big_series.values, color=PURPLE_PALETTE[1], edgecolor='black', linewidth=1)
        ax.set_title('Top Startups by Investment', fontsize=14, fontweight='bold', pad=10)
        ax.set_xlabel('Startup', fontsize=12)
        ax.set_ylabel('Amount (Cr)', fontsize=12)
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)
        ax.set_facecolor('#f9f9f9')
        fig.patch.set_facecolor('#ffffff')
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        vertical_series = df[df['investors'].str.contains(investor, na=False)].groupby('vertical')['amount'].sum().dropna()
        if vertical_series.isna().all() or len(vertical_series) == 0:
            st.write("No valid investment data available for this investor.")
        else:
            st.subheader('Sectors Invested In')
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            ax1.pie(vertical_series, labels=vertical_series.index, autopct='%0.1f%%', 
                    colors=['#800080', '#9B59B6', '#BCA0DC', '#D7BDE2', '#E6B0FA'][:len(vertical_series)], 
                    startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}, 
                    textprops={'fontsize': 12, 'fontweight': 'bold'})
            ax1.set_title('Sector Distribution', fontsize=14, fontweight='bold', pad=10)
            fig1.patch.set_facecolor('#ffffff')
            ax1.axis('equal')
            plt.tight_layout()
            st.pyplot(fig1)

    print(df.info())

    df['year'] = df['date'].dt.year
    year_series = df[df['investors'].str.contains(investor)].groupby('year')['amount'].sum()

    st.subheader('YoY Investment')
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    ax2.plot(year_series.index, year_series.values, 
             marker='o', linewidth=2.5, color=PURPLE_PALETTE[2], 
             markersize=8, markerfacecolor=COMPLEMENTARY_COLOR, markeredgecolor='black')
    ax2.set_title('Year-over-Year Investment', fontsize=14, fontweight='bold', pad=10)
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Amount (Cr)', fontsize=12)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_facecolor('#f9f9f9')
    fig2.patch.set_facecolor('#ffffff')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    st.pyplot(fig2)


# UI for Analysis
st.sidebar.title('Startup Funding Analysis')

option = st.sidebar.selectbox('Select One',['Overall Analysis','Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()


else:
    selected_investor = st.sidebar.selectbox('Select StartUp',sorted(set(df['investors'].str.split(',').sum())))
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
