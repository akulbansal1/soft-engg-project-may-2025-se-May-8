import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Row, Col, Typography, Card, List, Avatar, Tag, Button, Spin, message } from 'antd';
import { 
  CalendarOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  RightOutlined,
  TeamOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const Dashboard = () => {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [upcomingAppointments, setUpcomingAppointments] = useState([]);

  const BACKEND_BASE_URL = 'https://backend-server-production-5c03.up.railway.app';

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch patients
        const patientsResponse = await fetch(`${BACKEND_BASE_URL}/api/v1/users/`, {
          method: 'GET',
          credentials: 'include'
        });
        const patientsData = await patientsResponse.json();
        setPatients(patientsData);
        
        // Fetch appointments (assuming doctor ID is 1 for now, you can get it from params or context)
        const doctorId = id || 1;
        const appointmentsResponse = await fetch(`${BACKEND_BASE_URL}/api/v1/appointments/doctor/${doctorId}`, {
          method: 'GET',
          credentials: 'include'
        });
        const appointmentsData = await appointmentsResponse.json();
        setAppointments(appointmentsData);
        
        // Filter upcoming appointments (after today's date)
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const upcoming = appointmentsData
          .filter(appointment => {
            const appointmentDate = new Date(appointment.date);
            return appointmentDate >= today;
          })
          .sort((a, b) => {
            const dateA = new Date(`${a.date} ${a.time}`);
            const dateB = new Date(`${b.date} ${b.time}`);
            return dateA - dateB;
          })
          .map(appointment => {
            // Find patient details
            const patient = patientsData.find(p => p.id === appointment.user_id);
            return {
              ...appointment,
              patientName: patient ? patient.name : 'Unknown Patient',
              patientPhone: patient ? patient.phone : 'N/A'
            };
          });
        
        setUpcomingAppointments(upcoming);
        
      } catch (error) {
        message.error('Failed to fetch dashboard data');
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
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
          Healthcare Dashboard
        </Title>
        <Text style={{ fontSize: 'clamp(14px, 2vw, 16px)', color: '#64748b', fontWeight: '500' }}>
          Real-time patient monitoring and management
        </Text>
      </div>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12}>
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
              <div style={{ flex: 1, minWidth: 0 }}>
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
                  lineHeight: '1',
                  display: 'block'
                }}>
                  {patients.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <CheckCircleOutlined style={{ color: '#10b981', fontSize: '12px', marginRight: '4px' }} />
                  <Text style={{ fontSize: '12px', color: '#10b981', fontWeight: '600' }}>
                    Active patients registered
                  </Text>
                </div>
              </div>
              <div style={{
                width: 'clamp(48px, 8vw, 60px)',
                height: 'clamp(48px, 8vw, 60px)',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <TeamOutlined style={{ fontSize: 'clamp(20px, 4vw, 28px)', color: 'white' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12}>
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
              <div style={{ flex: 1, minWidth: 0 }}>
                <Text style={{ 
                  fontSize: 'clamp(12px, 2vw, 14px)', 
                  color: '#64748b', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  UPCOMING APPOINTMENTS
                </Text>
                <Text style={{ 
                  fontSize: 'clamp(24px, 5vw, 32px)', 
                  fontWeight: '700', 
                  color: '#1e293b', 
                  lineHeight: '1',
                  display: 'block'
                }}>
                  {upcomingAppointments.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <ClockCircleOutlined style={{ color: '#f59e0b', fontSize: '12px', marginRight: '4px' }} />
                  <Text style={{ fontSize: '12px', color: '#f59e0b', fontWeight: '600' }}>
                    Scheduled appointments
                  </Text>
                </div>
              </div>
              <div style={{
                width: 'clamp(48px, 8vw, 60px)',
                height: 'clamp(48px, 8vw, 60px)',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <CalendarOutlined style={{ fontSize: 'clamp(20px, 4vw, 28px)', color: 'white' }} />
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Upcoming Appointments */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24}>
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                <div>
                  <Text style={{ fontSize: 'clamp(16px, 3vw, 18px)', fontWeight: '700', color: '#1e293b' }}>
                    Upcoming Appointments
                  </Text>
                  <br />
                  <Text style={{ fontSize: 'clamp(12px, 2vw, 14px)', color: '#64748b', fontWeight: '500' }}>
                    All scheduled appointments after today
                  </Text>
                </div>
                <Button type="link" icon={<RightOutlined />} style={{ padding: 0, color: '#3b82f6', flexShrink: 0 }}>
                  View Calendar
                </Button>
              </div>
            }
            style={{
              borderRadius: '16px',
              border: '1px solid #e2e8f0',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              height: '100%',
              display: 'flex',
              flexDirection: 'column'
            }}
            bodyStyle={{ 
              padding: '16px 24px 24px', 
              flex: 1,
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div style={{ 
              flex: 1,
              overflowY: 'auto',
              overflowX: 'hidden',
              paddingRight: '4px',
              marginRight: '-4px'
            }}>
              {upcomingAppointments.length === 0 ? (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '48px 16px',
                  color: '#64748b' 
                }}>
                  <CalendarOutlined style={{ fontSize: '48px', color: '#cbd5e1', marginBottom: '16px' }} />
                  <Text style={{ display: 'block', fontSize: '16px', fontWeight: '500' }}>
                    No upcoming appointments
                  </Text>
                  <Text style={{ fontSize: '14px', color: '#94a3b8' }}>
                    All appointments are up to date
                  </Text>
                </div>
              ) : (
                <List
                  dataSource={upcomingAppointments}
                  split={false}
                  renderItem={(appointment, index) => (
                    <List.Item style={{ 
                      padding: '16px 0', 
                      border: 'none',
                      borderBottom: index < upcomingAppointments.length - 1 ? '1px solid #f1f5f9' : 'none'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'flex-start', width: '100%', gap: '12px' }}>
                        <div style={{
                          width: '60px',
                          height: '60px',
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          border: '1px solid #e2e8f0',
                          flexShrink: 0
                        }}>
                          <Text style={{ fontSize: '12px', fontWeight: '600', color: '#64748b', lineHeight: '1' }}>
                            {formatDate(appointment.date).split(' ')[0]}
                          </Text>
                          <Text style={{ fontSize: '16px', fontWeight: '700', color: '#1e293b', lineHeight: '1', margin: '2px 0' }}>
                            {formatDate(appointment.date).split(' ')[2]}
                          </Text>
                          <Text style={{ fontSize: '11px', color: '#64748b', lineHeight: '1' }}>
                            {formatDate(appointment.date).split(' ')[1]}
                          </Text>
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                            <Text style={{ 
                              fontSize: 'clamp(14px, 2.5vw, 16px)', 
                              fontWeight: '600', 
                              color: '#1e293b'
                            }}>
                              {appointment.patientName}
                            </Text>
                            <Text style={{ fontSize: '13px', color: '#64748b', flexShrink: 0 }}>
                              • {formatTime(appointment.time)}
                            </Text>
                          </div>
                          <Text style={{ 
                            fontSize: '14px', 
                            color: '#3b82f6', 
                            fontWeight: '600',
                            display: 'block', 
                            marginBottom: '6px'
                          }}>
                            {appointment.name}
                          </Text>
                          {appointment.notes && (
                            <Text style={{ 
                              fontSize: '12px', 
                              color: '#64748b', 
                              display: 'block',
                              marginBottom: '8px',
                              fontStyle: 'italic'
                            }}>
                              {appointment.notes}
                            </Text>
                          )}
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px' }}>
                            <Text style={{ fontSize: '12px', color: '#64748b' }}>
                              Phone: {appointment.patientPhone}
                            </Text>
                            <Tag
                              color="#3b82f6"
                              style={{
                                borderRadius: '8px',
                                fontSize: '10px',
                                fontWeight: '600',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                margin: 0,
                                flexShrink: 0
                              }}
                            >
                              SCHEDULED
                            </Tag>
                          </div>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              )}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;