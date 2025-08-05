import React, { useState, useEffect } from 'react';
import {
  Modal,
  Card,
  Typography,
  Space,
  Avatar,
  Divider,
  Tag,
  List,
  Empty,
  Spin,
  message,
  Alert
} from 'antd';
import { 
  MedicineBoxOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  UserOutlined,
  CheckCircleOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const MedicinesModal = ({ visible, onClose, patientName, appointmentId, userId, doctorId }) => {
  const [medicines, setMedicines] = useState([]);
  const [loading, setLoading] = useState(false);

  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

  useEffect(() => {
    if (visible && userId) {
      fetchMedicines();
    }
  }, [visible, userId]);

  const fetchMedicines = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${BACKEND_BASE_URL}/api/v1/medicines/user/${userId}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMedicines(data);
    } catch (error) {
      console.error('Error fetching medicines:', error);
      message.error('Failed to fetch patient medicines');
    } finally {
      setLoading(false);
    }
  };

  const currentAppointmentMedicines = medicines.filter(
    medicine => medicine.appointment_id === appointmentId
  );

  const otherMedicines = medicines.filter(
    medicine => medicine.appointment_id !== appointmentId
  );

  const getMedicineStatus = (medicine) => {
    const today = dayjs();
    const startDate = dayjs(medicine.start_date);
    const endDate = dayjs(medicine.end_date);

    if (today.isBefore(startDate)) {
      return { status: 'upcoming', color: '#3b82f6', text: 'Upcoming' };
    } else if (today.isAfter(endDate)) {
      return { status: 'completed', color: '#10b981', text: 'Completed' };
    } else {
      return { status: 'active', color: '#f59e0b', text: 'Active' };
    }
  };

  const formatDateRange = (startDate, endDate) => {
    const start = dayjs(startDate);
    const end = dayjs(endDate);
    return `${start.format('MMM DD')} - ${end.format('MMM DD, YYYY')}`;
  };

  const MedicineCard = ({ medicine, isCurrentAppointment = false }) => {
    const medicineStatus = getMedicineStatus(medicine);
    
    return (
      <Card
        size="small"
        style={{
          marginBottom: '12px',
          borderRadius: '12px',
          border: isCurrentAppointment ? '2px solid #3b82f6' : '1px solid #e2e8f0',
          background: isCurrentAppointment ? '#f8faff' : 'white',
          boxShadow: isCurrentAppointment ? '0 4px 12px rgba(59, 130, 246, 0.15)' : '0 1px 3px rgba(0, 0, 0, 0.1)'
        }}
        bodyStyle={{ padding: '16px' }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <MedicineBoxOutlined style={{ 
                fontSize: '16px', 
                color: isCurrentAppointment ? '#3b82f6' : '#64748b' 
              }} />
              <Text style={{ 
                fontSize: '16px', 
                fontWeight: '600', 
                color: '#1e293b' 
              }}>
                {medicine.name}
              </Text>
              <Tag
                color={medicineStatus.color}
                style={{
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: '600',
                  padding: '2px 8px',
                  border: 'none'
                }}
              >
                {medicineStatus.text}
              </Tag>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Text style={{ fontSize: '13px', color: '#64748b', minWidth: '60px' }}>
                    Dosage:
                  </Text>
                  <Text style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
                    {medicine.dosage}
                  </Text>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Text style={{ fontSize: '13px', color: '#64748b', minWidth: '60px' }}>
                    Frequency:
                  </Text>
                  <Text style={{ fontSize: '14px', fontWeight: '500', color: '#374151' }}>
                    {medicine.frequency}
                  </Text>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CalendarOutlined style={{ fontSize: '12px', color: '#64748b' }} />
                  <Text style={{ fontSize: '13px', color: '#64748b' }}>
                    {formatDateRange(medicine.start_date, medicine.end_date)}
                  </Text>
                </div>
              </Space>
            </div>

            {medicine.notes && (
              <div style={{ 
                padding: '8px 12px', 
                background: '#f8fafc', 
                borderRadius: '8px',
                marginTop: '8px'
              }}>
                <Text style={{ fontSize: '13px', color: '#64748b', fontStyle: 'italic' }}>
                  Note: {medicine.notes}
                </Text>
              </div>
            )}
          </div>
        </div>
      </Card>
    );
  };

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <MedicineBoxOutlined style={{ fontSize: '18px', color: 'white' }} />
          </div>
          <div>
            <Text style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              color: '#1e293b',
              display: 'block'
            }}>
              Patient Medicines
            </Text>
            <Text style={{ fontSize: '14px', color: '#64748b' }}>
              {patientName} - Medicine history and prescriptions
            </Text>
          </div>
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      centered
      style={{ borderRadius: '16px' }}
      bodyStyle={{ padding: '24px', maxHeight: '70vh', overflowY: 'auto' }}
    >
      {loading ? (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: '300px' 
        }}>
          <Spin size="large" />
        </div>
      ) : (
        <div>
          {/* Patient Info Header */}
          <Card
            style={{
              background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
              border: 'none',
              borderRadius: '12px',
              marginBottom: '24px'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Avatar
                size={48}
                style={{
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  fontSize: '16px',
                  fontWeight: '600'
                }}
              >
                {patientName?.split(' ').map(n => n[0]).join('') || 'P'}
              </Avatar>
              <div>
                <Text style={{ 
                  fontSize: '16px', 
                  fontWeight: '600', 
                  color: '#1e293b',
                  display: 'block'
                }}>
                  {patientName}
                </Text>
                <Text style={{ fontSize: '14px', color: '#64748b' }}>
                  Total Medicines: {medicines.length} | Active: {
                    medicines.filter(m => getMedicineStatus(m).status === 'active').length
                  }
                </Text>
              </div>
            </div>
          </Card>

          {medicines.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <span style={{ color: '#64748b' }}>
                  No medicines prescribed for this patient yet
                </span>
              }
            />
          ) : (
            <>
              {/* Current Appointment Medicines */}
              {currentAppointmentMedicines.length > 0 && (
                <div style={{ marginBottom: '32px' }}>
                  <Alert
                    message={
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <CheckCircleOutlined />
                        <Text style={{ fontWeight: '600' }}>
                          For This Appointment
                        </Text>
                      </div>
                    }
                    description={`You have prescribed ${currentAppointmentMedicines.length} medicine(s) for this appointment`}
                    type="info"
                    showIcon={false}
                    style={{
                      marginBottom: '16px',
                      borderRadius: '8px',
                      background: 'linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%)',
                      border: '1px solid #93c5fd'
                    }}
                  />
                  
                  <div>
                    {currentAppointmentMedicines.map((medicine) => (
                      <MedicineCard 
                        key={medicine.id} 
                        medicine={medicine} 
                        isCurrentAppointment={true}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Medicine History */}
              {otherMedicines.length > 0 && (
                <div>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '8px', 
                    marginBottom: '16px' 
                  }}>
                    <HistoryOutlined style={{ fontSize: '16px', color: '#64748b' }} />
                    <Title level={5} style={{ 
                      margin: 0, 
                      color: '#374151',
                      fontSize: '16px',
                      fontWeight: '600'
                    }}>
                      Medicine History
                    </Title>
                    <Text style={{ fontSize: '13px', color: '#64748b' }}>
                      ({otherMedicines.length} previous prescriptions)
                    </Text>
                  </div>

                  <Divider style={{ margin: '12px 0' }} />

                  <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                    {otherMedicines
                      .sort((a, b) => new Date(b.start_date) - new Date(a.start_date))
                      .map((medicine) => (
                        <MedicineCard key={medicine.id} medicine={medicine} />
                      ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </Modal>
  );
};

export default MedicinesModal;