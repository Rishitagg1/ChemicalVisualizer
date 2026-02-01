import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import 'chart.js/auto';
import './App.css';

function App() {
  // --- STATE ---
  const [view, setView] = useState('welcome'); // 'welcome', 'login', 'signup', 'dashboard'
  const [theme, setTheme] = useState('light');
  const [user, setUser] = useState({});
  const [formData, setFormData] = useState({});
  const [stats, setStats] = useState(null);

  // --- THEME ---
  useEffect(() => { document.documentElement.setAttribute('data-theme', theme); }, [theme]);
  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');
  const ThemeToggle = () => (<div className="theme-switch" onClick={toggleTheme}><div className="switch-thumb"></div></div>);

  // --- HANDLERS ---
  const handleInputChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleLogin = async (e) => { 
    e.preventDefault(); 
    try { 
      const res = await axios.post('http://127.0.0.1:8000/api/login/', formData); 
      setUser({ name: res.data.name }); 
      setView('dashboard'); 
    } catch (err) { alert('Invalid Credentials'); } 
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/api/signup/', formData);
      alert('Account Created! Please Login.');
      setView('login');
    } catch (err) { alert('Signup Failed. Email might exist.'); }
  };

  const handleUpload = async (e) => { 
    const file = e.target.files[0]; if (!file) return; 
    const data = new FormData(); data.append('file', file); 
    try { const res = await axios.post('http://127.0.0.1:8000/api/upload/', data); setStats(res.data); } 
    catch (err) { alert('Upload Failed'); } 
  };

  const colors = ['#fc8181', '#f687b3', '#f6ad55', '#faf089', '#68d391', '#63b3ed'];
  const chartHoleColor = theme === 'dark' ? '#292d32' : '#e0e5ec';

  // ============================================
  // RENDER VIEWS
  // ============================================

  // --- 1. WELCOME / LOGIN / SIGNUP ---
  if (['welcome', 'login', 'signup'].includes(view)) {
    return (
      <div className="app-container">
        <div className="skeuo-card" style={{maxWidth: '400px', margin: '0 auto', textAlign:'center'}}>
          <div style={{display:'flex', justifyContent:'flex-end', width:'100%', marginBottom:'10px'}}><ThemeToggle /></div>
          
          <h1>Chemical Vis</h1>
          <p>Universal Data Console</p>

          <div style={{margin: '30px 0'}}>
            <div style={{width:'80px', height:'80px', borderRadius:'50%', background:'var(--bg)', margin:'0 auto', boxShadow:'5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light)', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'30px'}}>🧪</div>
          </div>

          {view === 'welcome' && (
             <button onClick={() => setView('login')}>Initialize System</button>
          )}

          {view === 'login' && (
            <form onSubmit={handleLogin} style={{width: '100%'}}>
              <input className="skeuo-inset" name="email" placeholder="Email" onChange={handleInputChange} required />
              <input className="skeuo-inset" name="password" type="password" placeholder="Password" onChange={handleInputChange} required />
              <button type="submit" style={{color: '#ff8c00', marginTop:'10px'}}>Authenticate</button>
              
              <div style={{marginTop:'20px', display:'flex', justifyContent:'space-between', fontSize:'12px'}}>
                <span onClick={() => setView('signup')} style={{cursor:'pointer', color:'#ff8c00', fontWeight:'bold'}}>Create Account</span>
                <span onClick={() => setView('welcome')} style={{cursor:'pointer', textDecoration:'underline'}}>Back</span>
              </div>
            </form>
          )}

          {view === 'signup' && (
            <form onSubmit={handleSignup} style={{width: '100%'}}>
              <input className="skeuo-inset" name="name" placeholder="Full Name" onChange={handleInputChange} required />
              <input className="skeuo-inset" name="email" placeholder="Email" onChange={handleInputChange} required />
              <input className="skeuo-inset" name="password" type="password" placeholder="Set Password" onChange={handleInputChange} required />
              <input className="skeuo-inset" name="phone" placeholder="Phone" onChange={handleInputChange} />
              <input className="skeuo-inset" name="institute" placeholder="Institute / Company" onChange={handleInputChange} />
              
              <button type="submit" style={{color: '#10b981', marginTop:'10px'}}>Register User</button>
              
              <p onClick={() => setView('login')} style={{marginTop:'20px', fontSize:'12px', cursor:'pointer', textDecoration:'underline'}}>
                Already have an account? Login
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  // --- 2. DASHBOARD ---
  return (
    <div className="app-container">
      <div className="skeuo-card">
        <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'30px'}}>
          <div><h1>Console: {user.name}</h1><p style={{margin:0}}>System Online • Ready</p></div>
          <div style={{display:'flex', gap:'15px', alignItems:'center'}}>
            <ThemeToggle />
            <button onClick={() => setView('welcome')} style={{width:'auto', fontSize:'12px', padding:'10px 20px'}}>Logout</button>
          </div>
        </div>

        <div className="upload-area" onClick={() => document.getElementById('fileInput').click()}>
           📂 LOAD DATASET (CSV, EXCEL, JSON)
           <input id="fileInput" type="file" hidden onChange={handleUpload} accept=".csv, .xlsx, .xls, .json" />
        </div>

        {stats && (
          <div className="fade-in">
            <div className="stats-grid" style={{gridTemplateColumns: `repeat(${Math.min((stats.metrics?.length || 0) + 1, 4)}, 1fr)`}}>
              <div className="stat-box"><span className="stat-val">{stats.total_count}</span><span className="stat-lbl">Entries</span></div>
              {stats.metrics && stats.metrics.map((metric, index) => (
                <div className="stat-box" key={index}>
                  <span className="stat-val" style={{color: colors[index % colors.length]}}>{metric.value}</span>
                  <span className="stat-lbl">{metric.label}</span>
                </div>
              ))}
            </div>

            <div className="skeuo-inset" style={{height:'400px', display:'flex', alignItems:'center', justifyContent:'center', position:'relative'}}>
               <Doughnut data={{ labels: Object.keys(stats.chart_data || {}), datasets: [{ data: Object.values(stats.chart_data || {}), backgroundColor: colors, borderWidth: 0 }] }} options={{ maintainAspectRatio: false, cutout: '60%', plugins: { legend: { position: 'right', labels: { color: theme === 'dark' ? '#e0e0e0' : '#4a5568' } } } }} />
               <div style={{position:'absolute', width:'100px', height:'100px', borderRadius:'50%', background: chartHoleColor, boxShadow: `inset 2px 2px 5px var(--shadow-dark), inset -2px -2px 5px var(--shadow-light)`}}></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;