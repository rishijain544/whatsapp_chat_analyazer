Here is a comprehensive `README.md` file tailored specifically for your "WhatsApp Chat Analyzer" project.

-----

# 💬 WhatsApp Chat Analyzer

[](https://www.python.org/)
[](https://streamlit.io/)
[](https://opensource.org/licenses/MIT)

A web application built with Streamlit and Python to analyze, visualize, and gain insights from your exported WhatsApp chat files. This tool provides a detailed breakdown of chat activity, user patterns, language usage, and engagement trends for both group chats and individual conversations.

## ✨ Features

This analyzer provides a comprehensive dashboard with 11 distinct analysis modules, available for the **Overall** chat and for **each individual user**:

1.  **🏆 Top Statistics:** At-a-glance metrics for:

      * Total Messages
      * Total Words
      * Total Media Shared
      * Total Links Shared

2.  **☁️ Word Cloud:** A beautiful visualization of the most frequently used words in the chat, ignoring common stop words.

3.  **🗣️ Most Common Words:** A table and bar chart displaying the top 20 most frequently used words and their counts.

4.  **📅 Monthly Activity Timeline:** A line graph showing the total number of messages sent for each month over the years, visualizing the chat's long-term activity cycles.

5.  **📈 Daily Activity Timeline:** A detailed line graph showing message counts for every single day, perfect for identifying specific bursts of activity.

6.  **🗓️ Most Busy Day:** A bar chart illustrating the most active day of the week (e.g., Monday vs. Sunday).

7.  **🗓️ Most Busy Month:** A bar chart showing the most active month of the year (e.g., January vs. August).

8.  **🔥 Weekly Activity Heatmap:** A powerful heatmap that cross-references the **Day of the Week** with the **Hour of the Day** to show the exact times the chat is most active.

9.  **😅 Most Common Emojis:** A table and bar chart of the top 10 emojis used, providing insight into the group's tone.

10. **🖼️ Shared Media Timeline:** A scrollable table listing all media messages sent, along with the sender and timestamp.

11. **👥 User Activity (Overall only):**

      * A table of **all users** ranked by message count and their percentage contribution.
      * A bar chart visualizing the **Top 10 Most Active Users**.

-----

## 🛠️ Tech Stack

  * **Framework:** [Streamlit](https://streamlit.io/)
  * **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
  * **Plotting:** [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/)
  * **Text Processing:** [WordCloud](https://github.com/amueller/word_cloud), [emoji](https://pypi.org/project/emoji/), `re` (Regular Expressions)

-----

## 🚀 How to Run Locally

### 1\. Prerequisites

  * Python 3.9+
  * `pip` and `venv`

### 2\. Clone the Repository

```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
cd <YOUR_REPO_NAME>
```

### 3\. Create a Virtual Environment

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4\. Install Dependencies

Create a `requirements.txt` file in the main directory with the following content:

```txt
streamlit
pandas
matplotlib
seaborn
emoji
wordcloud
```

Then, install them using `pip`:

```bash
pip install -r requirements.txt
```

### 5\. Run the Application

From your terminal, run:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser.

-----

## 💡 How to Use

1.  **Export Your Chat:**

      * Open any WhatsApp chat (group or individual).
      * Tap the three-dot menu (⋮) \> **More** \> **Export chat**.
      * **Crucially, select "Without Media"**.
      * Save the exported `.txt` file.

2.  **Upload the File:**

      * Drag and drop the `.txt` file onto the uploader in the app's sidebar.

3.  **Analyze\!**

      * The app will instantly process the data and display the full analysis.
      * Use the **"Show analysis for"** dropdown in the sidebar to toggle between the "Overall" group analysis and the analysis for any specific user.

-----

## 📂 File Structure

```
.
├── 📄 app.py              # Main Streamlit application file (UI and analysis functions)
├── 📄 preprocessor.py    # Module for parsing and cleaning the raw .txt file
├── 📄 requirements.txt    # List of all Python dependencies
└── 📄 README.md           # This file
```

-----
