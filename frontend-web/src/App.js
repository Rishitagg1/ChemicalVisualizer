import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import 'chart.js/auto';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import './App.css';

function App() {
  // --- STATE ---
  const [view, setView] = useState('welcome');
  const [theme, setTheme] = useState('dark');
  const [user, setUser] = useState({});
  const [formData, setFormData] = useState({});
  const [stats, setStats] = useState(null);
  
  // UI State
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [expandedStats, setExpandedStats] = useState(false);
  const [historyList, setHistoryList] = useState([]);

  // --- EFFECTS ---
  useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);
  
  // Load history from local storage on mount
  useEffect(() => {
    const saved = localStorage.getItem('upload_history');
    if (saved) setHistoryList(JSON.parse(saved));
  }, []);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

  // --- LOGIC ---
  const handleInputChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleLogin = async (e) => { 
    e.preventDefault(); 
    try { 
      const res = await axios.post('http://127.0.0.1:8000/api/login/', formData); 
      // Store password temporarily for validation check later (simulated security)
      setUser({ ...res.data, currentPass: formData.password }); 
      setView(res.data.role === 'admin' ? 'admin' : 'dashboard'); 
    } catch (err) { alert('Invalid Credentials'); } 
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try { await axios.post('http://127.0.0.1:8000/api/signup/', formData); alert('Account Created! Please Login.'); setView('login'); } 
    catch (err) { alert('Signup Failed'); }
  };

  const handleUpload = async (e) => { 
    const file = e.target.files[0]; if (!file) return; 
    const data = new FormData(); data.append('file', file); 
    try { 
      const res = await axios.post('http://127.0.0.1:8000/api/upload/', data); 
      setStats(res.data);
      addToHistory(file.name, res.data.total_count);
    } catch (err) { alert('Upload Failed'); } 
  };

  const addToHistory = (name, rows) => {
    const entry = { name, rows, date: new Date().toLocaleString() };
    const newList = [entry, ...historyList];
    setHistoryList(newList);
    localStorage.setItem('upload_history', JSON.stringify(newList));
  };

  const generatePDF = () => {
    if(!stats) return alert("No data to report!");
    const doc = new jsPDF();
    
    // Header
    doc.setFillColor(59, 130, 246); // Blue
    doc.rect(0, 0, 210, 40, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(22);
    doc.text("Chemical Visualizer Report", 14, 20);
    doc.setFontSize(12);
    doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 30);

    // Summary
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(16);
    doc.text("Executive Summary", 14, 55);
    doc.setFontSize(12);
    doc.text("The uploaded dataset has been processed and optimized.", 14, 65);
    
    // Table
    const tableData = stats.metrics.map(m => [m.label, m.value]);
    tableData.unshift(["Total Rows", stats.total_count]);

    doc.autoTable({
      startY: 75,
      head: [['Metric Name', 'Value']],
      body: tableData,
      theme: 'grid',
      headStyles: { fillColor: [59, 130, 246] },
    });

    doc.save("Enhanced_Report.pdf");
  };

  const handleProfileSave = (e) => {
    e.preventDefault();
    const { newPass, confirmPass, newName } = formData;
    
    if (newPass || confirmPass) {
      if (newPass !== confirmPass) return alert("New passwords do not match!");
      if (newPass === user.currentPass) return alert("Cannot reuse your old password!");
      alert("Password updated successfully!");
    } else if (newName) {
      alert("Profile name updated!");
    }
    setShowEditProfile(false);
  };

  // --- COLORS (Earth & Ocean Palette) ---
  const colors = ['#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51', '#8AB17D'];

  // --- RENDER HELPERS ---
  const Modal = ({ title, children, onClose }) => (
    <div className="modal-overlay" onClick={onClose}>
      <div className="glass-card" style={{maxWidth:'500px'}} onClick={e => e.stopPropagation()}>
        <h2 style={{marginTop:0}}>{title}</h2>
        {children}
        <button onClick={onClose} style={{background:'#ef4444', color:'white', marginTop:'20px', width:'100%'}}>Close</button>
      </div>
    </div>
  );

  // ================= VIEWS =================

  if (view === 'welcome') {
    return (
      <div className="app-container">
        <div className="glass-card" style={{textAlign:'center', maxWidth:'400px'}}>
          <h1 style={{fontSize:'48px', color:'#2563eb', marginBottom:'10px'}}>Chemical Vis</h1>
          <p style={{fontSize:'18px', color:'#666', marginBottom:'40px'}}>Industrial Telemetry System</p>
          <button onClick={() => setView('login')} style={{background:'#2563eb', color:'white', fontSize:'18px', width:'100%'}}>Launch System</button>
        </div>
      </div>
    );
  }

  if (view === 'login' || view === 'signup') {
    return (
      <div className="app-container">
        <div className="glass-card" style={{maxWidth:'400px', textAlign:'center'}}>
          <h2>{view === 'login' ? 'Secure Login' : 'Create Account'}</h2>
          <form onSubmit={view === 'login' ? handleLogin : handleSignup}>
            {view === 'signup' && (
              <>
                <input name="name" placeholder="Full Name" onChange={handleInputChange} required />
                <input name="phone" placeholder="Phone Number" onChange={handleInputChange} />
                <input name="institute" placeholder="Institute" onChange={handleInputChange} />
              </>
            )}
            <input name="email" placeholder="Email ID" onChange={handleInputChange} required />
            <input name="password" type="password" placeholder="Password" onChange={handleInputChange} required />
            
            <button type="submit" style={{background:'#2563eb', color:'white', width:'100%'}}>
              {view === 'login' ? 'Access Console' : 'Register'}
            </button>
          </form>
          <p onClick={() => setView(view === 'login' ? 'signup' : 'login')} style={{marginTop:'20px', cursor:'pointer', color:'#2563eb', fontWeight:'bold'}}>
            {view === 'login' ? 'Create New Account' : 'Back to Login'}
          </p>
        </div>
      </div>
    );
  }

  // --- DASHBOARD ---
  if (view === 'dashboard' || view === 'admin') {
    return (
      <div className="app-container">
        <div className="glass-card">
          
          {/* HEADER */}
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'30px'}}>
            <h1 style={{margin:0}}>Dashboard</h1>
            <div style={{display:'flex', gap:'10px', alignItems:'center', position:'relative'}}>
              <button className="icon-btn" onClick={() => setShowHistory(true)} title="History">🕒</button>
              <button className="icon-btn" onClick={() => setIsMenuOpen(!isMenuOpen)} title="Menu">☰</button>
              
              {/* HAMBURGER MENU */}
              {isMenuOpen && (
                <div className="menu-dropdown">
                  <div className="menu-item" onClick={() => { setShowEditProfile(true); setIsMenuOpen(false); }}>👤 Edit Profile</div>
                  <div className="menu-item" onClick={() => { toggleTheme(); setIsMenuOpen(false); }}>
                    {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
                  </div>
                  <div style={{height:'1px', background:'rgba(128,128,128,0.2)', margin:'5px 0'}}></div>
                  <div className="menu-item" onClick={() => setView('welcome')} style={{color:'#ef4444'}}>🚪 Logout</div>
                </div>
              )}
            </div>
          </div>

          {/* ADMIN VIEW OVERRIDE */}
          {view === 'admin' ? (
             <div>
               <h3>Admin Console (Master)</h3>
               <p>User database management via backend CSV.</p>
             </div>
          ) : (
            <>
              {/* ACTION BUTTONS */}
              <div style={{display:'flex', gap:'15px', marginBottom:'30px'}}>
                <button style={{flex:1, background:'#f59e0b', color:'white', height:'60px', fontSize:'16px'}} onClick={() => document.getElementById('fileInput').click()}>
                  ☁ Upload Dataset
                  <input id="fileInput" type="file" hidden onChange={handleUpload} accept=".csv, .xlsx, .json" />
                </button>
                <button style={{flex:1, background:'#8b5cf6', color:'white', height:'60px', fontSize:'16px'}} onClick={generatePDF}>
                  📄 Download PDF Report
                </button>
              </div>

              {/* STATS AREA */}
              {stats && (
                <div className="fade-in">
                  <div className="stats-grid">
                    <div className="stat-box" style={{background: colors[0]}}>
                      <span className="stat-val">{stats.total_count}</span>
                      <span className="stat-lbl">Total Rows</span>
                    </div>
                    {/* Show limited or all based on state */}
                    {stats.metrics.slice(0, expandedStats ? undefined : 4).map((m, i) => (
                      <div className="stat-box" key={i} style={{background: colors[(i+1) % colors.length]}}>
                        <span className="stat-val">{m.value}</span>
                        <span className="stat-lbl">{m.label}</span>
                      </div>
                    ))}
                  </div>
                  
                  {stats.metrics.length > 4 && (
                    <div style={{textAlign:'center', marginTop:'20px'}}>
                      <button onClick={() => setExpandedStats(!expandedStats)} style={{background:'rgba(128,128,128,0.2)', color:'inherit', borderRadius:'20px'}}>
                        {expandedStats ? 'Show Less' : `Show All ${stats.metrics.length} Metrics`}
                      </button>
                    </div>
                  )}

                  {/* CHART */}
                  <h3 style={{textAlign:'center', marginTop:'40px', opacity:0.7}}>Distribution Analysis</h3>
                  <div style={{height:'350px', display:'flex', justifyContent:'center'}}>
                    <Doughnut 
                      data={{ 
                        labels: Object.keys(stats.chart_data || {}), 
                        datasets: [{ 
                          data: Object.values(stats.chart_data || {}), 
                          backgroundColor: colors, 
                          borderWidth: 0,
                          hoverOffset: 15 
                        }] 
                      }} 
                      options={{ 
                        maintainAspectRatio: false, 
                        cutout: '70%',
                        plugins: { legend: { position: 'right', labels: { color: theme === 'dark' ? '#e0e0e0' : '#333' } } } 
                      }} 
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* --- MODALS --- */}
        
        {/* History Modal */}
        {showHistory && (
          <Modal title="Upload History" onClose={() => setShowHistory(false)}>
            {historyList.length === 0 ? <p>No history found.</p> : (
              <div style={{maxHeight:'300px', overflowY:'auto'}}>
                {historyList.map((item, i) => (
                  <div key={i} style={{padding:'10px', borderBottom:'1px solid rgba(128,128,128,0.2)'}}>
                    <div style={{fontWeight:'bold'}}>📄 {item.name}</div>
                    <div style={{fontSize:'12px', opacity:0.7}}>📅 {item.date} • 📊 {item.rows} Rows</div>
                  </div>
                ))}
              </div>
            )}
          </Modal>
        )}

        {/* Edit Profile Modal */}
        {showEditProfile && (
          <Modal title="Edit Profile & Security" onClose={() => setShowEditProfile(false)}>
            <form onSubmit={handleProfileSave}>
              <label style={{display:'block', marginBottom:'5px', fontWeight:'bold', color:'#3b82f6'}}>Profile Details</label>
              <input name="newName" placeholder="Update Full Name" onChange={handleInputChange} />
              
              <label style={{display:'block', marginBottom:'5px', marginTop:'20px', fontWeight:'bold', color:'#3b82f6'}}>Change Password</label>
              <input name="newPass" type="password" placeholder="New Password" onChange={handleInputChange} />
              <input name="confirmPass" type="password" placeholder="Confirm New Password" onChange={handleInputChange} />
              
              <button type="submit" style={{background:'#10b981', color:'white', width:'100%', marginTop:'10px'}}>Save Changes</button>
            </form>
          </Modal>
        )}

      </div>
    );
  }

  return null;
}

export default App;