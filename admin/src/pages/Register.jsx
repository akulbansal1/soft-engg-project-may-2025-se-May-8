import React, { useState } from 'react';
import { Card, Form, Input, Button, Typography, message } from 'antd';

const { Title, Text, Link } = Typography;

const Register = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleRegister = async (values) => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      message.success('Registration successful!');
      console.log('Registered values:', values);
    } catch (error) {
      message.error('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Background dots */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        zIndex: 1
      }} />
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
          }
        `}
      </style>

      {/* Centered Card */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        width: '100%',
        maxWidth: '1100px',
        zIndex: 2,
        padding: '20px',
      }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <Card
            style={{
              borderRadius: '24px',
              border: 'none',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              background: 'rgba(255, 255, 255, 0.95)',
              backdropFilter: 'blur(20px)'
            }}
            bodyStyle={{ padding: 'clamp(32px, 6vw, 48px)' }}
          >
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <Title level={2} style={{
                color: '#1e293b',
                marginBottom: '8px',
                fontSize: 'clamp(24px, 4vw, 32px)',
                fontWeight: '700'
              }}>
                Create Your Account
              </Title>
              <Text style={{
                fontSize: '16px',
                color: '#64748b',
                fontWeight: '500'
              }}>
                Register to access the medical dashboard
              </Text>
            </div>

            <Form
              form={form}
              onFinish={handleRegister}
              layout="vertical"
              size="large"
            >
              <Form.Item
                name="name"
                rules={[{ required: true, message: 'Please enter your name' }]}
              >
                <Input
                  placeholder="Full name (e.g., Dr. A. Kumar)"
                  style={{
                    height: '52px',
                    borderRadius: '12px',
                    border: '2px solid #e2e8f0',
                    fontSize: '16px',
                    backgroundColor: '#ffffff'
                  }}
                />
              </Form.Item>

              <Form.Item
                name="location"
                rules={[{ required: true, message: 'Please enter your location' }]}
              >
                <Input
                  placeholder="Location (e.g., Delhi)"
                  style={{
                    height: '52px',
                    borderRadius: '12px',
                    border: '2px solid #e2e8f0',
                    fontSize: '16px',
                    backgroundColor: '#ffffff'
                  }}
                />
              </Form.Item>

              <Form.Item style={{ marginBottom: '20px' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  style={{
                    height: '52px',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    border: 'none',
                    boxShadow: '0 4px 14px 0 rgba(59, 130, 246, 0.35)'
                  }}
                >
                  {loading ? 'Registering...' : 'Register'}
                </Button>
              </Form.Item>

              <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
                <Text style={{ marginRight: '8px' }}>Already have an account?</Text>
                <Link href="/login" style={{ fontWeight: 600, color: '#2563eb' }}>
                  Login here
                </Link>
              </Form.Item>
            </Form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Register;