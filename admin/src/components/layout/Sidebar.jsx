import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Avatar } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  UserOutlined,
  CalendarOutlined,
  SettingOutlined,
  HeartOutlined,
  FileTextOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Text } = Typography;

const Sidebar = () => {
  const [loading, setLoading] = useState(true);
  const [collapsed, setCollapsed] = useState(false);
  const [doctorDetails, setDoctorDetails] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: doctorDetails ? `/dashboard/${doctorDetails.id}` : '/dashboard',
      icon: <DashboardOutlined style={{ fontSize: '18px' }} />,
      label: <span style={{ fontSize: '15px', fontWeight: '500' }}>Dashboard</span>,
    },
    {
      key: doctorDetails ? `/patients/${doctorDetails.id}` : '/patients',
      icon: <UserOutlined style={{ fontSize: '18px' }} />,
      label: <span style={{ fontSize: '15px', fontWeight: '500' }}>Patients</span>,
    },
    {
      key: doctorDetails ? `/appointments/${doctorDetails.id}` : '/appointments',
      icon: <CalendarOutlined style={{ fontSize: '18px' }} />,
      label: <span style={{ fontSize: '15px', fontWeight: '500' }}>Appointments</span>,
    },
    {
      key: doctorDetails ? `/profile/${doctorDetails.id}` : '/profile',
      icon: <SettingOutlined style={{ fontSize: '18px' }} />,
      label: <span style={{ fontSize: '15px', fontWeight: '500' }}>Settings</span>,
    },
  ];

  useEffect(() => {
    const getActiveDoctorDetails = () => {
      try {
        const storedDetails = localStorage.getItem('activeDoctorDetails');
        if (storedDetails) {
          const parsedDetails = JSON.parse(storedDetails);
          return parsedDetails;
        }
        return null;
      } catch (error) {
        console.error('Error parsing doctor details from localStorage:', error);
        localStorage.removeItem('activeDoctorDetails');
        return null;
      }
    };

    const activeDoctor = getActiveDoctorDetails();
    
    if (!activeDoctor) {
      message.warning('Please select a doctor profile to access the dashboard');
      navigate('/login');
      return;
    }

    // Set doctor details and stop loading
    setDoctorDetails(activeDoctor);
    setLoading(false);
  }, [navigate]);

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      width={280}
      collapsedWidth={80}
      style={{
        background: '#ffffff',
        borderRight: '1px solid #e2e8f0',
        boxShadow: '2px 0 8px rgba(0, 0, 0, 0.02)',
      }}
      trigger={
        <div style={{
          background: '#ffffff',
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '48px',
          color: '#64748b',
          fontSize: '16px'
        }}>
          {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
        </div>
      }
    >
      {/* Logo Section */}
      <div style={{
        padding: collapsed ? '24px 16px' : '32px 24px',
        borderBottom: '1px solid #f1f5f9',
        textAlign: collapsed ? 'center' : 'left'
      }}>
        {collapsed ? (
          <div style={{
            width: '40px',
            height: '40px',
            background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto'
          }}>
            <HeartOutlined style={{ color: 'white', fontSize: '20px' }} />
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <HeartOutlined style={{ color: 'white', fontSize: '24px' }} />
            </div>
            <div>
              <Text style={{ 
                fontSize: '20px', 
                fontWeight: '700', 
                color: '#1e293b',
                lineHeight: '1.2',
                display: 'block'
              }}>
                HealthCare
              </Text>
              <Text style={{ 
                fontSize: '13px', 
                color: '#64748b',
                fontWeight: '500'
              }}>
                Medical Dashboard
              </Text>
            </div>
          </div>
        )}
      </div>

      {/* Doctor Profile Section */}
      {!collapsed && (
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #f1f5f9',
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Avatar
              size={44}
              style={{
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                border: '2px solid white',
                boxShadow: '0 2px 8px rgba(16, 185, 129, 0.2)'
              }}
            >
              {doctorDetails ? getInitials(doctorDetails.name) : 'DC'}
            </Avatar>
            <div style={{ flex: 1 }}>
              <Text style={{ 
                fontSize: '15px', 
                fontWeight: '600', 
                color: '#1e293b',
                display: 'block',
                lineHeight: '1.3'
              }}>
                {doctorDetails ? doctorDetails.name : 'Dr. John Doe'}
              </Text>
              <Text style={{ 
                fontSize: '12px', 
                color: '#64748b',
                fontWeight: '500'
              }}>
                General Practitioner
              </Text>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Menu */}
      <div style={{ padding: '16px 0' }}>
        <Menu
          selectedKeys={[location.pathname]}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            background: 'transparent',
            border: 'none',
            fontSize: '15px'
          }}
        />
      </div>
    </Sider>
  );
};

export default Sidebar;