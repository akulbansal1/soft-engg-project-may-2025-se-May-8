import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import Appointments from './pages/Appointments';
import Profile from './pages/Profile';
import Login from './pages/Login';
import './index.css';

const { Content } = Layout;

// Layout wrapper component that conditionally shows sidebar/header
const AppLayout = ({ children }) => {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return children;
  }

  return (
    <Layout style={{ height: '100vh', background: '#f8fafc' }}>
      <Sidebar />
      <Layout style={{ background: '#f8fafc' }}>
        <Header />
        <Content style={{ 
          padding: '32px', 
          background: '#f8fafc',
          overflow: 'auto'
        }}>
          {children}
        </Content>
      </Layout>
    </Layout>
  );
};

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#2563eb',
          colorSuccess: '#10b981',
          colorWarning: '#f59e0b',
          colorError: '#ef4444',
          borderRadius: 12,
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          fontSize: 14,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
        components: {
          Layout: {
            bodyBg: '#f8fafc',
            siderBg: '#ffffff',
            headerBg: '#ffffff',
          },
          Menu: {
            itemBg: 'transparent',
            itemSelectedBg: '#f1f5f9',
            itemHoverBg: '#f8fafc',
            itemSelectedColor: '#2563eb',
            itemColor: '#64748b',
          },
          Card: {
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
          }
        }
      }}
    >
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard/:id" element={<Dashboard />} />
            <Route path="/patients/:id" element={<Patients />} />
            <Route path="/appointments/:id" element={<Appointments />} />
            <Route path="/profile/:id" element={<Profile />} />
          </Routes>
        </AppLayout>
      </Router>
    </ConfigProvider>
  );
}

export default App;