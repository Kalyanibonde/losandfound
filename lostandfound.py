import streamlit as st
import datetime
import uuid
import io
from PIL import Image
import base64

# Set page configuration
st.set_page_config(
    page_title="Lost & Found System",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'lost_items' not in st.session_state:
    st.session_state.lost_items = []

if 'found_items' not in st.session_state:
    st.session_state.found_items = []

if 'claims' not in st.session_state:
    st.session_state.claims = []

# Function to convert image to base64 for storage
def image_to_base64(image_file):
    if image_file is None:
        return ""
    file_bytes = image_file.getvalue()
    encoded = base64.b64encode(file_bytes).decode()
    return encoded

# Function to display base64 image
def display_image(base64_string, width=300):
    if base64_string == "" or base64_string is None:
        return None
    
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        st.error(f"Error displaying image: {e}")
        return None

# Create a custom CSS for the app
st.markdown("""
<style>
    .main-header {
        font-size: 42px;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 26px;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        margin-bottom: 5px;
    }
    .card {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .success-msg {
        color: #28a745;
        font-weight: bold;
    }
    .info-msg {
        color: #17a2b8;
        font-weight: bold;
    }
    .warning-msg {
        color: #ffc107;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='main-header'>📱 Lost & Found System</div>", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", 
    ["Home", "Report Lost Item", "Report Found Item", "Search Items", 
     "Claim Item", "Admin Dashboard"]
)

# Filter options for the sidebar
st.sidebar.markdown("<div class='sub-header'>Filters</div>", unsafe_allow_html=True)
item_types = ["All Types", "Electronics", "Clothing", "Documents", "Keys", "Bags", "Jewelry", "Other"]
filter_type = st.sidebar.selectbox("Item Type", item_types)
filter_status = st.sidebar.selectbox("Status", ["All Statuses", "Open", "Claimed", "Returned", "Closed"])

# Date filters
st.sidebar.write("Date Range:")
start_date = st.sidebar.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.datetime.now())

# Apply filters function
def apply_filters(items, item_type_col='item_type', status_col='status', date_col='date_reported'):
    filtered_items = []
    
    for item in items:
        # Convert string dates to datetime objects for comparison
        item_date = datetime.datetime.strptime(item[date_col], "%Y-%m-%d").date()
        
        # Check if item meets all filter criteria
        type_match = filter_type == "All Types" or item[item_type_col] == filter_type
        status_match = filter_status == "All Statuses" or item[status_col] == filter_status
        date_match = start_date <= item_date <= end_date
        
        if type_match and status_match and date_match:
            filtered_items.append(item)
    
    return filtered_items

# Home Page
if page == "Home":
    st.markdown("<div class='sub-header'>Welcome to the Lost & Found System</div>", unsafe_allow_html=True)
    
    # Dashboard statistics in a row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Lost Items</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{len(st.session_state.lost_items)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Found Items</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{len(st.session_state.found_items)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Returned Items</div>", unsafe_allow_html=True)
        returned_items = sum(1 for item in st.session_state.lost_items if item['status'] == 'Returned')
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{returned_items}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Success Rate</div>", unsafe_allow_html=True)
        if len(st.session_state.lost_items) > 0:
            success_rate = (returned_items / len(st.session_state.lost_items)) * 100
            st.markdown(f"<div style='font-size: 24px; text-align: center;'>{success_rate:.1f}%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 24px; text-align: center;'>0%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent lost and found items
    st.markdown("<div class='sub-header'>Recent Lost Items</div>", unsafe_allow_html=True)
    if st.session_state.lost_items:
        # Sort items by date (most recent first)
        recent_lost = sorted(st.session_state.lost_items, 
                            key=lambda x: datetime.datetime.strptime(x['date_reported'], "%Y-%m-%d"), 
                            reverse=True)[:5]
        
        for item in recent_lost:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<b>{item['item_name']}</b> ({item['item_type']}) - {item['status']}", unsafe_allow_html=True)
            st.markdown(f"<i>Lost on {item['date_lost']} at {item['location']}</i>", unsafe_allow_html=True)
            st.markdown(f"<small>Description: {item['description']}</small>", unsafe_allow_html=True)
            
            # Display image if available
            if item['image'] and item['image'] != "":
                img = display_image(item['image'])
                if img:
                    st.image(img, width=200)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No lost items reported yet.")

    st.markdown("<div class='sub-header'>Recent Found Items</div>", unsafe_allow_html=True)
    if st.session_state.found_items:
        # Sort items by date (most recent first)
        recent_found = sorted(st.session_state.found_items, 
                             key=lambda x: datetime.datetime.strptime(x['date_reported'], "%Y-%m-%d"), 
                             reverse=True)[:5]
        
        for item in recent_found:
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            st.markdown(f"<b>{item['item_name']}</b> ({item['item_type']}) - {item['status']}", unsafe_allow_html=True)
            st.markdown(f"<i>Found on {item['date_found']} at {item['location']}</i>", unsafe_allow_html=True)
            st.markdown(f"<small>Description: {item['description']}</small>", unsafe_allow_html=True)
            
            # Display image if available
            if item['image'] and item['image'] != "":
                img = display_image(item['image'])
                if img:
                    st.image(img, width=200)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No found items reported yet.")

# Report Lost Item Page
elif page == "Report Lost Item":
    st.markdown("<div class='sub-header'>Report a Lost Item</div>", unsafe_allow_html=True)
    
    with st.form("lost_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_type = st.selectbox("Item Type*", item_types[1:])
            item_name = st.text_input("Item Name*")
            description = st.text_area("Description*")
            location = st.text_input("Last Seen Location*")
        
        with col2:
            date_lost = st.date_input("Date Lost*", datetime.datetime.now())
            reporter_name = st.text_input("Your Name*")
            contact_info = st.text_input("Contact Information (Phone/Email)*")
            image_file = st.file_uploader("Upload Image (if available)", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("Submit Report")
        
        if submit_button:
            # Validate required fields
            if not (item_name and description and location and reporter_name and contact_info):
                st.error("Please fill all required fields marked with *")
            else:
                # Convert image to base64 if available
                image_base64 = image_to_base64(image_file) if image_file else ""
                
                # Create new lost item entry
                new_item = {
                    'id': str(uuid.uuid4()),
                    'item_type': item_type,
                    'item_name': item_name,
                    'description': description,
                    'location': location,
                    'date_lost': date_lost.strftime("%Y-%m-%d"),
                    'reporter_name': reporter_name,
                    'contact_info': contact_info,
                    'status': 'Open',
                    'date_reported': datetime.datetime.now().strftime("%Y-%m-%d"),
                    'image': image_base64
                }
                
                # Add to session state
                st.session_state.lost_items.append(new_item)
                
                st.success("Your lost item has been reported successfully!")
                st.info(f"Your reference ID is: {new_item['id']}")

# Report Found Item Page
elif page == "Report Found Item":
    st.markdown("<div class='sub-header'>Report a Found Item</div>", unsafe_allow_html=True)
    
    with st.form("found_item_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_type = st.selectbox("Item Type*", item_types[1:])
            item_name = st.text_input("Item Name*")
            description = st.text_area("Description*")
            location = st.text_input("Found Location*")
        
        with col2:
            date_found = st.date_input("Date Found*", datetime.datetime.now())
            founder_name = st.text_input("Your Name*")
            contact_info = st.text_input("Contact Information (Phone/Email)*")
            image_file = st.file_uploader("Upload Image (if available)", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("Submit Report")
        
        if submit_button:
            # Validate required fields
            if not (item_name and description and location and founder_name and contact_info):
                st.error("Please fill all required fields marked with *")
            else:
                # Convert image to base64 if available
                image_base64 = image_to_base64(image_file) if image_file else ""
                
                # Create new found item entry
                new_item = {
                    'id': str(uuid.uuid4()),
                    'item_type': item_type,
                    'item_name': item_name,
                    'description': description,
                    'location': location,
                    'date_found': date_found.strftime("%Y-%m-%d"),
                    'founder_name': founder_name,
                    'contact_info': contact_info,
                    'status': 'Open',
                    'date_reported': datetime.datetime.now().strftime("%Y-%m-%d"),
                    'image': image_base64
                }
                
                # Add to session state
                st.session_state.found_items.append(new_item)
                
                st.success("Your found item has been reported successfully!")
                st.info(f"Your reference ID is: {new_item['id']}")

# Search Items Page
elif page == "Search Items":
    st.markdown("<div class='sub-header'>Search Lost & Found Items</div>", unsafe_allow_html=True)
    
    # Search options
    search_type = st.radio("Search For:", ["Lost Items", "Found Items", "Both"])
    
    # Search parameters
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_term = st.text_input("Search by keyword (name, description, location)")
        
    with search_col2:
        search_item_type = st.selectbox("Filter by Type", item_types)
    
    # Search function
    def search_items(items, term, item_type):
        results = []
        term = term.lower()
        
        for item in items:
            # Check if search term exists in name, description or location
            name_match = term in item.get('item_name', '').lower()
            desc_match = term in item.get('description', '').lower()
            loc_match = term in item.get('location', '').lower()
            
            # Check if item type matches
            type_match = item_type == "All Types" or item.get('item_type') == item_type
            
            if (name_match or desc_match or loc_match) and type_match:
                results.append(item)
        
        return results
    
    # Perform search when button is clicked
    if st.button("Search"):
        lost_results = []
        found_results = []
        
        if search_type in ["Lost Items", "Both"]:
            lost_results = search_items(st.session_state.lost_items, search_term, search_item_type)
            
        if search_type in ["Found Items", "Both"]:
            found_results = search_items(st.session_state.found_items, search_term, search_item_type)
        
        # Display results
        if search_type in ["Lost Items", "Both"]:
            st.markdown("<div class='section-header'>Lost Items Results</div>", unsafe_allow_html=True)
            if lost_results:
                for item in lost_results:
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<b>{item['item_name']}</b> ({item['item_type']}) - {item['status']}", unsafe_allow_html=True)
                    st.markdown(f"<i>Lost on {item['date_lost']} at {item['location']}</i>", unsafe_allow_html=True)
                    st.markdown(f"Description: {item['description']}", unsafe_allow_html=True)
                    
                    # Display image if available
                    if item['image'] and item['image'] != "":
                        img = display_image(item['image'])
                        if img:
                            st.image(img, width=200)
                    
                    if item['status'] == 'Open':
                        if st.button(f"I found this item! (ID: {item['id']})", key=f"found_{item['id']}"):
                            st.session_state.temp_claim_id = item['id']
                            st.session_state.temp_claim_type = 'lost'
                            st.experimental_rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No matching lost items found.")
        
        if search_type in ["Found Items", "Both"]:
            st.markdown("<div class='section-header'>Found Items Results</div>", unsafe_allow_html=True)
            if found_results:
                for item in found_results:
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<b>{item['item_name']}</b> ({item['item_type']}) - {item['status']}", unsafe_allow_html=True)
                    st.markdown(f"<i>Found on {item['date_found']} at {item['location']}</i>", unsafe_allow_html=True)
                    st.markdown(f"Description: {item['description']}", unsafe_allow_html=True)
                    
                    # Display image if available
                    if item['image'] and item['image'] != "":
                        img = display_image(item['image'])
                        if img:
                            st.image(img, width=200)
                    
                    if item['status'] == 'Open':
                        if st.button(f"This is mine! (ID: {item['id']})", key=f"mine_{item['id']}"):
                            st.session_state.temp_claim_id = item['id']
                            st.session_state.temp_claim_type = 'found'
                            st.experimental_rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No matching found items found.")

# Claim Item Page
elif page == "Claim Item":
    st.markdown("<div class='sub-header'>Claim an Item</div>", unsafe_allow_html=True)
    
    # Check if we're coming from the search page with a pre-selected item
    claim_id = ""
    claim_type = ""
    
    if 'temp_claim_id' in st.session_state and 'temp_claim_type' in st.session_state:
        claim_id = st.session_state.temp_claim_id
        claim_type = st.session_state.temp_claim_type
        # Clear temporary session state
        del st.session_state.temp_claim_id
        del st.session_state.temp_claim_type
    
    # Form for claiming an item
    with st.form("claim_form"):
        if not claim_id:
            claim_type = st.radio("Type of Item to Claim", ["Lost", "Found"])
            claim_id = st.text_input("Item Reference ID*")
        else:
            st.info(f"Claiming {'Lost' if claim_type == 'lost' else 'Found'} item with ID: {claim_id}")
            claim_type = "Lost" if claim_type == 'lost' else "Found"
        
        claimer_name = st.text_input("Your Name*")
        contact_info = st.text_input("Contact Information (Phone/Email)*")
        proof_description = st.text_area("Provide details to prove ownership/finding of the item*")
        
        submit_claim = st.form_submit_button("Submit Claim")
        
        if submit_claim:
            # Validate required fields
            if not (claim_id and claimer_name and contact_info and proof_description):
                st.error("Please fill all required fields marked with *")
            else:
                found = False
                
                # Check if item exists
                if claim_type == "Lost":
                    for item in st.session_state.found_items:
                        if item['id'] == claim_id and item['status'] == 'Open':
                            found = True
                            
                            # Create claim
                            new_claim = {
                                'id': str(uuid.uuid4()),
                                'item_id': claim_id,
                                'item_type': 'Found',
                                'claimer_name': claimer_name,
                                'contact_info': contact_info,
                                'description': proof_description,
                                'date_claimed': datetime.datetime.now().strftime("%Y-%m-%d"),
                                'status': 'Pending'
                            }
                            
                            # Update item status
                            item['status'] = 'Claimed'
                            
                            # Add claim to session state
                            st.session_state.claims.append(new_claim)
                            
                            st.success("Your claim has been submitted successfully!")
                            st.info(f"Your claim reference ID is: {new_claim['id']}")
                            break
                else:
                    for item in st.session_state.lost_items:
                        if item['id'] == claim_id and item['status'] == 'Open':
                            found = True
                            
                            # Create claim
                            new_claim = {
                                'id': str(uuid.uuid4()),
                                'item_id': claim_id,
                                'item_type': 'Lost',
                                'claimer_name': claimer_name,
                                'contact_info': contact_info,
                                'description': proof_description,
                                'date_claimed': datetime.datetime.now().strftime("%Y-%m-%d"),
                                'status': 'Pending'
                            }
                            
                            # Update item status
                            item['status'] = 'Claimed'
                            
                            # Add claim to session state
                            st.session_state.claims.append(new_claim)
                            
                            st.success("Your claim has been submitted successfully!")
                            st.info(f"Your claim reference ID is: {new_claim['id']}")
                            break
                
                if not found:
                    st.error("Item not found or is no longer available for claiming.")

# Admin Dashboard
elif page == "Admin Dashboard":
    st.markdown("<div class='sub-header'>Admin Dashboard</div>", unsafe_allow_html=True)
    
    # Simple password protection
    password = st.text_input("Enter Admin Password", type="password")
    
    if password == "admin123":  # Simple password for demo purposes
        admin_tab1, admin_tab2, admin_tab3 = st.tabs(["Lost Items", "Found Items", "Claims"])
        
        with admin_tab1:
            st.markdown("<div class='section-header'>Manage Lost Items</div>", unsafe_allow_html=True)
            
            # Apply filters
            filtered_lost = apply_filters(st.session_state.lost_items)
            
            if filtered_lost:
                for i, item in enumerate(filtered_lost):
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<b>ID:</b> {item['id']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Item:</b> {item['item_name']} ({item['item_type']})", unsafe_allow_html=True)
                    st.markdown(f"<b>Status:</b> {item['status']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Reporter:</b> {item['reporter_name']} - {item['contact_info']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Details:</b> Lost on {item['date_lost']} at {item['location']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Description:</b> {item['description']}", unsafe_allow_html=True)
                    
                    # Display image if available
                    if item['image'] and item['image'] != "":
                        img = display_image(item['image'])
                        if img:
                            st.image(img, width=200)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Mark as Returned", key=f"return_lost_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.lost_items):
                                if original_item['id'] == item['id']:
                                    st.session_state.lost_items[idx]['status'] = 'Returned'
                                    st.success(f"Item {item['id']} marked as Returned")
                                    break
                    
                    with col2:
                        if st.button("Mark as Closed", key=f"close_lost_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.lost_items):
                                if original_item['id'] == item['id']:
                                    st.session_state.lost_items[idx]['status'] = 'Closed'
                                    st.success(f"Item {item['id']} marked as Closed")
                                    break
                    
                    with col3:
                        if st.button("Delete", key=f"delete_lost_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.lost_items):
                                if original_item['id'] == item['id']:
                                    del st.session_state.lost_items[idx]
                                    st.success(f"Item {item['id']} deleted")
                                    break
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No lost items match the current filters.")
        
        with admin_tab2:
            st.markdown("<div class='section-header'>Manage Found Items</div>", unsafe_allow_html=True)
            
            # Apply filters
            filtered_found = apply_filters(st.session_state.found_items)
            
            if filtered_found:
                for i, item in enumerate(filtered_found):
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<b>ID:</b> {item['id']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Item:</b> {item['item_name']} ({item['item_type']})", unsafe_allow_html=True)
                    st.markdown(f"<b>Status:</b> {item['status']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Founder:</b> {item['founder_name']} - {item['contact_info']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Details:</b> Found on {item['date_found']} at {item['location']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Description:</b> {item['description']}", unsafe_allow_html=True)
                    
                    # Display image if available
                    if item['image'] and item['image'] != "":
                        img = display_image(item['image'])
                        if img:
                            st.image(img, width=200)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Mark as Returned", key=f"return_found_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.found_items):
                                if original_item['id'] == item['id']:
                                    st.session_state.found_items[idx]['status'] = 'Returned'
                                    st.success(f"Item {item['id']} marked as Returned")
                                    break
                    
                    with col2:
                        if st.button("Mark as Closed", key=f"close_found_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.found_items):
                                if original_item['id'] == item['id']:
                                    st.session_state.found_items[idx]['status'] = 'Closed'
                                    st.success(f"Item {item['id']} marked as Closed")
                                    break
                    
                    with col3:
                        if st.button("Delete", key=f"delete_found_{i}"):
                            # Find the item in the original list
                            for idx, original_item in enumerate(st.session_state.found_items):
                                if original_item['id'] == item['id']:
                                    del st.session_state.found_items[idx]
                                    st.success(f"Item {item['id']} deleted")
                                    break
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No found items match the current filters.")
        
        with admin_tab3:
            st.markdown("<div class='section-header'>Manage Claims</div>", unsafe_allow_html=True)
            
            if st.session_state.claims:
                for i, claim in enumerate(st.session_state.claims):
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<b>Claim ID:</b> {claim['id']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Item ID:</b> {claim['item_id']} ({claim['item_type']} Item)", unsafe_allow_html=True)
                    st.markdown(f"<b>Status:</b> {claim['status']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Claimer:</b> {claim['claimer_name']} - {claim['contact_info']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Date Claimed:</b> {claim['date_claimed']}", unsafe_allow_html=True)
                    st.markdown(f"<b>Proof/Description:</b> {claim['description']}", unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("Approve Claim", key=f"approve_{i}"):
                            # Find the claim in the original list
                            for idx, original_claim in enumerate(st.session_state.claims):
                                if original_claim['id'] == claim['id']:
                                    st.session_state.claims[idx]['status'] = 'Approved'
                                    
                                    # Update the item status
                                    if claim['item_type'] == 'Lost':
                                        for ldx, lost_item in enumerate(st.session_state.lost_items):
                                            if lost_item['id'] == claim['item_id']:
                                                st.session_state.lost_items[ldx]['status'] = 'Returned'
                                                break
                                    else:
                                        for fdx, found_item in enumerate(st.session_state.found_items):
                                            if found_item['id'] == claim['item_id']:
                                                st.session_state.found_items[fdx]['status'] = 'Returned'
                                                break
                                    
                                    st.success(f"Claim {claim['id']} approved")
                                    break
                    
                    with col2:
                        if st.button("Reject Claim", key=f"reject_{i}"):
                            # Find the claim in the original list
                            for idx, original_claim in enumerate(st.session_state.claims):
                                if original_claim['id'] == claim['id']:
                                    st.session_state.claims[idx]['status'] = 'Rejected'
                                    
                                    # Update the item status back to Open
                                    if claim['item_type'] == 'Lost':
                                        for ldx, lost_item in enumerate(st.session_state.lost_items):
                                            if lost_item['id'] == claim['item_id']:
                                                st.session_state.lost_items[ldx]['status'] = 'Open'
                                                break
                                    else:
                                        for fdx, found_item in enumerate(st.session_state.found_items):
                                            if found_item['id'] == claim['item_id']:
                                                st.session_state.found_items[fdx]['status'] = 'Open'
                                                break
                                    
                                    st.success(f"Claim {claim['id']} rejected")
                                    break
                    
                    with col3:
                        if st.button("Delete Claim", key=f"delete_claim_{i}"):
                            # Find the claim in the original list
                            for idx, original_claim in enumerate(st.session_state.claims):
                                if original_claim['id'] == claim['id']:
                                    del st.session_state.claims[idx]
                                    st.success(f"Claim {claim['id']} deleted")
                                    break
                    
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No claims have been made yet.")
    else:
        st.warning("Please enter the correct admin password to access the dashboard.")

# Add a statistics and reports page
elif page == "Statistics and Reports":
    st.markdown("<div class='sub-header'>Statistics and Reports</div>", unsafe_allow_html=True)
    
    # Date range for the reports
    st.sidebar.write("Report Period:")
    report_start_date = st.sidebar.date_input("Start Date", datetime.datetime.now() - datetime.timedelta(days=90))
    report_end_date = st.sidebar.date_input("End Date", datetime.datetime.now())
    
    # Generate statistics
    total_lost = len(st.session_state.lost_items)
    total_found = len(st.session_state.found_items)
    returned_items = sum(1 for item in st.session_state.lost_items if item['status'] == 'Returned')
    
    # Filter items within the date range
    filtered_lost = []
    filtered_found = []
    for item in st.session_state.lost_items:
        item_date = datetime.datetime.strptime(item['date_reported'], "%Y-%m-%d").date()
        if report_start_date <= item_date <= report_end_date:
            filtered_lost.append(item)
    
    for item in st.session_state.found_items:
        item_date = datetime.datetime.strptime(item['date_reported'], "%Y-%m-%d").date()
        if report_start_date <= item_date <= report_end_date:
            filtered_found.append(item)
    
    # Count items by type
    lost_by_type = {}
    found_by_type = {}
    
    for item in filtered_lost:
        if item['item_type'] in lost_by_type:
            lost_by_type[item['item_type']] += 1
        else:
            lost_by_type[item['item_type']] = 1
    
    for item in filtered_found:
        if item['item_type'] in found_by_type:
            found_by_type[item['item_type']] += 1
        else:
            found_by_type[item['item_type']] = 1
    
    # Count items by status
    lost_by_status = {}
    found_by_status = {}
    
    for item in filtered_lost:
        if item['status'] in lost_by_status:
            lost_by_status[item['status']] += 1
        else:
            lost_by_status[item['status']] = 1
    
    for item in filtered_found:
        if item['status'] in found_by_status:
            found_by_status[item['status']] += 1
        else:
            found_by_status[item['status']] = 1
    
    # Display statistics
    st.markdown("<div class='section-header'>Summary Statistics</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Lost Items</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{len(filtered_lost)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Found Items</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{len(filtered_found)}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Returned Items</div>", unsafe_allow_html=True)
        returned_in_period = sum(1 for item in filtered_lost if item['status'] == 'Returned')
        st.markdown(f"<div style='font-size: 24px; text-align: center;'>{returned_in_period}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Recovery Rate</div>", unsafe_allow_html=True)
        if len(filtered_lost) > 0:
            recovery_rate = (returned_in_period / len(filtered_lost)) * 100
            st.markdown(f"<div style='font-size: 24px; text-align: center;'>{recovery_rate:.1f}%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='font-size: 24px; text-align: center;'>0%</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Draw charts - Create data for visualization
    st.markdown("<div class='section-header'>Item Categories</div>", unsafe_allow_html=True)
    
    # Display simple bar charts
    lost_type_data = [[category, count] for category, count in lost_by_type.items()]
    found_type_data = [[category, count] for category, count in found_by_type.items()]
    
    # Use columns for side-by-side charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Lost Items by Type</div>", unsafe_allow_html=True)
        
        # Create simple HTML/CSS bar chart
        for category, count in sorted(lost_by_type.items(), key=lambda x: x[1], reverse=True):
            # Calculate percentage of total
            percentage = (count / len(filtered_lost)) * 100 if filtered_lost else 0
            
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 100px; font-weight: bold;">{category}</div>
                    <div style="flex-grow: 1; margin: 0 10px;">
                        <div style="background-color: #f0f2f6; border-radius: 4px; height: 24px; width: 100%;">
                            <div style="background-color: #1E88E5; border-radius: 4px; height: 24px; width: {percentage}%"></div>
                        </div>
                    </div>
                    <div style="width: 50px; text-align: right;">{count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Found Items by Type</div>", unsafe_allow_html=True)
        
        # Create simple HTML/CSS bar chart
        for category, count in sorted(found_by_type.items(), key=lambda x: x[1], reverse=True):
            # Calculate percentage of total
            percentage = (count / len(filtered_found)) * 100 if filtered_found else 0
            
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 100px; font-weight: bold;">{category}</div>
                    <div style="flex-grow: 1; margin: 0 10px;">
                        <div style="background-color: #f0f2f6; border-radius: 4px; height: 24px; width: 100%;">
                            <div style="background-color: #4CAF50; border-radius: 4px; height: 24px; width: {percentage}%"></div>
                        </div>
                    </div>
                    <div style="width: 50px; text-align: right;">{count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add status charts
    st.markdown("<div class='section-header'>Item Status</div>", unsafe_allow_html=True)
    
    status_col1, status_col2 = st.columns(2)
    
    with status_col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Lost Items by Status</div>", unsafe_allow_html=True)
        
        # Create simple HTML/CSS bar chart
        for status, count in sorted(lost_by_status.items(), key=lambda x: x[1], reverse=True):
            # Calculate percentage of total
            percentage = (count / len(filtered_lost)) * 100 if filtered_lost else 0
            
            # Choose color based on status
            if status == 'Returned':
                color = '#4CAF50'  # Green
            elif status == 'Open':
                color = '#FFC107'  # Yellow
            elif status == 'Claimed':
                color = '#2196F3'  # Blue
            else:
                color = '#9E9E9E'  # Grey
            
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 100px; font-weight: bold;">{status}</div>
                    <div style="flex-grow: 1; margin: 0 10px;">
                        <div style="background-color: #f0f2f6; border-radius: 4px; height: 24px; width: 100%;">
                            <div style="background-color: {color}; border-radius: 4px; height: 24px; width: {percentage}%"></div>
                        </div>
                    </div>
                    <div style="width: 50px; text-align: right;">{count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with status_col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>Found Items by Status</div>", unsafe_allow_html=True)
        
        # Create simple HTML/CSS bar chart
        for status, count in sorted(found_by_status.items(), key=lambda x: x[1], reverse=True):
            # Calculate percentage of total
            percentage = (count / len(filtered_found)) * 100 if filtered_found else 0
            
            # Choose color based on status
            if status == 'Returned':
                color = '#4CAF50'  # Green
            elif status == 'Open':
                color = '#FFC107'  # Yellow
            elif status == 'Claimed':
                color = '#2196F3'  # Blue
            else:
                color = '#9E9E9E'  # Grey
            
            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 100px; font-weight: bold;">{status}</div>
                    <div style="flex-grow: 1; margin: 0 10px;">
                        <div style="background-color: #f0f2f6; border-radius: 4px; height: 24px; width: 100%;">
                            <div style="background-color: {color}; border-radius: 4px; height: 24px; width: {percentage}%"></div>
                        </div>
                    </div>
                    <div style="width: 50px; text-align: right;">{count}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Export options
    st.markdown("<div class='section-header'>Export Reports</div>", unsafe_allow_html=True)
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("Export Lost Items Report"):
            # Create a simple CSV string
            csv_data = "ID,Item Name,Type,Status,Date Lost,Date Reported,Location\n"
            
            for item in filtered_lost:
                csv_data += f"{item['id']},{item['item_name']},{item['item_type']},{item['status']},{item['date_lost']},{item['date_reported']},{item['location']}\n"
            
            # Create a download link
            b64 = base64.b64encode(csv_data.encode()).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="lost_items_report.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    with export_col2:
        if st.button("Export Found Items Report"):
            # Create a simple CSV string
            csv_data = "ID,Item Name,Type,Status,Date Found,Date Reported,Location\n"
            
            for item in filtered_found:
                csv_data += f"{item['id']},{item['item_name']},{item['item_type']},{item['status']},{item['date_found']},{item['date_reported']},{item['location']}\n"
            
            # Create a download link
            b64 = base64.b64encode(csv_data.encode()).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="found_items_report.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

# Add the Statistics page to the navigation
if page == "Home":
    # Add a button to access statistics on the home page
    if st.button("View Statistics and Reports"):
        # Update the page selection and rerun
        st.session_state.page = "Statistics and Reports"
        st.experimental_rerun()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 30px; padding: 10px; font-size: 12px; color: #666;">
    &copy; 2025 Lost & Found System | Version 1.0
</div>
""", unsafe_allow_html=True)