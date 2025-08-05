import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Avatar, Dropdown, Space, Typography, Badge, Button, Input, message } from 'antd';
import { 
  BellOutlined, 
  UserOutlined, 
  LogoutOutlined, 
  SearchOutlined,
  MessageOutlined,
  SettingOutlined
} from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Text } = Typography;
const { Search } = Input;

const Header = () => {
  const [doctorDetails, setDoctorDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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

    setDoctorDetails(activeDoctor);
    setLoading(false);
  }, [navigate]);

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'My Profile',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Account Settings',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Sign Out',
      danger: true,
      onClick: () => handleLogout()
    },
  ];

  const notificationItems = [
    {
      key: '1',
      label: (
        <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
          <Text strong style={{ fontSize: '13px', color: '#1e293b' }}>New appointment scheduled</Text>
          <br />
          <Text style={{ fontSize: '12px', color: '#64748b' }}>John Doe - 2:30 PM today</Text>
        </div>
      ),
    },
    {
      key: '2',
      label: (
        <div style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
          <Text strong style={{ fontSize: '13px', color: '#1e293b' }}>Lab results ready</Text>
          <br />
          <Text style={{ fontSize: '12px', color: '#64748b' }}>Patient ID: #12345</Text>
        </div>
      ),
    },
    {
      key: '3',
      label: (
        <div style={{ padding: '8px 0' }}>
          <Text strong style={{ fontSize: '13px', color: '#1e293b' }}>Prescription refill request</Text>
          <br />
          <Text style={{ fontSize: '12px', color: '#64748b' }}>Sarah Johnson - Pending approval</Text>
        </div>
      ),
    },
  ];

  const handleLogout = () => {
    // Clear localStorage and redirect to login
    localStorage.removeItem('activeDoctorDetails');
    message.success('Logged out successfully');
    navigate('/login');
  };

  // Get greeting based on time
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  // Get initials for avatar
  const getInitials = (name) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (loading || !doctorDetails) {
    return null;
  }

  return (
    <AntHeader style={{
      background: '#ffffff',
      padding: '0 16px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid #e2e8f0',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.02)',
      height: '72px',
      minWidth: '0', // Prevents flex item from overflowing
      '@media (min-width: 768px)': {
        padding: '0 24px'
      },
      '@media (min-width: 1024px)': {
        padding: '0 32px'
      }
    }}>
      {/* Left Section - Welcome Message */}
      <div style={{ 
        flex: '1 1 auto',
        minWidth: '0', // Allows flex item to shrink
        marginRight: '16px'
      }}>
        <Text style={{ 
          fontSize: '18px', 
          fontWeight: '700', 
          color: '#1e293b',
          lineHeight: '1.2',
          display: 'block',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          '@media (min-width: 768px)': {
            fontSize: '22px'
          },
          '@media (min-width: 1024px)': {
            fontSize: '24px'
          }
        }}>
          {getGreeting()}, {doctorDetails.name}
        </Text>
        <Text style={{ 
          fontSize: '12px', 
          color: '#64748b',
          fontWeight: '500',
          display: 'block',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          '@media (min-width: 768px)': {
            fontSize: '13px'
          },
          '@media (min-width: 1024px)': {
            fontSize: '14px'
          }
        }}>
          8 appointments today • {doctorDetails.location} • {new Date().toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric' 
          })}
        </Text>
      </div>

      {/* Center Section - Search (Hidden on small screens) */}
      <div style={{ 
        flex: '0 1 300px',
        maxWidth: '400px', 
        margin: '0 16px',
        display: 'none',
        '@media (min-width: 1024px)': {
          display: 'block'
        }
      }}>
        <Search
          placeholder="Search patients, appointments..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          style={{
            borderRadius: '12px',
          }}
        />
      </div>
      
      {/* Right Section - Actions */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexShrink: 0 // Prevents this section from shrinking
      }}>
        {/* Quick Actions - Hide message button on small screens */}
        <div style={{
          display: 'none',
          '@media (min-width: 768px)': {
            display: 'flex'
          }
        }}>
          <Button
            type="text"
            icon={<MessageOutlined />}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              color: '#64748b',
              marginRight: '8px'
            }}
          />
        </div>
        
        <Dropdown
          menu={{ items: notificationItems }}
          placement="bottomRight"
          arrow
          trigger={['click']}
        >
          <Button
            type="text"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              color: '#64748b',
              position: 'relative',
              marginRight: '12px'
            }}
          >
            <Badge count={3} size="small" offset={[2, -2]}>
              <BellOutlined style={{ fontSize: '18px' }} />
            </Badge>
          </Button>
        </Dropdown>

        {/* User Profile Dropdown */}
        <Dropdown
          menu={{ items: userMenuItems }}
          placement="bottomRight"
          arrow
          trigger={['click']}
        >
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px 4px 4px',
            borderRadius: '12px',
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            minWidth: '0' // Allows content to shrink
          }}>
            <Avatar
              size={36}
              style={{
                background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                border: '2px solid white',
                boxShadow: '0 2px 8px rgba(37, 99, 235, 0.2)',
                flexShrink: 0
              }}
            >
              {getInitials(doctorDetails.name)}
            </Avatar>
            <div style={{ 
              textAlign: 'left',
              minWidth: '0',
              display: 'none',
              '@media (min-width: 640px)': {
                display: 'block'
              }
            }}>
              <Text style={{ 
                fontSize: '13px', 
                fontWeight: '600', 
                color: '#1e293b',
                display: 'block',
                lineHeight: '1.2',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {doctorDetails.name}
              </Text>
              <Text style={{ 
                fontSize: '11px', 
                color: '#64748b',
                fontWeight: '500'
              }}>
                Online
              </Text>
            </div>
          </div>
        </Dropdown>
      </div>
    </AntHeader>
  );
};

export default Header;