import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Avatar, 
  Tag, 
  Button, 
  Input, 
  Space, 
  Typography,
  Dropdown,
  Row,
  Col,
  Spin,
  message
} from 'antd';
import { 
  SearchOutlined, 
  PlusOutlined, 
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  UserOutlined,
  PhoneOutlined,
  MailOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';

const { Title, Text } = Typography;
const { Search } = Input;

const Patients = () => {
  const { id } = useParams();
  const [searchText, setSearchText] = useState('');
  const [patients, setPatients] = useState([]);
  const [filteredPatients, setFilteredPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);

        const response = await fetch(`${BACKEND_BASE_URL}/api/v1/users/`, {
          method: 'GET',
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Transform API data to match component structure
        const transformedData = data.map(patient => ({
          id: patient.id,
          name: patient.name,
          phone: patient.phone,
          age: calculateAge(patient.dob),
          gender: patient.gender,
          dob: patient.dob,
          email: generateEmail(patient.name), // Generate email from name
          condition: generateCondition(), // Generate random condition for display
          lastVisit: formatDate(patient.created_at),
          status: patient.is_active ? 'Active' : 'Inactive',
          created_at: patient.created_at
        }));
        
        setPatients(transformedData);
        setFilteredPatients(transformedData);
      } catch (error) {
        console.error('Error fetching patients:', error);
        message.error('Failed to load patients. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  // Helper function to calculate age from date of birth
  const calculateAge = (dob) => {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    
    return age;
  };

  // Helper function to generate email from name
  const generateEmail = (name) => {
    return name.toLowerCase().replace(' ', '.') + '@email.com';
  };

  // Helper function to generate random condition (since not in API)
  const generateCondition = () => {
    const conditions = ['Hypertension', 'Diabetes', 'Heart Disease', 'Anxiety', 'Arthritis', 'Migraine'];
    return conditions[Math.floor(Math.random() * conditions.length)];
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleSearch = (value) => {
    setSearchText(value);
    const filtered = patients.filter(patient =>
      patient.name.toLowerCase().includes(value.toLowerCase()) ||
      patient.condition.toLowerCase().includes(value.toLowerCase()) ||
      patient.phone.includes(value)
    );
    setFilteredPatients(filtered);
  };

  const actionMenuItems = [
    {
      key: 'view',
      icon: <EyeOutlined />,
      label: 'View Details',
    },
    {
      key: 'edit',
      icon: <EditOutlined />,
      label: 'Edit Patient',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: 'Delete Patient',
      danger: true,
    },
  ];

  const getStatusColor = (status) => {
    return status === 'Active' ? '#10b981' : '#f59e0b';
  };

  const getConditionColor = (condition) => {
    const colors = {
      'Hypertension': '#ef4444',
      'Diabetes': '#f59e0b',
      'Heart Disease': '#dc2626',
      'Anxiety': '#3b82f6',
      'Arthritis': '#8b5cf6',
      'Migraine': '#06b6d4'
    };
    return colors[condition] || '#64748b';
  };

  const columns = [
    {
      title: 'Patient Information',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Avatar
            size={44}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              fontSize: '16px',
              fontWeight: '600'
            }}
          >
            {text.split(' ').map(n => n[0]).join('')}
          </Avatar>
          <div>
            <Text style={{ 
              fontSize: '16px', 
              fontWeight: '600', 
              color: '#1e293b',
              display: 'block',
              marginBottom: '2px'
            }}>
              {text}
            </Text>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <MailOutlined style={{ fontSize: '12px', color: '#64748b' }} />
              <Text style={{ fontSize: '13px', color: '#64748b' }}>
                {record.email}
              </Text>
            </div>
          </div>
        </div>
      ),
    },
    {
      title: 'Demographics',
      key: 'demographics',
      render: (_, record) => (
        <div>
          <Text style={{ 
            fontSize: '15px', 
            fontWeight: '600', 
            color: '#1e293b',
            display: 'block',
            marginBottom: '2px'
          }}>
            {record.age} years
          </Text>
          <Text style={{ fontSize: '13px', color: '#64748b' }}>
            {record.gender}
          </Text>
        </div>
      ),
    },
    {
      title: 'Contact',
      dataIndex: 'phone',
      key: 'phone',
      render: (phone) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <PhoneOutlined style={{ fontSize: '12px', color: '#64748b' }} />
          <Text style={{ fontSize: '14px', color: '#1e293b', fontWeight: '500' }}>
            {phone}
          </Text>
        </div>
      ),
    },
    {
      title: 'Last Visit',
      dataIndex: 'lastVisit',
      key: 'lastVisit',
      render: (date) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CalendarOutlined style={{ fontSize: '12px', color: '#64748b' }} />
          <Text style={{ fontSize: '14px', color: '#1e293b' }}>
            {date}
          </Text>
        </div>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag
          color={getStatusColor(status)}
          style={{
            borderRadius: '8px',
            fontSize: '11px',
            fontWeight: '600',
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            padding: '4px 8px',
            border: 'none'
          }}
        >
          {status}
        </Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <Dropdown
          menu={{ items: actionMenuItems }}
          placement="bottomRight"
          arrow
        >
          <Button 
            type="text" 
            icon={<MoreOutlined />}
            style={{
              borderRadius: '8px',
              width: '32px',
              height: '32px'
            }}
          />
        </Dropdown>
      ),
    },
  ];

  // Calculate stats from actual data
  const activePatients = patients.filter(p => p.status === 'Active').length;
  const newThisMonth = patients.filter(p => {
    const createdDate = new Date(p.created_at);
    const currentDate = new Date();
    return createdDate.getMonth() === currentDate.getMonth() && 
           createdDate.getFullYear() === currentDate.getFullYear();
  }).length;

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px' 
      }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 16px' }}>
      {/* Header Section */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ 
          color: '#1e293b', 
          marginBottom: '8px', 
          fontSize: 'clamp(24px, 4vw, 32px)', 
          fontWeight: '700' 
        }}>
          Patient Management
        </Title>
        <Text style={{ fontSize: 'clamp(14px, 2vw, 16px)', color: '#64748b', fontWeight: '500' }}>
          Manage and monitor your patient records and health information
        </Text>
      </div>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        
        <Col xs={24} sm={8}>
          <Card
            style={{
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: 'clamp(16px, 3vw, 24px)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: 'clamp(12px, 2vw, 14px)', 
                  color: '#64748b', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  TOTAL PATIENTS
                </Text>
                <Text style={{ 
                  fontSize: 'clamp(24px, 5vw, 32px)', 
                  fontWeight: '700', 
                  color: '#1e293b', 
                  lineHeight: '1'
                }}>
                  {patients.length}
                </Text>
              </div>
              <div style={{
                width: 'clamp(48px, 8vw, 60px)',
                height: 'clamp(48px, 8vw, 60px)',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <UserOutlined style={{ fontSize: 'clamp(20px, 4vw, 28px)', color: 'white' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            style={{
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: 'clamp(16px, 3vw, 24px)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: 'clamp(12px, 2vw, 14px)', 
                  color: '#64748b', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  ACTIVE PATIENTS
                </Text>
                <Text style={{ 
                  fontSize: 'clamp(24px, 5vw, 32px)', 
                  fontWeight: '700', 
                  color: '#1e293b', 
                  lineHeight: '1'
                }}>
                  {activePatients}
                </Text>
              </div>
              <div style={{
                width: 'clamp(48px, 8vw, 60px)',
                height: 'clamp(48px, 8vw, 60px)',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <UserOutlined style={{ fontSize: 'clamp(20px, 4vw, 28px)', color: 'white' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={8}>
          <Card
            style={{
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: 'clamp(16px, 3vw, 24px)' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: 'clamp(12px, 2vw, 14px)', 
                  color: '#64748b', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  NEW THIS MONTH
                </Text>
                <Text style={{ 
                  fontSize: 'clamp(24px, 5vw, 32px)', 
                  fontWeight: '700', 
                  color: '#1e293b', 
                  lineHeight: '1'
                }}>
                  {newThisMonth}
                </Text>
              </div>
              <div style={{
                width: 'clamp(48px, 8vw, 60px)',
                height: 'clamp(48px, 8vw, 60px)',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <PlusOutlined style={{ fontSize: 'clamp(20px, 4vw, 28px)', color: 'white' }} />
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Main Content */}
      <Card
        style={{
          borderRadius: '16px',
          border: '1px solid #e2e8f0',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        }}
        bodyStyle={{ padding: 'clamp(16px, 3vw, 24px)' }}
      >
        {/* Header with Search and Add Button */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '24px',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          <Search
            placeholder="Search patients by name, condition, or phone..."
            allowClear
            enterButton={
              <Button 
                type="primary" 
                icon={<SearchOutlined />}
                style={{
                  borderRadius: '0 8px 8px 0',
                  height: '40px',
                  fontWeight: '600'
                }}
              >
                Search
              </Button>
            }
            size="large"
            onSearch={handleSearch}
            onChange={(e) => handleSearch(e.target.value)}
            style={{ 
              maxWidth: '400px',
              flex: 1
            }}
            className="custom-search"
          />
        </div>

        {/* Results Summary */}
        <div style={{ marginBottom: '16px' }}>
          <Text style={{ color: '#64748b', fontSize: '14px' }}>
            Showing {filteredPatients.length} of {patients.length} patients
            {searchText && ` for "${searchText}"`}
          </Text>
        </div>

        {/* Table */}
        <Table
          columns={columns}
          dataSource={filteredPatients}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} of ${total} patients`,
            style: { marginTop: '24px' }
          }}
          style={{
            borderRadius: '12px',
            overflow: 'hidden'
          }}
          rowClassName={() => 'custom-table-row'}
        />
      </Card>

      <style jsx>{`
        .custom-table-row:hover {
          background: #f8fafc !important;
        }
        .ant-table-thead > tr > th {
          background: #f8fafc !important;
          border-bottom: 1px solid #e2e8f0 !important;
          font-weight: 600 !important;
          color: #1e293b !important;
        }
        .ant-table-tbody > tr > td {
          border-bottom: 1px solid #f1f5f9 !important;
          padding: 16px !important;
        }
      `}</style>
    </div>
  );
};

export default Patients;