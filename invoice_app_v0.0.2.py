import streamlit as st
import datetime
import pyperclip

# ---------------------- INITIAL SETUP ----------------------
def init_session_state():
    # Rates (fixed, read-only)
    if "rates" not in st.session_state:
        st.session_state["rates"] = ["Weekday", "Saturday", "Sunday", "Public Holiday"]
    
    # User-managed lists
    if "participants" not in st.session_state:
        st.session_state["participants"] = ["Alice", "Bob"]
    if "categories" not in st.session_state:
        st.session_state["categories"] = ["CSE", "Group"]
    if "locations" not in st.session_state:
        st.session_state["locations"] = [ "@Travel", "@Participants"]
    
    # session_logs: list of dicts
    # Each dict: {
    #   "participants": list[str],  # possibly multiple
    #   "date": date,
    #   "start_time": str (4-digit "HHMM"),
    #   "end_time": str (4-digit "HHMM"),
    #   "break_mins": int,
    #   "rate": str,
    #   "category": str,
    #   "hours": float,
    #   "locations": list[str]
    # }
    if "session_logs" not in st.session_state:
        st.session_state["session_logs"] = []

# ---------------------- TIME FORMATTER ----------------------
def format_24hr_with_suffix(time_str: str) -> str:
    """
    Convert a 4-digit time_str in 24-hour format into HH:MM + am/pm,
    preserving the 24-hour hour number.
      e.g. '0900' -> '09:00am'
           '1305' -> '13:05pm'
    """
    if len(time_str) != 4 or not time_str.isdigit():
        return time_str
    hour = int(time_str[:2])
    minute = int(time_str[2:])
    suffix = "am" if hour < 12 else "pm"
    return f"{hour:02d}:{minute:02d}{suffix}"

# ---------------------- CONFIGURATION PAGE ----------------------
def page_configuration():
    st.header("Configuration")
    
    # ----- Participants -----
    st.subheader("Manage Participants")
    with st.form(key="add_participant_form", clear_on_submit=True):
        new_participant = st.text_input("Add a new participant", "")
        submitted_add_participant = st.form_submit_button("Add Participant")
        if submitted_add_participant:
            if new_participant.strip():
                st.session_state["participants"].append(new_participant.strip())
                st.success(f"Added participant: {new_participant.strip()}")
            else:
                st.warning("Participant name cannot be empty.")
    if st.session_state["participants"]:
        st.write("Current participants:")
        # Remove participant
        with st.form(key="remove_participant_form"):
            remove_part = st.selectbox(
                "Select a participant to remove",
                options=["(None)"] + st.session_state["participants"],
                label_visibility="collapsed",
            )
            submitted_remove_participant = st.form_submit_button("Remove Participant")
            if submitted_remove_participant:
                if remove_part != "(None)":
                    st.session_state["participants"].remove(remove_part)
                    st.success(f"Removed participant: {remove_part}")
                    st.experimental_rerun()
        for p in st.session_state["participants"]:
            st.write(f"- {p}")
    st.divider()

    # ----- Categories -----
    st.subheader("Manage Categories")
    with st.form(key="add_category_form", clear_on_submit=True):
        new_category = st.text_input("Add a new category", "")
        submitted_add_cat = st.form_submit_button("Add Category")
        if submitted_add_cat:
            if new_category.strip():
                st.session_state["categories"].append(new_category.strip())
                st.success(f"Added category: {new_category.strip()}")
            else:
                st.warning("Category cannot be empty.")
    if st.session_state["categories"]:
        st.write("Current categories:")
        # Remove category
        with st.form(key="remove_category_form"):
            remove_cat = st.selectbox(
                "Select a category to remove",
                options=["(None)"] + st.session_state["categories"],
                label_visibility="collapsed",
            )
            submitted_remove_cat = st.form_submit_button("Remove Category")
            if submitted_remove_cat:
                if remove_cat != "(None)":
                    st.session_state["categories"].remove(remove_cat)
                    st.success(f"Removed category: {remove_cat}")
                    st.experimental_rerun()
        for c in st.session_state["categories"]:
            st.write(f"- {c}")
    st.divider()

    # ----- Locations -----
    st.subheader("Manage Locations")
    with st.form(key="add_location_form", clear_on_submit=True):
        new_location = st.text_input("Add a new location (will prefix '@' if missing)", "")
        submitted_add_loc = st.form_submit_button("Add Location")
        if submitted_add_loc:
            loc = new_location.strip()
            if loc:
                if not loc.startswith("@"):
                    loc = "@" + loc
                st.session_state["locations"].append(loc)
                st.success(f"Added location: {loc}")
            else:
                st.warning("Location cannot be empty.")
    if st.session_state["locations"]:
        st.write("Current locations:")
        # Remove location
        with st.form(key="remove_location_form"):
            remove_loc = st.selectbox(
                "Select a location to remove",
                options=["(None)"] + st.session_state["locations"],
                label_visibility="collapsed",
            )
            submitted_remove_loc = st.form_submit_button("Remove Location")
            if submitted_remove_loc:
                if remove_loc != "(None)":
                    st.session_state["locations"].remove(remove_loc)
                    st.success(f"Removed location: {remove_loc}")
                    st.experimental_rerun()
        for loc in st.session_state["locations"]:
            st.write(f"- {loc}")
    st.divider()

    # ----- Rates (fixed, read-only) -----
    st.subheader("Rates (Fixed)")
    for rate in st.session_state["rates"]:
        st.write(f"- {rate}")

# ---------------------- RECORD LOGS PAGE ----------------------
def page_record_logs():
    st.header("Record Session Logs")

    # Basic checks
    if not st.session_state["participants"]:
        st.warning("No participants available. Please add some in Configuration.")
        return
    if not st.session_state["categories"]:
        st.warning("No categories available. Please add some in Configuration.")
        return
    if not st.session_state["rates"]:
        st.warning("No rates available. (They should be fixed in code.)")
        return

    with st.form(key="add_log_form", clear_on_submit=False):
        selected_participants = st.multiselect(
            "Select Participant(s)",
            st.session_state["participants"],
            help="Select one or more participants for a group event."
        )
        date_entry = st.date_input("Session Date", datetime.date.today())
        rate_choice = st.selectbox("Rate Type", st.session_state["rates"])
        category_choice = st.selectbox("Category", st.session_state["categories"])
        hours = st.number_input("Number of hours (decimal)", min_value=0.0, step=0.25, value=1.0)

        col1, col2 = st.columns(2)
        with col1:
            start_time_raw = st.text_input("Start time (24hr, e.g. 0900)", "0900")
        with col2:
            end_time_raw = st.text_input("End time (24hr, e.g. 1300)", "1300")

        break_mins = st.number_input("Break minutes", min_value=0, step=5, value=0)
        selected_locations = st.multiselect("Locations", st.session_state["locations"])

        submitted_add_log = st.form_submit_button("Add Log Entry")
        if submitted_add_log:
            if selected_participants:
                log_entry = {
                    "participants": selected_participants,  # multiple if group
                    "date": date_entry,
                    "start_time": start_time_raw,
                    "end_time": end_time_raw,
                    "break_mins": break_mins,
                    "rate": rate_choice,
                    "category": category_choice,
                    "hours": hours,
                    "locations": selected_locations,
                }
                st.session_state["session_logs"].append(log_entry)
                st.success(
                    f"Added log for {', '.join(selected_participants)} on {date_entry}"
                )
            else:
                st.warning("Please select at least one participant before adding the log.")

    # Show current logs
    if st.session_state["session_logs"]:
        st.write("Current Logs:")
        for i, log in enumerate(st.session_state["session_logs"]):
            part_list = ", ".join(log["participants"])
            st.write(
                f"{i+1}) Participants: {part_list} | {log['date']} | "
                f"{log['start_time']} - {log['end_time']} "
                f"({log['break_mins']} min break) | Rate: {log['rate']} | "
                f"Category: {log['category']} | Hours: {log['hours']} | "
                f"Locations: {log['locations']}"
            )

# ---------------------- GENERATE INVOICE PAGE ----------------------
def page_generate_invoice():
    st.header("Generate Weekly Invoice (Single Participant)")

    if not st.session_state["session_logs"]:
        st.warning("No logs recorded yet. Please add some in 'Record Session Logs'.")
        return

    # Gather all participants found in logs
    participants_in_logs = set()
    for log in st.session_state["session_logs"]:
        for p in log["participants"]:
            participants_in_logs.add(p)

    if not participants_in_logs:
        st.warning("No participants found in logs.")
        return

    # Choose participant, then a date range start
    participant = st.selectbox("Select Participant", sorted(list(participants_in_logs)))
    week_start = st.date_input("Week Start (typically Monday)", datetime.date.today())
    week_end = week_start + datetime.timedelta(days=6)
    st.write(f"Selected period: {week_start} to {week_end}")

    # Filter logs if participant is included and date is in [week_start, week_end]
    filtered_logs = []
    for log in st.session_state["session_logs"]:
        if participant in log["participants"] and (week_start <= log["date"] <= week_end):
            filtered_logs.append(log)

    if not filtered_logs:
        st.warning(f"No logs found for {participant} in that date range.")
        return

    final_lines = []
    for log in filtered_logs:
        formatted_date = log["date"].strftime("%a, %b %d, %Y")
        start_str = format_24hr_with_suffix(log["start_time"])
        end_str   = format_24hr_with_suffix(log["end_time"])
        break_str = f" ({log['break_mins']} Minutes Less)" if log['break_mins'] else ""
        period_str = f"{start_str}-{end_str}{break_str}"

        # Show all participants for group events
        all_parts = log["participants"]
        if len(all_parts) == 1:
            participants_str = all_parts[0]
        else:
            participants_str = "[" + ", ".join(all_parts) + "]"

        # Format locations
        locs = log["locations"]
        if len(locs) > 1:
            locs_str = "[" + ", ".join(locs) + "]"
        elif len(locs) == 1:
            locs_str = locs[0]
        else:
            locs_str = ""

        line_str = (
            f"{log['hours']} Hours [{log['rate']}, {log['category']}], "
            f"{formatted_date}, {period_str}, "
            f"{participants_str}, {locs_str}"
        )
        final_lines.append(line_str)

    st.subheader(f"Invoice Lines for {participant}")
    for i, line in enumerate(final_lines, start=1):
        st.write(f"{i}) {line}")

    joined_text = "\n".join(final_lines)
    if st.button("Copy All to Clipboard"):
        pyperclip.copy(joined_text)
        st.success("Copied lines to clipboard!")

# ---------------------- MAIN APP ----------------------
def main():
    st.set_page_config(page_title="NDIS Invoicing v2.2", layout="wide")
    init_session_state()

    # Sidebar nav
    pages = {
        "Configuration": page_configuration,
        "Record Logs": page_record_logs,
        "Generate Invoice": page_generate_invoice
    }
    choice = st.sidebar.selectbox("Go to", list(pages.keys()))
    pages[choice]()

if __name__ == "__main__":
    main()
