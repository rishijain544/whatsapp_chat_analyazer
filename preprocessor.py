import re
import pandas as pd


def preprocess(data):
    # Pattern to identify the *start* of a new message line
    # It matches (Date), (Time), and then (The rest of the line)
    pattern = r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s*(\d{1,2}:\d{2}\s*[apAP]m)\s*-\s*(.*)"

    # Replace the problematic "narrow no-break space" (U+202F) with a regular space
    data = data.replace('\u202f', ' ')

    lines = data.splitlines()

    parsed_messages = []
    current_message_data = None

    for line in lines:
        match = re.match(pattern, line)

        if match:
            # --- 1. This is a NEW message line ---

            # First, if a message was being built, save it.
            if current_message_data:
                parsed_messages.append(current_message_data)

            # Now, start the new message
            date_time_str = f"{match.group(1)}, {match.group(2)}"
            message_content_part = match.group(3)

            # Split the content part into User and Message
            user_match = re.match(r'^(.*?):\s*(.*)', message_content_part)

            if user_match:
                # Standard user message (e.g., "Mohit NIMS: Hello")
                user = user_match.group(1).strip()
                message_text = user_match.group(2).strip()
            else:
                # This is a group notification (e.g., "Mohit NIMS added you")
                user = 'group_notification'
                message_text = message_content_part.strip()

            # Store the new message data
            current_message_data = {
                'date_time': date_time_str,
                'user': user,
                'message': message_text
            }

        elif current_message_data:
            # --- 2. This is a CONTINUATION line ---
            # Append this line's text to the 'message' of the current message
            current_message_data['message'] += '\n' + line.strip()

    # After the loop, save the very last message
    if current_message_data:
        parsed_messages.append(current_message_data)

    if not parsed_messages:
        print("⚠️ No messages found — check chat format or export type.")
        return pd.DataFrame()

    # --- 3. Create DataFrame ---
    df = pd.DataFrame(parsed_messages)

    # Rename column and convert to datetime
    df.rename(columns={'date_time': 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y, %I:%M %p', errors='coerce')

    # Drop any rows that failed date parsing
    df.dropna(subset=['date'], inplace=True)

    # Filter out group notifications *after* parsing
    df = df[df['user'] != 'group_notification']

    # --- 4. Add Date Components ---
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.strftime('%B')
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.strftime('%A')
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute
    df['month_year'] = df['date'].dt.strftime('%B-%Y')

    return df