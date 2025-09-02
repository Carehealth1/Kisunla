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
            'infusions': [
                {'id': 21, 'number': 21, 'date': '2025-08-27', 'dose': 1400, 'volume': 40.0, 'status': 'completed', 'notes': 'Maintenance dose - patient tolerated well'},
                {'id': 20, 'number': 20, 'date': '2025-08-13', 'dose': 1400, 'volume': 40.0, 'status': 'completed', 'notes': ''},
                {'id': 19, 'number': 19, 'date': '2025-07-28', 'dose': 1400, 'volume': 40.0, 'status': 'completed', 'notes': ''},
                {'id': 18, 'number': 18, 'date': '2025-05-12', 'dose': 1400, 'volume': 40.0, 'status': 'completed', 'notes': ''},
                {'id': 17, 'number': 17, 'date': '2025-05-05', 'dose': 1050, 'volume': 30.0, 'status': 'completed', 'notes': 'Third dose - titration phase'}
            ],
            'mri_tracking': [
                {'id': 5, 'date': '2025-08-27', 'type': 'Baseline', 'notes': 'Stable - no new ARIA findings'},
                {'id': 4, 'date': '2025-08-13', 'type': 'Baseline', 'notes': 'N/A'},
                {'id': 3, 'date': '2025-07-30', 'type': 'Baseline', 'notes': 'Mild FLAIR changes noted'},
                {'id': 2, 'date': '2025-07-15', 'type': 'Baseline', 'notes': 'Baseline study'},
                {'id': 1, 'date': '2025-06-05', 'type': 'Baseline', 'notes': 'Pre-treatment baseline'}
            ],
            'aria_assessments': [
                {
                    'id': 4, 'date': '2025-08-27',
                    'aria_e': {'flair_severity': 'None', 'clinical_severity': 'Asymptomatic'},
                    'aria_h': {'microhemorrhages': 'None', 'siderosis': 'None'},
                    'symptoms': []
                },
                {
                    'id': 3, 'date': '2025-08-13',
                    'aria_e': {'flair_severity': 'None', 'clinical_severity': 'Asymptomatic'},
                    'aria_h': {'microhemorrhages': 'None', 'siderosis': 'None'},
                    'symptoms': []
                },
                {
                    'id': 2, 'date': '2025-07-30',
                    'aria_e': {'flair_severity': 'Mild', 'clinical_severity': 'Asymptomatic'},
                    'aria_h': {'microhemorrhages': 'Mild (2-4)', 'siderosis': 'None'},
                    'symptoms': []
                }
            ],
            'cms_registry': '123445',
            'apoe4_status': 'Homozygote (e4/e4)',
            'overall_aria_risk': '45%',
            'symptomatic_aria': '9%',
            'serious_events': '3%'
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
        st.markdown("### Treatment Progress")
        current_infusion = st.session_state.patient_data['infusions'][0]['number']
        
        st.markdown(f"""
        <div class="card">
            <div style="font-size: 2rem; font-weight: bold; color: #2563eb; margin-bottom: 0.5rem;">
                Infusion {current_infusion} of ~18-24*
            </div>
            <div style="font-size: 0.875rem; color: #6b7280;">
                *Treatment duration varies based on amyloid reduction
            </div>
            
            <div class="dosing-schedule">
                <h4 style="margin-bottom: 0.5rem;">Dosing Schedule</h4>
                <div style="font-size: 0.875rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span>Dose 1:</span> <span style="font-weight: bold;">350 mg</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span>Dose 2:</span> <span style="font-weight: bold;">700 mg</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                        <span>Dose 3:</span> <span style="font-weight: bold;">1050 mg</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Maintenance:</span> <span style="font-weight: bold;">1400 mg Q4W</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### CMS Registry")
        st.markdown(f"""
        <div class="card">
            <div style="text-align: center; font-size: 1.5rem; font-weight: bold; padding: 1rem; background: #f8fafc; border-radius: 0.5rem; margin-bottom: 1rem;">
                {st.session_state.patient_data['cms_registry']}
            </div>
            
            <h4 style="margin-bottom: 0.5rem;">ApoE ε4 Status</h4>
            <div style="padding: 0.5rem; background: #f8fafc; border-radius: 0.5rem; margin-bottom: 0.5rem;">
                {st.session_state.patient_data['apoe4_status']}
            </div>
            <div class="risk-high">High Risk</div>
            <div style="font-size: 0.875rem; color: #dc2626;">Two copies of ApoE ε4 allele</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Latest MRI Status")
        latest_mri = st.session_state.patient_data['mri_tracking'][0]
        
        st.markdown(f"""
        <div class="card">
            <div style="margin-bottom: 0.5rem;"><span style="font-weight: bold;">Date:</span> {latest_mri['date']}</div>
            <div style="margin-bottom: 0.5rem;">
                <span style="font-weight: bold;">MRI Type:</span>
                <span style="background: #fce7f3; color: #be185d; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.75rem; margin-left: 0.5rem;">
                    {latest_mri['type']}
                </span>
            </div>
            <div><span style="font-weight: bold;">Notes:</span> {latest_mri['notes'] or 'No notes'}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ARIA Risk Assessment")
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span style="color: #ef4444; margin-right: 0.5rem;">⚠️</span>
                <span style="font-size: 1.125rem; font-weight: bold;">ARIA Risk Assessment</span>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Overall ARIA Risk</div>
                <div style="font-size: 3rem; font-weight: bold; color: #111827;">{st.session_state.patient_data['overall_aria_risk']}</div>
                <div style="font-size: 0.875rem; color: #6b7280;">Total ARIA incidence rate</div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;">
                <div>
                    <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Symptomatic ARIA</div>
                    <div style="font-size: 1.25rem; font-weight: bold;">{st.session_state.patient_data['symptomatic_aria']}</div>
                </div>
                <div>
                    <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.25rem;">Serious Events</div>
                    <div style="font-size: 1.25rem; font-weight: bold;">{st.session_state.patient_data['serious_events']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_infusions():
    """Render the infusions tab"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### Infusion History")
    
    with col2:
        if st.button("➕ Add New Infusion", type="primary"):
            st.session_state.show_add_infusion = True
    
    # Display infusions
    for infusion in st.session_state.patient_data['infusions']:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div style="display: flex; align-items: center;">
                    <div class="infusion-number">#{infusion['number']}</div>
                    <div style="margin-left: 0.75rem;">
                        <div style="font-weight: bold;">Infusion {infusion['number']}</div>
                        <div style="font-size: 0.875rem; color: #6b7280;">{infusion['date']}</div>
                    </div>
                </div>
                <div style="display: flex; align-items: center;">
                    <span class="completed-badge">✓ Completed</span>
                    <span style="margin-left: 0.5rem; color: #9ca3af; cursor: pointer;">✏️</span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; font-size: 0.875rem;">
                <div>
                    <span style="color: #6b7280;">Dose:</span>
                    <span style="margin-left: 0.25rem; font-weight: bold;">{infusion['dose']} mg</span>
                </div>
                <div>
                    <span style="color: #6b7280;">Volume:</span>
                    <span style="margin-left: 0.25rem; font-weight: bold;">{infusion['volume']} mL</span>
                </div>
                <div>
                    <span style="color: #6b7280;">Duration:</span>
                    <span style="margin-left: 0.25rem; font-weight: bold;">~30 min</span>
                </div>
            </div>
            
            {f'<div style="margin-top: 0.5rem; font-size: 0.875rem;"><span style="color: #6b7280;">Notes:</span> <span style="margin-left: 0.25rem;">{infusion["notes"]}</span></div>' if infusion['notes'] else ''}
        </div>
        """, unsafe_allow_html=True)
    
    # Add infusion modal
    if st.session_state.get('show_add_infusion', False):
        render_add_infusion_modal()

def render_add_infusion_modal():
    """Render the add infusion modal"""
    with st.expander("New Infusion Entry", expanded=True):
        with st.form("add_infusion_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                infusion_number = st.number_input("Infusion Number", min_value=1, value=22)
                infusion_date = st.date_input("Infusion Date", value=date.today())
            
            with col2:
                # Calculate dose automatically
                calculated_dose = calculate_kisunla_dose(infusion_number)
                st.info(f"Calculated Dose: {calculated_dose} mg")
                
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
        st.markdown("### MRI Tracking")
    
    with col2:
        if st.button("➕ Add MRI Tracking", type="primary"):
            st.session_state.show_add_mri = True
    
    # MRI Schedule Reminder
    st.markdown("""
    <div class="aria-warning">
        <div style="display: flex; align-items: center;">
            <span style="color: #f59e0b; margin-right: 0.5rem;">⚠️</span>
            <div>
                <div style="font-weight: bold; color: #92400e;">MRI Schedule Reminder</div>
                <div style="font-size: 0.875rem; color: #92400e;">
                    Required: Baseline + before infusions 2, 3, 4, and 7. Enhanced vigilance during first 24 weeks.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display MRI records
    for mri in st.session_state.patient_data['mri_tracking']:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <div>
                    <div style="font-weight: bold;">Date: {mri['date']}</div>
                    <div style="display: flex; align-items: center; margin-top: 0.25rem;">
                        <span style="font-size: 0.875rem; color: #6b7280; margin-right: 0.5rem;">MRI Type:</span>
                        <span style="background: #fce7f3; color: #be185d; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.75rem;">
                            {mri['type']}
                        </span>
                    </div>
                </div>
                <span style="color: #9ca3af; cursor: pointer;">✏️</span>
            </div>
            
            <div style="font-size: 0.875rem;">
                <span style="color: #6b7280;">Radiologist Notes:</span>
                <span style="margin-left: 0.25rem;">{mri['notes']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
        st.markdown("### ARIA Monitoring")
    
    with col2:
        if st.button("➕ Add New ARIA Monitoring", type="primary"):
            st.session_state.show_add_aria = True
    
    # Display ARIA assessments
    for assessment in st.session_state.patient_data['aria_assessments']:
        st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="font-weight: bold;">{assessment['date']}</div>
                <span style="color: #9ca3af; cursor: pointer;">✏️</span>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <h4 style="font-weight: bold; margin-bottom: 0.5rem;">ARIA-E Assessment</h4>
                    <div style="font-size: 0.875rem;">
                        <div style="margin-bottom: 0.25rem;">
                            <span style="color: #6b7280;">FLAIR Hyperintensity Severity:</span> {assessment['aria_e']['flair_severity']}
                        </div>
                        <div>
                            <span style="color: #6b7280;">Overall Clinical Severity:</span> {assessment['aria_e']['clinical_severity']}
                        </div>
                    </div>
                </div>
                
                <div>
                    <h4 style="font-weight: bold; margin-bottom: 0.5rem;">ARIA-H Assessment</h4>
                    <div style="font-size: 0.875rem;">
                        <div style="margin-bottom: 0.25rem;">
                            <span style="color: #6b7280;">Microhemorrhages:</span> {assessment['aria_h']['microhemorrhages']}
                        </div>
                        <div>
                            <span style="color: #6b7280;">Siderosis:</span> {assessment['aria_h']['siderosis']}
                        </div>
                    </div>
                </div>
            </div>
            
            {f'<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;"><h4 style="font-weight: bold; margin-bottom: 0.5rem;">Symptoms Present</h4><div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">{"".join([f\'<span style="background: #fecaca; color: #991b1b; padding: 0.25rem 0.5rem; border-radius: 9999px; font-size: 0.75rem;">{symptom}</span>\' for symptom in assessment["symptoms"]])}</div></div>' if assessment['symptoms'] else ''}
        </div>
        """, unsafe_allow_html=True)
    
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