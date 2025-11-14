import streamlit as st
import preprocessor
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from wordcloud import WordCloud, STOPWORDS
from collections import Counter
import emoji

# --- GLOBAL CONSTANTS & STOP WORDS ---

# Defining the robust media pattern once
MEDIA_PATTERN = r'<\s*[Mm]edia\s+[Oo]mitted\s*>'

# Define custom stop words (common chat words to ignore)
CUSTOM_STOP_WORDS = set([
    "media", "omitted", "hai", "bhai", "kya", "ko", "se", "na",
    "to", "h", "m", "ka", "ki", "ye", "hi", "he", "ke", "nhi",
    "gayi", "ho", "gaya", "toh", "sir", "mam", "ok", "lekin"
])
# Combine default English stop words with our custom list
ALL_STOP_WORDS = STOPWORDS.union(CUSTOM_STOP_WORDS)


# --- ANALYSIS FUNCTIONS ---

def fetch_stats(df_to_analyze):
    """Calculates overall statistics for the given DataFrame."""

    total_messages = df_to_analyze.shape[0]

    # 🎯 ACTION: This function counts media based on the pattern
    media_messages_count = df_to_analyze['message'].str.contains(
        MEDIA_PATTERN,
        case=False,
        na=False,
        regex=True
    ).sum()

    # Filter for non-media messages to count words and links
    non_media_messages = df_to_analyze[
        ~df_to_analyze['message'].str.contains(MEDIA_PATTERN, case=False, na=False, regex=True)
    ]

    words = []
    for message in non_media_messages['message']:
        words.extend(str(message).split())
    total_words = len(words)

    links = []
    for message in df_to_analyze['message']:
        links.extend(re.findall(r'(https?://\S+)', str(message)))
    total_links = len(links)

    return total_messages, total_words, media_messages_count, total_links


def get_most_busy_users(df):
    """
    Returns ALL users and their message percentage, sorted by message count.
    (Excluding system messages and media messages from the 'active' count)
    """
    df_active = df[
        (df['user'] != 'group_notification') &
        (~df['message'].str.contains(MEDIA_PATTERN, case=False, na=False, regex=True))
        ]

    user_counts = df_active['user'].value_counts()

    total_messages = df_active.shape[0]
    if total_messages == 0:
        return pd.Series(), pd.Series()

    user_percentage = round((user_counts / total_messages) * 100, 2)

    return user_counts, user_percentage


def fetch_media_messages(df_to_analyze):
    """
    Filters the DataFrame to return only rows corresponding to media files.
    """
    media_df = df_to_analyze[
        df_to_analyze['message'].str.contains(MEDIA_PATTERN, case=False, na=False, regex=True)
    ].copy()

    return media_df[['date', 'user', 'message']]


def create_wordcloud(df_to_analyze):
    """
    Generates a Word Cloud image from all messages in the DataFrame.
    """
    # Filter out media messages before generating word cloud
    df_text = df_to_analyze[
        ~df_to_analyze['message'].str.contains(MEDIA_PATTERN, case=False, na=False, regex=True)
    ]
    all_text = " ".join(str(msg).lower() for msg in df_text['message'])

    if not all_text:
        return None

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=ALL_STOP_WORDS,
        min_font_size=10
    ).generate(all_text)

    return wordcloud


def get_most_common_words(df_to_analyze, num_words=20):
    """
    Gets the most common words and their counts.
    """

    # Filter out media messages before getting common words
    df_text = df_to_analyze[
        ~df_to_analyze['message'].str.contains(MEDIA_PATTERN, case=False, na=False, regex=True)
    ]

    all_words = []
    for message in df_text['message']:
        words = str(message).lower().split()
        for word in words:
            if word not in ALL_STOP_WORDS and not word.startswith('http'):
                all_words.append(word)

    if not all_words:
        return pd.DataFrame(columns=["Word", "Count"])

    word_counts = Counter(all_words).most_common(num_words)

    df_common_words = pd.DataFrame(word_counts, columns=['Word', 'Count'])
    return df_common_words


def get_most_common_emojis(df_to_analyze, num_emojis=10):
    """
    Extracts, counts, and returns the most common emojis.
    """
    emojis_list = []

    for message in df_to_analyze['message']:
        for e in emoji.emoji_list(str(message)):
            emojis_list.append(e['emoji'])

    if not emojis_list:
        return pd.DataFrame(columns=["Emoji", "Count"])

    emoji_counts = Counter(emojis_list).most_common(num_emojis)

    df_common_emojis = pd.DataFrame(emoji_counts, columns=['Emoji', 'Count'])
    return df_common_emojis


def create_monthly_timeline(df_to_analyze):
    """
    Calculates the number of messages sent per month-year and returns it for plotting.
    """

    if 'month_year' not in df_to_analyze.columns:
        return pd.DataFrame(columns=['month_year', 'messages'])

    timeline = df_to_analyze.groupby(['month_year']).size().reset_index(name='messages')

    timeline['time'] = pd.to_datetime(timeline['month_year'], format='%B-%Y', errors='coerce')
    timeline.sort_values(by='time', inplace=True)

    return timeline


def create_daily_timeline(df_to_analyze):
    """
    Calculates the number of messages sent per day and returns it for plotting.
    """
    daily_df = df_to_analyze.groupby(df_to_analyze['date'].dt.date).size().reset_index(name='messages')

    daily_df.rename(columns={'date': 'day'}, inplace=True)
    daily_df['day_str'] = daily_df['day'].astype(str)

    return daily_df


def get_most_busy_day_stats(df_to_analyze):
    """
    Calculates the number of messages sent per day of the week and ensures correct sorting.
    """
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    day_counts = df_to_analyze['day_name'].value_counts().reset_index()
    day_counts.columns = ['Day', 'Message Count']

    day_counts['Day'] = pd.Categorical(day_counts['Day'], categories=day_order, ordered=True)
    day_counts.sort_values('Day', inplace=True)

    return day_counts


def get_most_busy_month_stats(df_to_analyze):
    """
    Calculates the number of messages sent per month name and ensures correct sorting.
    """
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    month_counts = df_to_analyze['month_name'].value_counts().reset_index()
    month_counts.columns = ['Month', 'Message Count']

    month_counts['Month'] = pd.Categorical(month_counts['Month'], categories=month_order, ordered=True)
    month_counts.sort_values('Month', inplace=True)

    return month_counts


def create_weekly_activity_heatmap(df_to_analyze):
    """
    Creates a pivot table of message counts by day of the week and hour of the day.
    """
    if df_to_analyze.empty:
        return pd.DataFrame()

    # Create the 'hour' column (0 to 23)
    df_to_analyze.loc[:, 'hour'] = df_to_analyze['date'].dt.hour

    # Define the correct order for days and hours
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hour_order = list(range(24))  # 0 to 23

    # Pivot the data to get message counts by day and hour
    activity_map = df_to_analyze.pivot_table(
        index='day_name',
        columns='hour',
        values='message',
        aggfunc='count'
    ).fillna(0)  # Fill NaN (periods with no messages) with 0

    # Reindex rows and columns to ensure correct order, filling missing ones with 0
    activity_map = activity_map.reindex(index=day_order, columns=hour_order, fill_value=0)

    return activity_map


# --- STREAMLIT APP LAYOUT ---

st.sidebar.title("📊 WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("📂 Upload your WhatsApp chat file (.txt)", type=["txt"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor.preprocess(data)

    # --- Date Component Creation for Timeline ---
    if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']):
        df['year'] = df['date'].dt.year
        df['month_num'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.strftime('%B')
        df['month_year'] = df['date'].dt.strftime('%B-%Y')
        df['day_name'] = df['date'].dt.day_name()
    else:
        st.error("Error: Preprocessing failed to create a valid 'date' column. Cannot run analysis.")
        st.stop()
    # --- End Date Component Creation ---

    system_patterns = (
        r'changed the group|added|removed|joined using|left|created group|'
        r'Messages and calls are|Missed voice call|end-to-end encrypted|'
        r'pinned a message|You deleted this message|This message was deleted'
    )
    df_filtered = df.copy()

    # 1. System Message Filtering (KEEPING MEDIA MESSAGES)
    df_filtered = df_filtered[
        ~df_filtered['message'].str.contains(system_patterns, case=False, na=False)
    ]
    df_filtered = df_filtered[
        ~df_filtered['user'].str.contains(system_patterns, case=False, na=False)
    ]
    df_filtered = df_filtered[df_filtered['user'].notna() & (df_filtered['user'].str.strip() != '')]

    # 🎯 IMPORTANT: We explicitly do NOT filter out media messages here.
    # The media messages (<Media omitted>) MUST remain in df_filtered
    # so that the 'Total Messages' count, 'Media Shared' count, and
    # 'Media Timeline' display them correctly.

    # --- USER SELECTION AND FILTERING ---
    user_list = sorted(df_filtered['user'].unique().tolist())

    user_list = [
        user for user in user_list
        if 'group' not in user.lower() and 'notification' not in user.lower()
    ]
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if selected_user != 'Overall':
        df_to_analyze = df_filtered[df_filtered['user'] == selected_user].copy()
    else:
        df_to_analyze = df_filtered.copy()

    # --- DASHBOARD/ANALYSIS LAYOUT ---
    st.title("💬 WhatsApp Chat Analysis")

    if df_to_analyze.empty:
        st.warning(f"No active messages found for **{selected_user}** after cleaning.")
    else:
        # 1. TOP STATISTICS
        st.header("1. Top Statistics 🏆")

        total_messages, total_words, media_messages_count, total_links = fetch_stats(df_to_analyze)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Messages 💬", value=total_messages)
        with col2:
            st.metric(label="Total Words ✍️", value=total_words)
        with col3:
            st.metric(label="Media Shared 🖼️", value=media_messages_count)
        with col4:
            st.metric(label="Links Shared 🔗", value=total_links)

        st.markdown("---")

        # 2. WORD CLOUD
        st.header(f"2. Word Cloud for: {selected_user} ☁️")

        wordcloud_image = create_wordcloud(df_to_analyze)

        if wordcloud_image:
            fig, ax = plt.subplots()
            ax.imshow(wordcloud_image, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
        else:
            st.info(f"Not enough text to generate a word cloud for **{selected_user}**.")

        st.markdown("---")

        # 3. MOST COMMON WORDS
        st.header(f"3. Most Common Words for: {selected_user} 🗣️")

        df_common_words = get_most_common_words(df_to_analyze, num_words=20)

        if not df_common_words.empty:

            st.markdown("#### Top 20 Words (Table)")
            st.dataframe(df_common_words, use_container_width=True)

            st.markdown("#### Top 20 Words (Bar Chart)")

            fig, ax = plt.subplots(figsize=(12, 8))

            sns.barplot(x='Word', y='Count', data=df_common_words, ax=ax, palette='viridis')

            ax.set_xticklabels(df_common_words['Word'], rotation='vertical')
            ax.set_title(f'Top {len(df_common_words)} Most Common Words')
            ax.set_xlabel('Word')
            ax.set_ylabel('Frequency')

            st.pyplot(fig)

        else:
            st.info(f"Not enough text to find common words for **{selected_user}**.")

        st.markdown("---")

        # 4. MONTHLY ACTIVITY TIMELINE
        st.header("4. Monthly Activity Timeline 📆")

        timeline_df = create_monthly_timeline(df_to_analyze)

        if not timeline_df.empty:
            st.markdown("#### Messages Sent Per Month")

            fig, ax = plt.subplots(figsize=(12, 6))

            ax.plot(timeline_df['month_year'], timeline_df['messages'], color='green', marker='o')

            ax.set_xticklabels(timeline_df['month_year'], rotation='vertical')
            ax.set_title(f'Monthly Message Trend for {selected_user}')
            ax.set_xlabel('Month-Year')
            ax.set_ylabel('Message Count')
            ax.grid(axis='y', linestyle='--')

            st.pyplot(fig)
        else:
            st.info(f"Not enough data to create a monthly timeline for **{selected_user}**.")

        st.markdown("---")

        # 5. DAILY ACTIVITY TIMELINE
        st.header("5. Daily Activity Timeline 📈")

        daily_timeline_df = create_daily_timeline(df_to_analyze)

        if not daily_timeline_df.empty:
            st.markdown("#### Messages Sent Per Day")

            fig, ax = plt.subplots(figsize=(12, 6))

            ax.plot(daily_timeline_df['day_str'], daily_timeline_df['messages'], color='darkblue', marker='.')

            step_size = max(1, len(daily_timeline_df) // 15)

            ax.set_xticks(daily_timeline_df['day_str'][::step_size])
            ax.set_xticklabels(daily_timeline_df['day_str'][::step_size], rotation='vertical')

            ax.set_title(f'Daily Message Trend for {selected_user}')
            ax.set_xlabel('Date (YYYY-MM-DD)')
            ax.set_ylabel('Message Count')
            ax.grid(axis='y', linestyle='--')

            st.pyplot(fig)
        else:
            st.info(f"Not enough data to create a daily timeline for **{selected_user}**.")

        st.markdown("---")

        # 6. MOST BUSY DAY ANALYSIS
        st.header("6. Most Busy Day Analysis 🗓️")

        busy_day_df = get_most_busy_day_stats(df_to_analyze)

        if not busy_day_df.empty:
            st.markdown("#### Message Count by Day of the Week")

            fig, ax = plt.subplots(figsize=(10, 6))

            sns.barplot(x='Day', y='Message Count', data=busy_day_df, ax=ax, palette='plasma')

            ax.set_title(f'Activity by Day of the Week for {selected_user}')
            ax.set_xlabel('Day of the Week')
            ax.set_ylabel('Total Messages')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--')

            st.pyplot(fig)

        else:
            st.info(f"Not enough data to create a busy day analysis for **{selected_user}**.")

        st.markdown("---")

        # 7. MOST BUSY MONTH ANALYSIS
        st.header("7. Most Busy Month Analysis 🗓️")

        busy_month_df = get_most_busy_month_stats(df_to_analyze)

        if not busy_month_df.empty:
            st.markdown("#### Message Count by Month of the Year")

            fig, ax = plt.subplots(figsize=(12, 6))

            sns.barplot(x='Month', y='Message Count', data=busy_month_df, ax=ax, palette='cubehelix')

            ax.set_title(f'Activity by Month of the Year for {selected_user}')
            ax.set_xlabel('Month')
            ax.set_ylabel('Total Messages')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--')

            st.pyplot(fig)

        else:
            st.info(f"Not enough data to create a busy month analysis for **{selected_user}**.")

        st.markdown("---")

        # 8. WEEKLY ACTIVITY HEATMAP
        st.header("8. Weekly Activity Heatmap 🔥")

        activity_map_df = create_weekly_activity_heatmap(df_to_analyze)

        if not activity_map_df.empty and activity_map_df.sum().sum() > 0:
            st.markdown("#### Weekly Activity Map (Time vs Day)")

            fig, ax = plt.subplots(figsize=(16, 7))

            # Create the heatmap
            sns.heatmap(
                activity_map_df,
                cmap='YlGnBu',
                ax=ax,
                linewidths=0.5,
                linecolor='lightgrey',
                cbar_kws={'label': 'Message Count'}
            )

            ax.set_title(f'Weekly Activity Map for {selected_user}')
            ax.set_xlabel('Hour of Day (0-23)')
            ax.set_ylabel('Day of Week')

            st.pyplot(fig)

        else:
            st.info(f"Not enough data to create a weekly activity heatmap for **{selected_user}**.")

        st.markdown("---")

        # 9. MOST COMMON EMOJIS (Renumbered)
        st.header(f"9. Most Common Emojis for: {selected_user} 😅")

        df_common_emojis = get_most_common_emojis(df_to_analyze, num_emojis=10)

        if not df_common_emojis.empty:
            col_emoji_table, col_emoji_chart = st.columns(2)

            with col_emoji_table:
                st.markdown("#### Top 10 Emojis (Table)")
                st.markdown('<style> .dataframe td { font-size: 20px; } </style>', unsafe_allow_html=True)
                st.dataframe(df_common_emojis, use_container_width=True)

            with col_emoji_chart:
                st.markdown("#### Top 10 Emojis (Bar Chart)")
                fig, ax = plt.subplots()

                ax.bar(df_common_emojis['Emoji'], df_common_emojis['Count'], color='lightcoral')

                ax.set_xticklabels(df_common_emojis['Emoji'], fontsize=18)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Top {len(df_common_emojis)} Emojis Used')
                st.pyplot(fig)

        else:
            st.info(f"No emojis found for **{selected_user}**.")

        st.markdown("---")

        # 10. MEDIA MESSAGES LIST (Renumbered)
        st.header("10. Shared Media Timeline 🖼️")

        media_df_to_show = fetch_media_messages(df_to_analyze)

        if not media_df_to_show.empty:
            media_df_to_show['Content Type'] = media_df_to_show['message']
            media_df_to_show = media_df_to_show.drop(columns=['message'])

            st.info(
                "The actual media files cannot be displayed, as the exported chat file only contains the placeholder text.")
            st.dataframe(media_df_to_show.rename(columns={
                'date': 'Date & Time',
                'user': 'Sender'
            }), use_container_width=True)
        else:
            st.info(f"No media messages found for **{selected_user}**.")

        st.markdown("---")

        # 11. MOST BUSY USERS (Renumbered)
        if selected_user == 'Overall':
            st.header("11. User Activity 👥")

            user_counts, user_percentage = get_most_busy_users(df_filtered)

            if not user_counts.empty:
                col5, col6 = st.columns(2)

                with col5:
                    st.markdown("#### Activity (All Users)")
                    st.dataframe(pd.DataFrame({
                        'User': user_counts.index,
                        'Messages': user_counts.values,
                        'Percentage': user_percentage.values
                    }))

                with col6:
                    st.markdown("#### Top 10 Most Active Users")
                    user_percentage_top10 = user_percentage.head(10)

                    fig, ax = plt.subplots()
                    sns.barplot(x=user_percentage_top10.index, y=user_percentage_top10.values, ax=ax, palette="viridis")
                    ax.set_xticklabels(user_percentage_top10.index, rotation='vertical')
                    ax.set_ylabel('Message Share (%)')
                    st.pyplot(fig)
            else:
                st.info("Not enough message data for busy user analysis.")