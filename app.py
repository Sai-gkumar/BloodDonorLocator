import sys
import io
import os

# Force absolute terminal console encoding standards
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sqlite3
import math
import leafmap.foliumap as leafmap
import setuptools

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_session_management'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Core Algorithm: Proximity Distance Processing (Haversine Formula) ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def determine_badge(count):
    if count >= 10: return {"name": "👑 Life Saver Elite", "class": "badge-gold"}
    elif count >= 5: return {"name": "🛡️ Blood Champion", "class": "badge-silver"}
    elif count >= 1: return {"name": "🩸 First Responder", "class": "badge-bronze"}
    return {"name": "🌱 New Donor", "class": "badge-new"}


# --- USER DASHBOARD PANEL ---
@app.route('/dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        blood_group = request.form['blood_group']
        is_available = 1 if request.form.get('is_available') else 0
        password = request.form['password']
        
        if password.strip():
            conn.execute('''
                UPDATE users SET name=?, phone=?, blood_group=?, is_available=?, password=? WHERE id=?
            ''', (name, phone, blood_group, is_available, password, user_id))
        else:
            conn.execute('''
                UPDATE users SET name=?, phone=?, blood_group=?, is_available=? WHERE id=?
            ''', (name, phone, blood_group, is_available, user_id))
            
        conn.commit()
        session['name'] = name
        return redirect(url_for('user_dashboard', success="Profile updated successfully!"))

    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('dashboard.html', user=user)


# --- UPDATED ADMIN PANEL WITH NOTIFICATION TRIGGER & ACTIONS ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied: Administrative privileges required.", 403
        
    conn = get_db_connection()
    
    action = request.args.get('action')
    target_id = request.args.get('id')
    
    if action == 'toggle_status' and target_id:
        conn.execute('UPDATE users SET is_available = NOT is_available WHERE id = ?', (target_id,))
        conn.commit()
    elif action == 'delete' and target_id:
        conn.execute('DELETE FROM users WHERE id = ?', (target_id,))
        conn.commit()
        
    if request.method == 'POST' and request.form.get('broadcast_msg'):
        msg = request.form.get('broadcast_msg')
        print(f"ALERT BROADCAST: {msg}") 
        return redirect(url_for('admin_dashboard', broadcast_status="Broadcast alert dispatched successfully!"))

    donors = conn.execute("SELECT * FROM users WHERE role = 'donor'").fetchall()
    conn.close()
    return render_template('admin.html', donors=donors)


@app.route('/', methods=['GET', 'POST'])
def index():
    # 1. Pull core geographic coordinates from URL query parameters
    user_lat = request.args.get('lat', default=17.6896, type=float)
    user_lng = request.args.get('lng', default=83.2185, type=float)
    
    # 2. Extract filtering state criteria interchangeably from POST or GET fallback channels
    if request.method == 'POST':
        selected_blood = request.form.get('blood_group', 'All')
        try:
            radius = float(request.form.get('radius', 1000.0))
        except (ValueError, TypeError):
            radius = 1000.0
    else:
        # Pull parameters from the URL when the slider or dropdown reloads the page
        selected_blood = request.args.get('blood_group', 'All')
        try:
            radius = float(request.args.get('radius', 1000.0))
        except (ValueError, TypeError):
            radius = 1000.0

    # Enforce range limits
    radius = min(radius, 1000.0)

    # 3. Query the data storage layer
    conn = get_db_connection()
    query = "SELECT id, name, blood_group, phone, latitude, longitude, donation_count FROM users WHERE role = 'donor' AND is_available = 1"
    params = []
    
    if selected_blood != 'All':
        query += " AND blood_group = ?"
        params.append(selected_blood)
        
    donors = conn.execute(query, params).fetchall()
    conn.close()

    nearby_donors = []
    map_locations = [[user_lat, user_lng]]

    for donor in donors:
        if donor['latitude'] is not None and donor['longitude'] is not None:
            dist = calculate_distance(user_lat, user_lng, donor['latitude'], donor['longitude'])
            if dist <= radius:
                donor_dict = dict(donor)
                donor_dict['distance'] = round(dist, 2)
                donor_dict['badge'] = determine_badge(donor['donation_count'])
                nearby_donors.append(donor_dict)
                map_locations.append([donor['latitude'], donor['longitude']])
                
    nearby_donors.sort(key=lambda x: x['distance'])

    # 4. Generate Interactive Leafmap Map Engine Canvas Canvas
    m = leafmap.Map(center=[user_lat, user_lng], zoom=6, draw_control=False, measure_control=False)
    m.add_marker(location=[user_lat, user_lng], popup="Search Center Target Location", icon_color="blue")

    for donor in nearby_donors:
        d_id = donor['id']
        d_name = donor['name']
        d_bg = donor['blood_group']
        d_dist = donor['distance']
        d_lat = donor['latitude']
        d_lng = donor['longitude']
        d_badge = donor['badge']['name']

        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 170px; line-height: 1.4;">
            <h4 style="margin:0 0 3px 0; color:#ff3e3e;">{d_name} ({d_bg})</h4>
            <span style="display:inline-block; font-size:10px; padding:2px 5px; background:#f2f2f2; border-radius:3px; margin-bottom:5px; font-weight:bold;">
                {d_badge}
            </span><br>
            <b>Distance:</b> {d_dist} km<br>
            <a href="/donor/{d_id}" target="_blank" style="display:inline-block; margin-top:6px; background:#222; color:white; text-decoration:none; padding:5px; border-radius:4px; font-size:11px; text-align:center; width:90%; font-weight:bold;">
                👤 View Full Profile
            </a>
            <button onclick="window.parent.drawRoute({user_lat}, {user_lng}, {d_lat}, {d_lng})" 
                    style="margin-top:5px; background:#ff3e3e; color:white; border:none; padding:5px; border-radius:4px; cursor:pointer; font-size:11px; width:100%; font-weight:bold;">
                🗺️ Plot Drive Route
            </button>
        </div>
        """
        m.add_marker(location=[d_lat, d_lng], popup=popup_html, icon_color="red")

    if len(map_locations) > 1:
        m.fit_bounds(map_locations)

    static_map_dir = os.path.join(app.static_folder, 'generated_maps')
    os.makedirs(static_map_dir, exist_ok=True)
    map_filepath = os.path.join(static_map_dir, 'live_map.html')
    m.to_html(map_filepath)

    return render_template(
        'index.html',
        donors=nearby_donors,
        selected_blood=selected_blood,
        radius=int(radius),
        user_lat=user_lat,
        user_lng=user_lng
    )


@app.route('/donor/<int:donor_id>')
def view_donor_profile(donor_id):
    conn = get_db_connection()
    donor = conn.execute('SELECT * FROM users WHERE id = ? AND role = "donor"', (donor_id,)).fetchone()
    conn.close()
    if not donor:
        return "Requested donor profile was not found.", 404
    badge = determine_badge(donor['donation_count'])
    return render_template('donor_profile.html', donor=donor, badge=badge)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        blood_group = request.form['blood_group']
        phone = request.form['phone']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        if not latitude or not longitude:
            return "Registration Error: Location data missing."

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO users (name, email, password, role, blood_group, phone, latitude, longitude)
                VALUES (?, ?, ?, 'donor', ?, ?, ?, ?)
            ''', (name, email, password, blood_group, phone, latitude, longitude))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Validation Error: This email is already registered."
        finally:
            conn.close()
            
    return render_template('register_donor.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            return redirect(url_for('index'))
        else:
            return "Invalid login combinations."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
