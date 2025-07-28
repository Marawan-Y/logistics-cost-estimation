# pages/Settings.py
import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import shutil

st.set_page_config(page_title="Settings", page_icon="⚙️")

def main():
    st.title("⚙️ Application Settings")
    st.markdown("Configure data persistence and application behavior")
    st.markdown("---")
    
    # Initialize data manager
    if 'data_manager' not in st.session_state:
        from utils.data_manager import DataManager
        st.session_state.data_manager = DataManager()
    
    data_manager = st.session_state.data_manager
    
    # Get current save status
    save_status = data_manager.get_save_status()
    
    # Data Persistence Settings
    st.subheader("💾 Data Persistence Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Auto-save toggle
        current_auto_save = st.session_state.get('auto_save', True)
        auto_save = st.checkbox(
            "Enable Auto-save",
            value=current_auto_save,
            help="Automatically save data after each change"
        )
        
        if auto_save != current_auto_save:
            st.session_state.auto_save = auto_save
            data_manager.auto_save = auto_save
            if auto_save:
                st.success("✅ Auto-save enabled")
            else:
                st.warning("⚠️ Auto-save disabled - remember to save manually!")
    
    with col2:
        # Manual save button
        if st.button("💾 Save Data Now", type="primary"):
            if data_manager.manual_save():
                st.success("✅ Data saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save data!")
    
    st.markdown("---")
    
    # File Status Information
    st.subheader("📊 Data File Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if save_status['file_exists']:
            st.success("📄 **Data File Status**")
            st.write("✅ File exists")
            
            # File size
            file_size_kb = save_status['file_size'] / 1024
            if file_size_kb < 1024:
                st.write(f"📏 Size: {file_size_kb:.1f} KB")
            else:
                file_size_mb = file_size_kb / 1024
                st.write(f"📏 Size: {file_size_mb:.1f} MB")
            
            # Last modified
            if save_status['last_save_time']:
                last_save = save_status['last_save_time']
                st.write(f"🕒 Last saved: {last_save.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.warning("📄 **Data File Status**")
            st.write("❌ No data file found")
            st.write("📝 Data exists only in current session")
    
    with col2:
        backup_count = save_status['backup_count']
        st.info("🗂️ **Backup Status**")
        st.write(f"📦 Backups available: {backup_count}")
        
        if backup_count > 0:
            st.write("🔒 Automatic backups created")
            st.write("📅 Last 10 versions kept")
        else:
            st.write("📝 No backups yet")
    
    with col3:
        st.info("🔄 **Auto-save Status**")
        if save_status['auto_save_enabled']:
            st.write("✅ Auto-save: ON")
            st.write("💾 Changes saved automatically")
        else:
            st.write("⏸️ Auto-save: OFF")
            st.write("⚠️ Manual save required")
    
    st.markdown("---")
    
    # Data Management Actions
    st.subheader("🛠️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Export & Import")
        
        # Export current configuration
        if st.button("📤 Export Current Configuration", use_container_width=True):
            config_data = data_manager.export_configuration()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.download_button(
                label="📥 Download Configuration File",
                data=config_data,
                file_name=f"logistics_config_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Import configuration
        st.markdown("**Import Configuration**")
        uploaded_file = st.file_uploader(
            "Choose configuration file",
            type=['json'],
            help="Upload a previously exported configuration file"
        )
        
        if uploaded_file is not None:
            try:
                # Preview the file content
                with st.expander("🔍 Preview Import Data"):
                    file_content = uploaded_file.read()
                    uploaded_file.seek(0)  # Reset file pointer
                    
                    preview_data = json.loads(file_content.decode('utf-8'))
                    
                    # Show summary
                    st.write("**Import Summary:**")
                    if 'materials' in preview_data:
                        st.write(f"• Materials: {len(preview_data['materials'])}")
                    if 'suppliers' in preview_data:
                        st.write(f"• Suppliers: {len(preview_data['suppliers'])}")
                    if 'metadata' in preview_data:
                        metadata = preview_data['metadata']
                        if 'save_timestamp' in metadata:
                            st.write(f"• Export date: {metadata['save_timestamp']}")
                
                # Confirm import
                if st.button("📥 Import Configuration", type="primary"):
                    if data_manager.import_configuration(uploaded_file.read()):
                        st.success("✅ Configuration imported successfully!")
                        st.info("🔄 Refreshing page...")
                        st.rerun()
                    else:
                        st.error("❌ Failed to import configuration")
                        
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    with col2:
        st.markdown("#### Data Cleanup")
        
        # Clear all data
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            if st.session_state.get('confirm_clear_settings', False):
                if data_manager.clear_all_data():
                    st.success("✅ All data cleared successfully!")
                    st.session_state.confirm_clear_settings = False
                    st.rerun()
                else:
                    st.error("❌ Failed to clear data!")
            else:
                st.session_state.confirm_clear_settings = True
                st.warning("⚠️ Click again to confirm clearing ALL data")
        
        # Reset to defaults
        if st.button("🔄 Reset Settings to Default", use_container_width=True):
            st.session_state.auto_save = True
            data_manager.auto_save = True
            st.success("✅ Settings reset to default")
            st.rerun()
    
    st.markdown("---")
    
    # Backup Management
    st.subheader("🗂️ Backup Management")
    
    backup_dir = Path("backups")
    backup_count = save_status['backup_count']
    
    if backup_dir.exists() and backup_count > 0:
        backup_files = list(backup_dir.glob("logistics_data_backup_*.json"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if backup_files:
            st.write(f"**Available Backups ({len(backup_files)} files):**")
            
            # Show backup files in a table
            backup_data = []
            for backup_file in backup_files[:10]:  # Show last 10
                stat = backup_file.stat()
                backup_data.append({
                    "Filename": backup_file.name,
                    "Date": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    "Size (KB)": f"{stat.st_size / 1024:.1f}",
                })
            
            if backup_data:
                import pandas as pd
                df_backups = pd.DataFrame(backup_data)
                st.dataframe(df_backups, use_container_width=True, height=200)
                
                # Restore from backup
                st.markdown("**Restore from Backup:**")
                selected_backup = st.selectbox(
                    "Select backup to restore",
                    options=[f["Filename"] for f in backup_data],
                    help="Choose a backup file to restore your data"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Restore from Selected Backup", type="primary"):
                        try:
                            backup_path = backup_dir / selected_backup
                            with open(backup_path, 'r', encoding='utf-8') as f:
                                backup_content = f.read()
                            
                            if data_manager.import_configuration(backup_content.encode('utf-8')):
                                st.success(f"✅ Data restored from {selected_backup}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to restore backup")
                        except Exception as e:
                            st.error(f"❌ Error restoring backup: {str(e)}")
                
                with col2:
                    if st.button("🗑️ Delete All Backups"):
                        if st.session_state.get('confirm_delete_backups', False):
                            try:
                                for backup_file in backup_files:
                                    backup_file.unlink()
                                st.success("✅ All backups deleted")
                                st.session_state.confirm_delete_backups = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting backups: {str(e)}")
                        else:
                            st.session_state.confirm_delete_backups = True
                            st.warning("⚠️ Click again to confirm deleting ALL backups")
    else:
        st.info("📝 No backup files found")
    
    st.markdown("---")
    
    # Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("#### File Locations")
        st.code(f"Data file: {Path('logistics_data.json').absolute()}")
        st.code(f"Backup directory: {Path('backups').absolute()}")
        
        st.markdown("#### Technical Information")
        statistics = data_manager.get_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Configuration Counts:**")
            st.write(f"• Materials: {statistics['total_materials']}")
            st.write(f"• Suppliers: {statistics['total_suppliers']}")
            st.write(f"• Locations: {statistics['total_locations']}")
            st.write(f"• Operations: {statistics['total_operations']}")
            st.write(f"• Packaging: {statistics['total_packaging']}")
            st.write(f"• Transport: {statistics['total_transport']}")
        
        with col2:
            st.write("**System Status:**")
            st.write(f"• Calculation Ready: {'✅' if statistics['calculation_ready'] else '❌'}")
            
            # Calculate total configurations
            total_configs = sum([
                statistics['total_materials'],
                statistics['total_suppliers'],
                statistics['total_locations'],
                statistics['total_operations'],
                statistics['total_packaging'],
                statistics['total_repacking'],
                statistics['total_customs'],
                statistics['total_transport'],
                statistics['total_co2'],
                statistics['total_warehouse'],
                statistics['total_interest'],
                statistics['total_additional_costs']
            ])
            st.write(f"• Total Configurations: {total_configs}")
            
            # Material-supplier pairs
            pairs = len(data_manager.get_material_supplier_pairs())
            st.write(f"• Material-Supplier Pairs: {pairs}")
        
        st.markdown("#### Session Information")
        st.write(f"• Data loaded from file: {'✅' if st.session_state.get('data_loaded', False) else '❌'}")
        st.write(f"• Current session auto-save: {'✅' if st.session_state.get('auto_save', True) else '❌'}")
        
        if 'last_save_time' in st.session_state and st.session_state.last_save_time:
            st.write(f"• Last save in session: {st.session_state.last_save_time.strftime('%H:%M:%S')}")
    
    st.markdown("---")
    
    # Data Integrity Check
    st.subheader("🔍 Data Integrity Check")
    
    if st.button("🔎 Run Data Integrity Check"):
        with st.spinner("Checking data integrity..."):
            issues = []
            warnings = []
            
            # Check for materials without suppliers
            materials = data_manager.get_materials()
            suppliers = data_manager.get_suppliers()
            
            if not materials and not suppliers:
                issues.append("No materials or suppliers configured")
            elif not materials:
                issues.append("No materials configured")
            elif not suppliers:
                issues.append("No suppliers configured")
            
            # Check for required configurations
            required_configs = {
                'Packaging': data_manager.get_packaging(),
                'Transport': data_manager.get_transport(),
                'Warehouse': data_manager.get_warehouse(),
                'CO₂': data_manager.get_co2()
            }
            
            for config_name, config_list in required_configs.items():
                if not config_list:
                    issues.append(f"No {config_name.lower()} configurations found")
            
            # Check for optional configurations
            optional_configs = {
                'Operations': data_manager.get_operations(),
                'Locations': data_manager.get_locations(),
                'Customs': data_manager.get_customs(),
                'Interest': data_manager.get_interest()
            }
            
            for config_name, config_list in optional_configs.items():
                if not config_list:
                    warnings.append(f"No {config_name.lower()} configurations (optional)")
            
            # Check for data consistency
            for material in materials:
                if not material.get('material_no'):
                    issues.append("Material found without material number")
                if not material.get('annual_volume') or material.get('annual_volume') <= 0:
                    issues.append(f"Material {material.get('material_no', 'Unknown')} has invalid annual volume")
                if not material.get('weight_per_pcs') or material.get('weight_per_pcs') <= 0:
                    issues.append(f"Material {material.get('material_no', 'Unknown')} has invalid weight per piece")
            
            for supplier in suppliers:
                if not supplier.get('vendor_id'):
                    issues.append("Supplier found without vendor ID")
            
            # Display results
            col1, col2 = st.columns(2)
            
            with col1:
                if issues:
                    st.error(f"❌ **Issues Found ({len(issues)}):**")
                    for issue in issues:
                        st.write(f"• {issue}")
                else:
                    st.success("✅ **No Critical Issues Found**")
            
            with col2:
                if warnings:
                    st.warning(f"⚠️ **Warnings ({len(warnings)}):**")
                    for warning in warnings:
                        st.write(f"• {warning}")
                else:
                    st.info("ℹ️ **No Warnings**")
    
    st.markdown("---")
    
    # Help Section
    with st.expander("ℹ️ Help & Information"):
        st.markdown("""
        ### 💾 Data Persistence Features
        
        **Auto-save:**
        - Automatically saves your data after each change
        - Can be disabled if you prefer manual control
        - Recommended to keep enabled for data safety
        
        **Manual Save:**
        - Force save data at any time using "Save Now" button
        - Useful when auto-save is disabled
        - Creates immediate backup before saving
        
        **Backups:**
        - Automatic backups created before each save
        - Last 10 versions kept automatically
        - Can restore from any backup version
        - Backups stored in `/backups` directory
        
        **File Storage:**
        - Data stored in `logistics_data.json` file
        - Human-readable JSON format
        - Includes metadata and timestamps
        - Survives browser sessions and computer restarts
        
        ### 🔧 Settings Guide
        
        **Export/Import:**
        - Export creates downloadable configuration file
        - Import loads previously saved configuration
        - Use for sharing configurations between users
        - Use for migrating data between systems
        
        **Data Cleanup:**
        - Clear all data removes everything permanently
        - Reset settings restores default preferences
        - Use backup restore to recover deleted data
        
        **Integrity Check:**
        - Scans for missing required configurations
        - Identifies data inconsistencies
        - Provides recommendations for fixes
        - Run regularly to ensure data quality
        
        ### ⚠️ Important Notes
        
        - **Data Location**: All data is stored locally on your computer
        - **Sharing**: Use export/import to share configurations
        - **Backup Strategy**: Keep regular exports as additional backups
        - **Browser Data**: Clearing browser data does NOT affect saved files
        - **File Access**: You can directly edit the JSON file if needed
        """)
    
    # Footer
    st.markdown("---")
    st.caption("Settings - Logistics Cost Automation Software v1.0")

if __name__ == "__main__":
    main()