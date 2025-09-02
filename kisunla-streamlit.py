import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Kisunla Treatment Flowsheet",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2rem;
    font-weight: bold;
    color: #1f2937;
    margin-bottom: 1rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.metric-card {
    text-align: center;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 0.5rem;
    border: 1px solid #e5e7eb;
}

.risk-high {
    color: #dc2626;
    font-weight: bold;
}

.completed-badge {
    background: #dcfce7;
    color: #166534;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
}

.infusion-number {
    background: #dcfce7;
    color: #166534;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 0.875rem;
}

.dosing-schedule {
    background: #f1f5f9;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

.aria-warning {
    background: #fef3c7;
    border: 1px solid #f59e0b;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = {
            'infusions': [],
            'mri_tracking': [],
            'aria_assessments': [],
            'cms_registry': '',
            'apoe4_status': 'Not Tested',
            'overall_aria_risk': 'Not Assessed',
            'symptomatic_aria': 'Not Assessed',
            'serious_events': 'Not Assessed'
        }

# Kisunla-specific functions
def calculate_kisunla_dose(infusion_number):
    """Calculate Kisunla dose based on gradual titration schedule"""
    if infusion_number == 1:
        return 350
    elif infusion_number == 2:
        return 700
    elif infusion_number == 3:
        return 1050
    else:
        return 1400  # Maintenance dose

def calculate_volume(dose):
    """Calculate volume based on Kisunla concentration (350mg/20mL)"""
    return (dose / 350) * 20

# Main app
def main():
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">Kisunla Treatment Flowsheet</h1>', unsafe_allow_html=True)
    
    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "💉 Infusions", "🧠 MRI Tracking", "⚠️ ARIA Monitoring"])
    
    with tab1:
        render_summary()
    
    with tab2:
        render_infusions()
    
    with tab3:
        render_mri_tracking()
        
    with tab4:
        render_aria_monitoring()
    
    # Save button (floating)
    st.markdown("---")
    if st.button("💾 Save", type="primary"):
        st.success("Data saved successfully!")

def render_summary():
    """Render the summary tab"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Treatment Progress Card
        if st.session_state.patient_data['infusions']:
            current_infusion = st.session_state.patient_data['infusions'][0]['number']
            st.subheader("Treatment Progress")
            with st.container():
                st.markdown(f"## Infusion {current_infusion} of ~18-24*")
                st.caption("*Treatment duration varies based on amyloid reduction")
        else:
            st.subheader("Treatment Progress")
            with st.container():
                st.info("No infusions recorded yet. Add your first infusion to start tracking treatment progress.")
        
        # Dosing Schedule (always show)
        st.markdown("**Dosing Schedule**")
        dosing_data = {
            "Dose": ["Dose 1", "Dose 2", "Dose 3", "Maintenance"],
            "Amount": ["350 mg", "700 mg", "1050 mg", "1400 mg Q4W"]
        }
        st.table(pd.DataFrame(dosing_data))
        
        # CMS Registry Card
        st.subheader("CMS Registry")
        with st.container():
            if st.session_state.patient_data['cms_registry']:
                st.markdown(f"### {st.session_state.patient_data['cms_registry']}")
            else:
                st.info("CMS Registry number not entered")
            
            st.markdown("**ApoE ε4 Status**")
            if st.session_state.patient_data['apoe4_status'] != 'Not Tested':
                st.info(st.session_state.patient_data['apoe4_status'])
                if 'Homozygote' in st.session_state.patient_data['apoe4_status']:
                    st.error("**High Risk** - Two copies of ApoE ε4 allele")
                elif 'Heterozygote' in st.session_state.patient_data['apoe4_status']:
                    st.warning("**Moderate Risk** - One copy of ApoE ε4 allele")
                else:
                    st.success("**Lower Risk** - No ApoE ε4 alleles")
            else:
                st.warning("ApoE ε4 testing required before treatment initiation")
    
    with col2:
        # Latest MRI Status Card
        st.subheader("Latest MRI Status")
        
        if st.session_state.patient_data['mri_tracking']:
            latest_mri = st.session_state.patient_data['mri_tracking'][0]
            with st.container():
                st.write(f"**Date:** {latest_mri['date']}")
                st.write(f"**MRI Type:** {latest_mri['type']}")
                st.write(f"**Notes:** {latest_mri['notes'] or 'No notes'}")
        else:
            with st.container():
                st.info("No MRI records yet. Schedule baseline MRI before treatment initiation.")
        
        # ARIA Risk Assessment Card  
        st.subheader("⚠️ ARIA Risk Assessment")
        
        with st.container():
            if st.session_state.patient_data['overall_aria_risk'] != 'Not Assessed':
                st.markdown("**Overall ARIA Risk**")
                st.markdown(f"# {st.session_state.patient_data['overall_aria_risk']}")
                st.caption("Total ARIA incidence rate")
                
                st.markdown("---")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Symptomatic ARIA", st.session_state.patient_data['symptomatic_aria'])
                with col_b:
                    st.metric("Serious Events", st.session_state.patient_data['serious_events'])
            else:
                st.warning("ARIA risk assessment pending. Complete ApoE ε4 testing and baseline assessments.")

def render_infusions():
    """Render the infusions tab"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Infusion History")
    
    with col2:
        if st.button("➕ Add New Infusion", type="primary"):
            render_add_infusion_modal()
    
    # Display infusions or empty state
    if st.session_state.patient_data['infusions']:
        for infusion in st.session_state.patient_data['infusions']:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**#{infusion['number']} - Infusion {infusion['number']}**")
                    st.caption(f"Date: {infusion['date']}")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.write(f"**Dose:** {infusion['dose']} mg")
                    with col_b:
                        st.write(f"**Volume:** {infusion['volume']} mL") 
                    with col_c:
                        st.write(f"**Duration:** ~30 min")
                    
                    if infusion['notes']:
                        st.write(f"**Notes:** {infusion['notes']}")
                
                with col2:
                    st.success("✓ Completed")
                
                st.divider()
    else:
        st.info("📋 No infusions recorded yet. Click 'Add New Infusion' to begin treatment tracking.")
        st.markdown("**Treatment will follow Kisunla's gradual titration schedule:**")
        st.markdown("- **Infusion 1:** 350 mg")
        st.markdown("- **Infusion 2:** 700 mg") 
        st.markdown("- **Infusion 3:** 1050 mg")
        st.markdown("- **Maintenance:** 1400 mg every 4 weeks")

@st.dialog("Add New Infusion")
def render_add_infusion_modal():
    """Render the add infusion modal as a popup"""
    with st.form("add_infusion_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            infusion_number = st.number_input("Infusion Number", min_value=1, value=22)
            infusion_date = st.date_input("Infusion Date", value=date.today())
        
        with col2:
            # Calculate dose automatically
            calculated_dose = calculate_kisunla_dose(infusion_number)
            st.success(f"Calculated Dose: {calculated_dose} mg")
            
            notes = st.text_area("Notes", placeholder="infusion")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Infusion", type="primary"):
                # Add new infusion
                new_infusion = {
                    'id': max([inf['id'] for inf in st.session_state.patient_data['infusions']]) + 1,
                    'number': infusion_number,
                    'date': infusion_date.strftime('%Y-%m-%d'),
                    'dose': calculated_dose,
                    'volume': calculate_volume(calculated_dose),
                    'status': 'completed',
                    'notes': notes
                }
                
                st.session_state.patient_data['infusions'].insert(0, new_infusion)
                st.session_state.show_add_infusion = False
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_add_infusion = False
                st.rerun()

def render_mri_tracking():
    """Render the MRI tracking tab"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("MRI Tracking")
    
    with col2:
        if st.button("➕ Add MRI Tracking", type="primary"):
            st.session_state.show_add_mri = True
    
    # MRI Schedule Reminder
    st.warning("⚠️ **MRI Schedule Reminder:** Required: Baseline + before infusions 2, 3, 4, and 7. Enhanced vigilance during first 24 weeks.")
    
    # Display MRI records or empty state
    if st.session_state.patient_data['mri_tracking']:
        for mri in st.session_state.patient_data['mri_tracking']:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**Date:** {mri['date']}")
                    st.write(f"**MRI Type:** {mri['type']}")
                    st.write(f"**Radiologist Notes:** {mri['notes']}")
                
                with col2:
                    st.button("✏️", key=f"edit_mri_{mri['id']}")
                
                st.divider()
    else:
        st.info("🧠 No MRI records yet. Add baseline MRI before starting treatment.")
        st.markdown("**Required MRI Schedule:**")
        st.markdown("- **Baseline MRI** (before first infusion)")
        st.markdown("- **Pre-infusion 2** (before 2nd dose)")
        st.markdown("- **Pre-infusion 3** (before 3rd dose)") 
        st.markdown("- **Pre-infusion 4** (before 4th dose)")
        st.markdown("- **Pre-infusion 7** (before 7th dose)")
    
    # Add MRI modal
    if st.session_state.get('show_add_mri', False):
        render_add_mri_modal()

def render_add_mri_modal():
    """Render the add MRI modal"""
    with st.expander("New MRI Entry", expanded=True):
        with st.form("add_mri_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mri_date = st.date_input("MRI Date", value=date.today())
                mri_type = st.selectbox("MRI Type", ["Baseline", "Follow-update", "Safety"])
            
            with col2:
                notes = st.text_area("Radiologist Notes", placeholder="mri")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Save MRI Record", type="primary"):
                    # Add new MRI record
                    new_mri = {
                        'id': max([mri['id'] for mri in st.session_state.patient_data['mri_tracking']]) + 1,
                        'date': mri_date.strftime('%Y-%m-%d'),
                        'type': mri_type,
                        'notes': notes
                    }
                    
                    st.session_state.patient_data['mri_tracking'].insert(0, new_mri)
                    st.session_state.show_add_mri = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_mri = False
                    st.rerun()

def render_aria_monitoring():
    """Render the ARIA monitoring tab"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("ARIA Monitoring")
    
    with col2:
        if st.button("➕ Add New ARIA Monitoring", type="primary"):
            st.session_state.show_add_aria = True
    
    # Display ARIA assessments or empty state
    if st.session_state.patient_data['aria_assessments']:
        for assessment in st.session_state.patient_data['aria_assessments']:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**Assessment Date:** {assessment['date']}")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write("**ARIA-E Assessment**")
                        st.write(f"FLAIR Hyperintensity Severity: {assessment['aria_e']['flair_severity']}")
                        st.write(f"Overall Clinical Severity: {assessment['aria_e']['clinical_severity']}")
                    
                    with col_b:
                        st.write("**ARIA-H Assessment**") 
                        st.write(f"Microhemorrhages: {assessment['aria_h']['microhemorrhages']}")
                        st.write(f"Siderosis: {assessment['aria_h']['siderosis']}")
                    
                    # Display symptoms if present
                    if assessment['symptoms']:
                        st.write("**Symptoms Present:**")
                        # Create columns for symptoms display
                        symptom_cols = st.columns(len(assessment['symptoms']))
                        for idx, symptom in enumerate(assessment['symptoms']):
                            with symptom_cols[idx]:
                                st.error(symptom)
                
                with col2:
                    st.button("✏️", key=f"edit_aria_{assessment['id']}")
                
                st.divider()
    else:
        st.info("⚠️ No ARIA assessments recorded yet. Add baseline assessment after first MRI.")
        st.markdown("**ARIA Monitoring Guidelines:**")
        st.markdown("- **ARIA-E:** Monitor for brain edema or sulcal effusions")
        st.markdown("- **ARIA-H:** Track microhemorrhages and superficial siderosis") 
        st.markdown("- **Symptoms:** Watch for headache, confusion, visual changes, dizziness")
        st.markdown("- **Frequency:** Assess with each scheduled MRI")
    
    # Add ARIA modal
    if st.session_state.get('show_add_aria', False):
        render_add_aria_modal()

def render_add_aria_modal():
    """Render the add ARIA assessment modal"""
    with st.expander("ARIA Assessment", expanded=True):
        with st.form("add_aria_form"):
            st.date_input("MRI Date", value=date.today(), key="aria_date")
            
            st.markdown("#### ARIA-E Assessment")
            col1, col2 = st.columns(2)
            with col1:
                flair_severity = st.selectbox("FLAIR Hyperintensity Severity", ["None", "Mild", "Moderate", "Severe"])
            with col2:
                clinical_severity = st.selectbox("Overall Clinical Severity", ["Asymptomatic", "Mild", "Moderate", "Severe"])
            
            st.markdown("#### ARIA-H Assessment")
            col1, col2 = st.columns(2)
            with col1:
                microhemorrhages = st.selectbox("Microhemorrhages", ["None", "Mild (≤4)", "Moderate (5-9)", "Severe (≥10)"])
            with col2:
                siderosis = st.selectbox("Superficial Siderosis", ["None", "Mild (1 area)", "Moderate (2 areas)", "Severe (>2 areas)"])
            
            st.markdown("#### Symptoms")
            col1, col2 = st.columns(2)
            
            symptoms = []
            with col1:
                if st.checkbox("Weakness"):
                    symptoms.append("Weakness")
                if st.checkbox("Dizziness"):
                    symptoms.append("Dizziness")
                if st.checkbox("Visual Changes"):
                    symptoms.append("Visual Changes")
            
            with col2:
                if st.checkbox("Nausea"):
                    symptoms.append("Nausea")
                if st.checkbox("Confusion"):
                    symptoms.append("Confusion")
                if st.checkbox("Headache"):
                    symptoms.append("Headache")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.form_submit_button("Save Assessment", type="primary"):
                    # Add new ARIA assessment
                    new_assessment = {
                        'id': max([aria['id'] for aria in st.session_state.patient_data['aria_assessments']]) + 1,
                        'date': st.session_state.aria_date.strftime('%Y-%m-%d'),
                        'aria_e': {
                            'flair_severity': flair_severity,
                            'clinical_severity': clinical_severity
                        },
                        'aria_h': {
                            'microhemorrhages': microhemorrhages,
                            'siderosis': siderosis
                        },
                        'symptoms': symptoms
                    }
                    
                    st.session_state.patient_data['aria_assessments'].insert(0, new_assessment)
                    st.session_state.show_add_aria = False
                    st.rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_aria = False
                    st.rerun()

if __name__ == "__main__":
    main()
