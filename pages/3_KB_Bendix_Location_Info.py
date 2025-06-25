import streamlit as st
from utils.validators import LocationValidator
from utils.data_manager import DataManager

st.set_page_config(page_title="KB/Bendix Location Info", page_icon="📍")

def main():
    st.title("KB/Bendix Location Information")
    st.markdown("Configure plant location details")
    st.markdown("---")

    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = DataManager()
    data_manager = st.session_state.data_manager
    validator = LocationValidator()

    # ---------- Add New Location ----------
    with st.form("location_form"):
        st.subheader("Add New Location")
        col1, col2 = st.columns(2)
        with col1:
            plant = st.text_input("KB/Bendix Plant *")
            country = st.text_input("KB/Bendix – Country *")
        with col2:
            distance = st.number_input(
                "Distance (km) *",
                min_value=0.0, step=0.1,
                help="Distance from supplier to KB/Bendix plant"
            )
        submitted = st.form_submit_button("Add Location", type="primary")
        if submitted:
            loc = {"plant": plant, "country": country, "distance": distance}
            res = validator.validate_location(loc)
            if res["is_valid"]:
                if data_manager.location_exists(plant):
                    st.error(f"Plant {plant} already exists. Use edit instead.")
                else:
                    data_manager.add_location(loc)
                    st.success("Location added successfully!")
                    st.rerun()
            else:
                for e in res["errors"]:
                    st.error(e)

    st.markdown("---")

    # Helper callbacks for edit/cancel
    def enter_edit(idx):
        st.session_state[f"edit_loc_flag_{idx}"] = True

    def exit_edit(idx):
        st.session_state[f"edit_loc_flag_{idx}"] = False

    # ---------- Existing ----------
    st.subheader("Existing Locations")
    locations = data_manager.get_locations()
    if not locations:
        st.info("No locations configured yet.")
    for i, loc in enumerate(locations):
        # Ensure an edit flag exists for each index
        flag_key = f"edit_loc_flag_{i}"
        if flag_key not in st.session_state:
            st.session_state[flag_key] = False

        with st.expander(f"{loc['plant']} – {loc['country']}"):
            col1, col2, col3 = st.columns([3,1,1])
            with col1:
                st.write(f"**Distance:** {loc['distance']:.1f} km")
            with col2:
                # Use a different key for the button widget
                if st.button("Edit", key=f"edit_btn_{i}", on_click=enter_edit, args=(i,)):
                    pass  # the callback enter_edit will set the flag
            with col3:
                # Delete can be immediate
                if st.button("Delete", key=f"del_btn_{i}", type="secondary"):
                    data_manager.remove_location(loc["plant"])
                    st.success("Location deleted")
                    st.rerun()

    # ---------- Edit Forms ----------
    for i, loc in enumerate(locations):
        flag_key = f"edit_loc_flag_{i}"
        if st.session_state.get(flag_key, False):
            # Show edit form
            with st.form(f"edit_loc_form_{i}"):
                st.subheader(f"Edit Location: {loc['plant']}")
                col1, col2 = st.columns(2)
                with col1:
                    new_country = st.text_input(
                        "KB/Bendix – Country", value=loc["country"], key=f"country_input_{i}"
                    )
                with col2:
                    new_distance = st.number_input(
                        "Distance (km)",
                        value=loc["distance"], min_value=0.0, step=0.1,
                        key=f"distance_input_{i}"
                    )
                col1b, col2b = st.columns(2)
                with col1b:
                    if st.form_submit_button("Update", type="primary"):
                        upd = {
                            "plant": loc["plant"],
                            "country": new_country,
                            "distance": new_distance,
                        }
                        res = validator.validate_location(upd)
                        if res["is_valid"]:
                            data_manager.update_location(loc["plant"], upd)
                            st.success("Location updated")
                            exit_edit(i)
                            st.rerun()
                        else:
                            for e in res["errors"]:
                                st.error(e)
                with col2b:
                    if st.form_submit_button("Cancel"):
                        exit_edit(i)
                        st.rerun()


if __name__ == "__main__":
    main()
