import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Avatar, 
  Typography, 
  Row, 
  Col, 
  Button, 
  Descriptions,
  Divider,
  Modal,
  Form,
  Input,
  message,
  Spin,
  Popconfirm,
  Space
} from 'antd';
import { 
  EditOutlined, 
  MailOutlined, 
  PhoneOutlined, 
  UserOutlined,
  DeleteOutlined,
  SaveOutlined 
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

const Profile = () => {
  const { id } = useParams();
  const [doctorData, setDoctorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [form] = Form.useForm();

  const SESSION_TOKEN = import.meta.env.VITE_ADMIN_TOKEN;
  const BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL

  // Fetch doctor data on component mount
  useEffect(() => {
    fetchDoctorData();
  }, [id]);

  const fetchDoctorData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BASE_URL}/api/v1/doctors/${id}`);
      setDoctorData(response.data);
    } catch (error) {
      console.error('Error fetching doctor data:', error);
      message.error('Failed to fetch doctor information');
    } finally {
      setLoading(false);
    }
  };

  const handleEditProfile = () => {
    form.setFieldsValue({
      name: doctorData.name,
      location: doctorData.location
    });
    setEditModalVisible(true);
  };

  const handleUpdateProfile = async (values) => {
    try {
      setUpdating(true);
      const response = await axios.put(
        `${BASE_URL}/api/v1/doctors/${id}?doctor_id=${id}&session_token=${SESSION_TOKEN}`,
        {
          name: values.name,
          location: values.location
        }
      );
      
      // Update local state with new data
      setDoctorData({
        ...doctorData,
        name: values.name,
        location: values.location
      });
      
      setEditModalVisible(false);
      message.success('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      message.error('Failed to update profile');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteProfile = async () => {
    try {
      setDeleting(true);
      await axios.delete(`${BASE_URL}/api/v1/doctors/${id}?doctor_id=${id}&session_token=${SESSION_TOKEN}`);
      message.success('Profile deleted successfully!');
      // You might want to redirect to login or another page after deletion
      // window.location.href = '/login';
    } catch (error) {
      console.error('Error deleting profile:', error);
      message.error('Failed to delete profile');
    } finally {
      setDeleting(false);
    }
  };

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

  if (!doctorData) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Text type="secondary">No doctor data found</Text>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <Title level={2} style={{ 
          color: '#1e293b', 
          marginBottom: '8px',
          fontSize: 'clamp(24px, 4vw, 32px)', 
          fontWeight: '700' 
        }}>
          Profile
        </Title>
        <Text style={{ fontSize: '16px', color: '#64748b', fontWeight: '500' }}>
          Manage your professional information
        </Text>
      </div>

      <Row gutter={[24, 24]}>
        {/* Left Column - Profile Card */}
        <Col xs={24} lg={8}>
          <Card
            bordered={false}
            style={{
              borderRadius: '16px',
              textAlign: 'center',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}
            bodyStyle={{ padding: '32px 24px' }}
          >
            <Avatar
              size={120}
              icon={<UserOutlined />}
              style={{ 
                backgroundColor: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                color: 'white',
                marginBottom: '24px',
                border: '4px solid #dbeafe',
                fontSize: '48px'
              }}
            />
            <Title level={3} style={{ 
              marginBottom: '8px',
              color: '#1e293b',
              fontWeight: '600'
            }}>
              {doctorData.name}
            </Title>
            <Text style={{ 
              fontSize: '16px',
              color: '#64748b',
              display: 'block',
              marginBottom: '24px'
            }}>
              Medical Professional
            </Text>
            
            <Divider style={{ margin: '24px 0' }} />
            
            <div style={{ marginBottom: '24px' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '8px',
                marginBottom: '12px'
              }}>
                <PhoneOutlined style={{ color: '#3b82f6', fontSize: '16px' }} />
                <Text style={{ fontSize: '14px', color: '#64748b' }}>
                  Location: {doctorData.location}
                </Text>
              </div>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '8px'
              }}>
                <UserOutlined style={{ color: '#3b82f6', fontSize: '16px' }} />
                <Text style={{ fontSize: '14px', color: '#64748b' }}>
                  ID: {doctorData.id}
                </Text>
              </div>
            </div>
            
            <Space direction="vertical" style={{ width: '100%' }} size={12}>
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                size="large"
                onClick={handleEditProfile}
                style={{
                  width: '100%',
                  borderRadius: '8px',
                  height: '44px',
                  fontWeight: '600',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  border: 'none',
                  boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
                }}
              >
                Edit Profile
              </Button>
              
              <Popconfirm
                title="Delete Profile"
                description="Are you sure you want to delete this profile? This action cannot be undone."
                onConfirm={handleDeleteProfile}
                okText="Yes, Delete"
                cancelText="Cancel"
                okButtonProps={{ danger: true }}
              >
                <Button 
                  danger
                  icon={<DeleteOutlined />}
                  size="large"
                  loading={deleting}
                  style={{
                    width: '100%',
                    borderRadius: '8px',
                    height: '44px',
                    fontWeight: '600'
                  }}
                >
                  Delete Profile
                </Button>
              </Popconfirm>
            </Space>
          </Card>
        </Col>

        {/* Right Column - Professional Information */}
        <Col xs={24} lg={16}>
          <Card 
            bordered={false}
            style={{
              borderRadius: '16px',
              boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
            }}
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Title level={4} style={{ margin: 0, color: '#1e293b', fontWeight: '600' }}>
                  Professional Information
                </Title>
                <Button 
                  type="text" 
                  icon={<EditOutlined />}
                  onClick={handleEditProfile}
                  style={{
                    color: '#3b82f6',
                    fontWeight: '500'
                  }}
                >
                  Edit
                </Button>
              </div>
            }
            bodyStyle={{ padding: '24px' }}
          >
            <Descriptions 
              column={{ xs: 1, sm: 1, md: 1 }} 
              size="large"
              labelStyle={{ 
                fontWeight: '600', 
                color: '#374151',
                width: '120px'
              }}
              contentStyle={{ 
                color: '#64748b' 
              }}
            >
              <Descriptions.Item label="Full Name">
                {doctorData.name}
              </Descriptions.Item>
              <Descriptions.Item label="Doctor ID">
                {doctorData.id}
              </Descriptions.Item>
              <Descriptions.Item label="Location">
                {doctorData.location}
              </Descriptions.Item>
            </Descriptions>

            <Divider style={{ margin: '32px 0' }} />

            <div>
              <Title level={4} style={{ 
                color: '#1e293b', 
                marginBottom: '16px',
                fontWeight: '600'
              }}>
                About
              </Title>
              <Paragraph style={{ 
                color: '#64748b',
                fontSize: '15px',
                lineHeight: '1.6'
              }}>
                Medical professional providing quality healthcare services. 
                Committed to patient care and maintaining the highest standards 
                of medical practice. Currently serving patients in {doctorData.location}.
              </Paragraph>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Edit Profile Modal */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <EditOutlined style={{ color: '#3b82f6' }} />
            <span>Edit Profile</span>
          </div>
        }
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        footer={null}
        width={500}
        styles={{
          body: { padding: '24px' }
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdateProfile}
          size="large"
        >
          <Form.Item
            label="Full Name"
            name="name"
            rules={[
              { required: true, message: 'Please enter your full name' },
              { min: 2, message: 'Name must be at least 2 characters' }
            ]}
          >
            <Input 
              placeholder="Enter your full name" 
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <Form.Item
            label="Location"
            name="location"
            rules={[
              { required: true, message: 'Please enter your location' },
              { min: 2, message: 'Location must be at least 2 characters' }
            ]}
          >
            <Input 
              placeholder="Enter your location" 
              style={{ borderRadius: '8px' }}
            />
          </Form.Item>

          <div style={{ 
            display: 'flex', 
            justifyContent: 'flex-end', 
            gap: '12px',
            marginTop: '24px' 
          }}>
            <Button 
              onClick={() => setEditModalVisible(false)}
              style={{ borderRadius: '8px' }}
            >
              Cancel
            </Button>
            <Button 
              type="primary" 
              htmlType="submit"
              loading={updating}
              icon={<SaveOutlined />}
              style={{
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                border: 'none',
                boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
              }}
            >
              Save Changes
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default Profile;