import streamlit as st
import datetime
import pyperclip

rates = ['Weekday', 'Saturday', 'Sunday', 'Public Holiday']
categories = ['CSE', 'PDA', 'Group']
locs = ['@1213GHR', '@Participants', '@Travel']

st.title("Formatter App")

# --- DATE INPUT ---
selected_date = st.date_input("Choose a date", datetime.date.today())
public_holiday = st.checkbox("Is it a public holiday?")

# --- DETERMINE RATE (Weekday/Sat/Sun/PH) ---
if public_holiday:
    rate = "Public Holiday"
elif selected_date.weekday() == 5:
    rate = "Saturday"
elif selected_date.weekday() == 6:
    rate = "Sunday"
else:
    rate = "Weekday"

# --- TIME FORMATTER (keep 24-hr hour, add am/pm suffix) ---
def format_24hr_with_suffix(time_str: str) -> str:
    """
    Convert a 4-digit time_str in 24-hour format into HH:MM + am/pm
    Examples:
      '0900' -> '09:00am'
      '1305' -> '13:05pm'
      '0005' -> '00:05am'
    """
    # Basic validation
    if len(time_str) != 4 or not time_str.isdigit():
        return time_str  # fallback if user typed something unusual

    hour = int(time_str[:2])
    minute = int(time_str[2:])

    # If hour < 12 => 'am', else 'pm'
    suffix = "am" if hour < 12 else "pm"
    
    # Keep the hour as entered (24-hr style),
    # but append the suffix based on <12 or >=12
    return f"{hour:02d}:{minute:02d}{suffix}"

# --- TIME INPUTS ---
start_time_raw = st.text_input("Start time (24hr format, e.g. 0900)", "0900")
end_time_raw = st.text_input("End time (24hr format, e.g. 1700)", "1700")

start_time_display = format_24hr_with_suffix(start_time_raw)
end_time_display   = format_24hr_with_suffix(end_time_raw)

break_minutes = st.text_input("How many minutes on break (0 for none)", "0")
break_str = f" ({break_minutes} Minutes Less)" if break_minutes != "0" else ""

period = f"{start_time_display}-{end_time_display}{break_str}"

# --- CATEGORY ---
category = st.selectbox("Choose a category", categories)
hours = st.text_input("Number of hours", "8")

# --- PARTICIPANTS ---
participants_input = []
if category == 'Group':
    num_participants = st.number_input("How many participants?", min_value=1, value=2, step=1)
    for i in range(int(num_participants)):
        name = st.text_input(f"Participant {i+1} name", key=f"participant_{i+1}")
        if name.strip():
            participants_input.append(name.strip())
    category_str = f"Group({int(num_participants)})"
else:
    single_name = st.text_input("Participant Name", "")
    if single_name.strip():
        participants_input.append(single_name.strip())
    category_str = category

# Format participants for final output
if len(participants_input) > 1:
    participants_str = "[" + ", ".join(participants_input) + "]"
elif len(participants_input) == 1:
    participants_str = participants_input[0]
else:
    participants_str = ""

# --- LOCATIONS ---
st.write("Select one or more locations:")
selected_locs = []
for loc in locs:
    if st.checkbox(loc, key=loc):
        selected_locs.append(loc)

# If "@Travel" is selected, ask for distance
if "@Travel" in selected_locs:
    distance = st.text_input("Enter travel distance in km (or 'n' to skip)", "n")
    if distance.lower() != "n":
        idx = selected_locs.index("@Travel")
        selected_locs[idx] = f"@Travel ({distance} km)"

# Format locations for final output
if len(selected_locs) > 1:
    locs_str = "[" + ", ".join(selected_locs) + "]"
elif len(selected_locs) == 1:
    locs_str = selected_locs[0]
else:
    locs_str = ""

# --- BUILD OUTPUT ---
formatted_date = selected_date.strftime("%a, %b %d, %Y")

final_string = (
    f"{hours} Hours [{rate}, {category_str}], "
    f"{formatted_date}, {period}, "
    f"{participants_str}, {locs_str}"
)

st.subheader("Final String")
st.write(final_string)

if st.button("Copy to Clipboard"):
    pyperclip.copy(final_string)
    st.success("Copied to clipboard!")
