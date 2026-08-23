import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Activity, AlertTriangle, CheckCircle, TrendingUp,
  Shield, Zap, Database, RefreshCw
} from 'lucide-react';
import './App.css';

const API_URL = 'http://localhost:5000';
const MONITOR_URL = 'http://localhost:5001';

function App() {
  const [socket, setSocket] = useState(null);
  const [modelHealth, setModelHealth] = useState({
    status: 'healthy',
    drift_score_ks: 0,
    drift_score_kl: 0,
    total_inferences: 0,
    drift_detected: false
  });
  const [driftHistory, setDriftHistory] = useState([]);
  const [driftEvents, setDriftEvents] = useState([]);
  const [inferenceData, setInferenceData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(MONITOR_URL);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to monitor service');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from monitor service');
      setConnected(false);
    });

    newSocket.on('health_update', (data) => {
      setModelHealth(data);
      
      // Update drift history for chart
      setDriftHistory(prev => {
        const newPoint = {
          timestamp: new Date().toLocaleTimeString(),
          ks_score: data.drift_score_ks,
          kl_score: data.drift_score_kl
        };
        return [...prev.slice(-30), newPoint];
      });
    });

    newSocket.on('drift_alert', (data) => {
      const alert = {
        id: Date.now(),
        type: 'drift',
        message: `Drift detected! KS: ${data.drift_score_ks.toFixed(4)}, KL: ${data.drift_score_kl.toFixed(4)}`,
        timestamp: new Date().toLocaleTimeString(),
        severity: 'critical'
      };
      setAlerts(prev => [alert, ...prev.slice(0, 9)]);
    });

    newSocket.on('adversarial_detected', (data) => {
      const alert = {
        id: Date.now(),
        type: 'adversarial',
        message: `Adversarial input detected: ${data.pattern}`,
        timestamp: new Date().toLocaleTimeString(),
        severity: 'warning'
      };
      setAlerts(prev => [alert, ...prev.slice(0, 9)]);
    });

    newSocket.on('rollback_complete', (data) => {
      const alert = {
        id: Date.now(),
        type: 'rollback',
        message: 'Model rollback completed successfully',
        timestamp: new Date().toLocaleTimeString(),
        severity: 'success'
      };
      setAlerts(prev => [alert, ...prev.slice(0, 9)]);
    });

    // Fetch initial data
    fetchDriftEvents();
    fetchInferenceLogs();

    // Poll for updates
    const interval = setInterval(() => {
      fetchDriftEvents();
      fetchInferenceLogs();
    }, 5000);

    return () => {
      newSocket.close();
      clearInterval(interval);
    };
  }, []);

  const fetchDriftEvents = async () => {
    try {
      const response = await axios.get(`${MONITOR_URL}/drift_events?limit=20`);
      setDriftEvents(response.data);
    } catch (error) {
      console.error('Error fetching drift events:', error);
    }
  };

  const fetchInferenceLogs = async () => {
    try {
      const response = await axios.get(`${MONITOR_URL}/inference_logs?limit=50`);
      const data = response.data;
      
      // Aggregate for visualization
      const aggregated = data.reduce((acc, log) => {
        const minute = new Date(log.timestamp).toLocaleTimeString();
        if (!acc[minute]) {
          acc[minute] = { timestamp: minute, fraud: 0, legitimate: 0 };
        }
        if (log.prediction === 1) {
          acc[minute].fraud++;
        } else {
          acc[minute].legitimate++;
        }
        return acc;
      }, {});
      
      setInferenceData(Object.values(aggregated).slice(-20));
    } catch (error) {
      console.error('Error fetching inference logs:', error);
    }
  };

  const triggerBaseline = async () => {
    try {
      await axios.post(`${API_URL}/baseline`);
      const alert = {
        id: Date.now(),
        type: 'info',
        message: 'Baseline generated successfully',
        timestamp: new Date().toLocaleTimeString(),
        severity: 'success'
      };
      setAlerts(prev => [alert, ...prev.slice(0, 9)]);
    } catch (error) {
      console.error('Error generating baseline:', error);
    }
  };

  const resetMonitoring = async () => {
    try {
      await axios.post(`${MONITOR_URL}/reset`);
      setDriftHistory([]);
      setDriftEvents([]);
      setAlerts([]);
      const alert = {
        id: Date.now(),
        type: 'info',
        message: 'Monitoring state reset',
        timestamp: new Date().toLocaleTimeString(),
        severity: 'success'
      };
      setAlerts([alert]);
    } catch (error) {
      console.error('Error resetting monitoring:', error);
    }
  };

  const getStatusColor = (status) => {
    if (modelHealth.drift_detected) return '#ef4444';
    return status === 'healthy' ? '#10b981' : '#f59e0b';
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Shield size={32} />
            <h1>ModelGuardian</h1>
          </div>
          <div className="connection-status">
            <div className={`status-indicator ${connected ? 'connected' : 'disconnected'}`} />
            <span>{connected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: getStatusColor(modelHealth.status) }}>
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Model Status</div>
            <div className="stat-value">{modelHealth.drift_detected ? 'DRIFT DETECTED' : 'Healthy'}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#3b82f6' }}>
            <TrendingUp size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">KS Score</div>
            <div className="stat-value">{modelHealth.drift_score_ks.toFixed(4)}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#8b5cf6' }}>
            <Zap size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">KL Divergence</div>
            <div className="stat-value">{modelHealth.drift_score_kl.toFixed(4)}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: '#06b6d4' }}>
            <Database size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Inferences</div>
            <div className="stat-value">{modelHealth.total_inferences}</div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        {/* Drift Score Chart */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Drift Detection Over Time</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={driftHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="timestamp" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ background: '#1f2937', border: 'none' }} />
              <Legend />
              <Line type="monotone" dataKey="ks_score" stroke="#3b82f6" name="KS Score" strokeWidth={2} />
              <Line type="monotone" dataKey="kl_score" stroke="#8b5cf6" name="KL Divergence" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Inference Distribution */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Prediction Distribution</h3>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={inferenceData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="timestamp" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip contentStyle={{ background: '#1f2937', border: 'none' }} />
              <Legend />
              <Area type="monotone" dataKey="fraud" stackId="1" stroke="#ef4444" fill="#ef4444" name="Fraud" />
              <Area type="monotone" dataKey="legitimate" stackId="1" stroke="#10b981" fill="#10b981" name="Legitimate" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts and Events */}
      <div className="bottom-grid">
        {/* Alerts */}
        <div className="alerts-card">
          <div className="card-header">
            <h3><AlertTriangle size={20} /> Real-time Alerts</h3>
          </div>
          <div className="alerts-list">
            {alerts.length === 0 ? (
              <div className="no-alerts">
                <CheckCircle size={48} />
                <p>No alerts - System running smoothly</p>
              </div>
            ) : (
              alerts.map(alert => (
                <div key={alert.id} className={`alert alert-${alert.severity}`}>
                  <div className="alert-content">
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-time">{alert.timestamp}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Drift Events */}
        <div className="events-card">
          <div className="card-header">
            <h3><Activity size={20} /> Drift Events History</h3>
          </div>
          <div className="events-list">
            {driftEvents.length === 0 ? (
              <div className="no-events">No drift events recorded</div>
            ) : (
              driftEvents.slice(-10).reverse().map((event, idx) => (
                <div key={idx} className="event-item">
                  <div className="event-type">{event.action || event.type}</div>
                  <div className="event-details">
                    {event.drift_score_ks && (
                      <span>KS: {event.drift_score_ks.toFixed(4)}</span>
                    )}
                    {event.drift_score_kl && (
                      <span>KL: {event.drift_score_kl.toFixed(4)}</span>
                    )}
                    {event.pattern && (
                      <span>Pattern: {event.pattern}</span>
                    )}
                  </div>
                  <div className="event-time">{new Date(event.timestamp).toLocaleString()}</div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="actions-card">
          <div className="card-header">
            <h3>Actions</h3>
          </div>
          <div className="actions-list">
            <button className="action-button primary" onClick={triggerBaseline}>
              <CheckCircle size={18} />
              Generate Baseline
            </button>
            <button className="action-button secondary" onClick={resetMonitoring}>
              <RefreshCw size={18} />
              Reset Monitoring
            </button>
            <button className="action-button info" onClick={fetchDriftEvents}>
              <Activity size={18} />
              Refresh Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
