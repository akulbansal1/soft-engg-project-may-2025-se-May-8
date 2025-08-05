import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Button, 
  Space, 
  Typography,
  DatePicker,
  Select,
  Row,
  Col,
  Avatar,
  Badge,
  Divider,
  Input,
  message,
  Spin
} from 'antd';
import { 
  PlusOutlined, 
  CalendarOutlined,
  MoreOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckOutlined,
  ClockCircleOutlined,
  UserOutlined,
  FileTextOutlined,
  FilterOutlined,
  SearchOutlined,
  ArrowRightOutlined,
  MedicineBoxOutlined,
  HistoryOutlined
} from '@ant-design/icons';
import { useParams } from 'react-router-dom';
import dayjs from 'dayjs';
import axios from 'axios';
import NewAppointmentModal from './NewAppointmentModal';
import PrescriptionModal from './PrescriptionModal';
import MedicinesModal from './MedicinesModal';

const { Title, Text } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Appointments = () => {
  const { id } = useParams(); 
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchText, setSearchText] = useState('');
  const [dateRange, setDateRange] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [isPrescriptionModalVisible, setIsPrescriptionModalVisible] = useState(false);
  const [isMedicinesModalVisible, setIsMedicinesModalVisible] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);

  const BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL

  // Fetch appointments on component mount
  useEffect(() => {
    fetchAppointments();
  }, [id]);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BASE_URL}/api/v1/appointments/doctor/${id}`
      );
      
      // Transform the API data to match the component's expected format
      const transformedAppointments = response.data.map(apt => ({
        id: apt.id,
        patientName: `Patient ${apt.user_id}`, // We'll need to fetch user details separately
        date: dayjs(apt.date).format('MM/DD/YYYY'),
        time: dayjs(apt.time, 'HH:mm:ss').format('hh:mm A'),
        type: apt.name,
        duration: '30 min', 
        status: 'Scheduled',
        notes: apt.notes,
        user_id: apt.user_id,
        doctor_id: apt.doctor_id,
        medicines: apt.medicines
      }));
      
      setAppointments(transformedAppointments);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      message.error('Failed to fetch appointments');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Scheduled': '#3b82f6',
      'Confirmed': '#10b981',
      'Pending': '#f59e0b',
      'Cancelled': '#ef4444',
      'Completed': '#8b5cf6'
    };
    return colors[status] || '#64748b';
  };

  const getTypeColor = (type) => {
    const colors = {
      'Consultation': '#06b6d4',
      'Check-up': '#10b981',
      'Follow-up': '#3b82f6',
      'Emergency': '#ef4444',
      'Routine': '#8b5cf6'
    };
    return colors[type] || '#64748b';
  };

  const handlePrescribe = (record) => {
    setSelectedPatient(record);
    setIsPrescriptionModalVisible(true);
  };

  const handleViewMedicines = (record) => {
    setSelectedPatient(record);
    setIsMedicinesModalVisible(true);
  };

  const columns = [
    {
      title: 'Patient',
      dataIndex: 'patientName',
      key: 'patientName',
      render: (name, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Avatar
            size={40}
            style={{
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            {name.split(' ').map(n => n[0]).join('')}
          </Avatar>
          <div>
            <Text style={{ 
              fontSize: '15px', 
              fontWeight: '600', 
              color: '#1e293b',
              display: 'block'
            }}>
              {name}
            </Text>
            <Text style={{ fontSize: '13px', color: '#64748b' }}>
              ID: {record.user_id}
            </Text>
          </div>
        </div>
      ),
    },
    {
      title: 'Date & Time',
      key: 'datetime',
      render: (_, record) => (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <CalendarOutlined style={{ fontSize: '12px', color: '#64748b' }} />
            <Text style={{ 
              fontSize: '14px', 
              fontWeight: '600', 
              color: '#1e293b'
            }}>
              {record.date}
            </Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ClockCircleOutlined style={{ fontSize: '12px', color: '#64748b' }} />
            <Text style={{ fontSize: '13px', color: '#64748b' }}>
              {record.time}
            </Text>
          </div>
        </div>
      ),
      sorter: (a, b) => new Date(a.date) - new Date(b.date),
    },
    {
      title: 'Appointment Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => (
        <Tag
          color={getTypeColor(type)}
          style={{
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: '600',
            padding: '4px 12px',
            border: 'none'
          }}
        >
          {type}
        </Tag>
      ),
      filters: [
        { text: 'Consultation', value: 'Consultation' },
        { text: 'Check-up', value: 'Check-up' },
        { text: 'Follow-up', value: 'Follow-up' },
        { text: 'Emergency', value: 'Emergency' },
      ],
      onFilter: (value, record) => record.type === value,
    },
    {
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      render: (duration) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ClockCircleOutlined style={{ fontSize: '12px', color: '#64748b' }} />
          <Text style={{ fontSize: '14px', color: '#1e293b', fontWeight: '500' }}>
            {duration}
          </Text>
        </div>
      ),
      sorter: (a, b) => parseInt(a.duration) - parseInt(b.duration),
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
      filters: [
        { text: 'Scheduled', value: 'Scheduled' },
        { text: 'Confirmed', value: 'Confirmed' },
        { text: 'Pending', value: 'Pending' },
        { text: 'Cancelled', value: 'Cancelled' },
        { text: 'Completed', value: 'Completed' },
      ],
      onFilter: (value, record) => record.status === value,
    },
    {
      title: 'Notes',
      dataIndex: 'notes',
      key: 'notes',
      render: (notes) => (
        <div style={{ 
          maxWidth: '200px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          <Text style={{ fontSize: '13px', color: '#64748b' }}>
            {notes || 'No notes'}
          </Text>
        </div>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="primary"
            icon={<MedicineBoxOutlined />}
            onClick={() => handlePrescribe(record)}
            style={{
              borderRadius: '8px',
              height: '36px',
              padding: '0 12px',
              fontWeight: '600',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              border: 'none',
              boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)',
              fontSize: '12px'
            }}
          >
            Prescribe
          </Button>
          <Button 
            icon={<HistoryOutlined />}
            onClick={() => handleViewMedicines(record)}
            style={{
              borderRadius: '8px',
              height: '36px',
              padding: '0 12px',
              fontWeight: '600',
              background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
              color: 'white',
              border: 'none',
              boxShadow: '0 2px 8px rgba(99, 102, 241, 0.3)',
              fontSize: '12px'
            }}
          >
            Medicines
          </Button>
        </Space>
      ),
    },
  ];

  const filteredAppointments = appointments.filter(apt => {
    const matchesStatus = statusFilter === 'all' || apt.status.toLowerCase() === statusFilter;
    const matchesSearch = apt.patientName.toLowerCase().includes(searchText.toLowerCase()) || 
                         apt.notes?.toLowerCase().includes(searchText.toLowerCase());
    const matchesDate = dateRange.length === 0 || 
                       (new Date(apt.date) >= new Date(dateRange[0]) && 
                        new Date(apt.date) <= new Date(dateRange[1]));
    
    return matchesStatus && matchesSearch && matchesDate;
  });

  const todayAppointments = appointments.filter(apt => 
    apt.date === dayjs().format('MM/DD/YYYY')
  );
  const upcomingAppointments = appointments.filter(apt => 
    apt.status === 'Scheduled' || apt.status === 'Confirmed'
  );
  const pendingAppointments = appointments.filter(apt => 
    apt.status === 'Pending'
  );
  const completedAppointments = appointments.filter(apt => 
    apt.status === 'Completed'
  );

  const handleNewAppointment = () => {
    setIsModalVisible(true);
  };

  const handleModalClose = () => {
    setIsModalVisible(false);
  };

  const handleAppointmentCreated = () => {
    fetchAppointments(); // Refresh the appointments list
    setIsModalVisible(false);
    message.success('Appointment created successfully!');
  };

  const handlePrescriptionModalClose = () => {
    setIsPrescriptionModalVisible(false);
    setSelectedPatient(null);
  };

  const handleMedicinesModalClose = () => {
    setIsMedicinesModalVisible(false);
    setSelectedPatient(null);
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

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 16px' }}>
      {/* Header Section */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <Title level={2} style={{ 
              color: '#1e293b', 
              marginBottom: '8px', 
              fontSize: 'clamp(24px, 4vw, 32px)', 
              fontWeight: '700' 
            }}>
              Appointment Scheduler
            </Title>
            <Text style={{ fontSize: 'clamp(14px, 2vw, 16px)', color: '#64748b', fontWeight: '500' }}>
              Manage your appointment schedule and patient bookings
            </Text>
          </div>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            size="large"
            onClick={handleNewAppointment}
            style={{
              borderRadius: '8px',
              height: '48px',
              padding: '0 24px',
              fontWeight: '600',
              boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              border: 'none'
            }}
          >
            New Appointment
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card
            bordered={false}
            style={{
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: '14px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  TODAY'S APPOINTMENTS
                </Text>
                <Text style={{ 
                  fontSize: '28px', 
                  fontWeight: '700', 
                  color: '#075985', 
                  lineHeight: '1'
                }}>
                  {todayAppointments.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <Text style={{ fontSize: '12px', color: '#0369a1', marginRight: '4px' }}>
                    {todayAppointments.filter(a => a.status === 'Confirmed').length} confirmed
                  </Text>
                </div>
              </div>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(14, 165, 233, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <CalendarOutlined style={{ fontSize: '20px', color: '#0369a1' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card
            bordered={false}
            style={{
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: '14px', 
                  color: '#047857', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  UPCOMING
                </Text>
                <Text style={{ 
                  fontSize: '28px', 
                  fontWeight: '700', 
                  color: '#065f46', 
                  lineHeight: '1'
                }}>
                  {upcomingAppointments.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <ArrowRightOutlined style={{ fontSize: '12px', color: '#059669', marginRight: '4px' }} />
                  <Text style={{ fontSize: '12px', color: '#047857' }}>
                    Next: {upcomingAppointments[0]?.date || 'None'}
                  </Text>
                </div>
              </div>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(16, 185, 129, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <ClockCircleOutlined style={{ fontSize: '20px', color: '#059669' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card
            bordered={false}
            style={{
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: '14px', 
                  color: '#92400e', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  PENDING CONFIRMATION
                </Text>
                <Text style={{ 
                  fontSize: '28px', 
                  fontWeight: '700', 
                  color: '#854d0e', 
                  lineHeight: '1'
                }}>
                  {pendingAppointments.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <Text style={{ fontSize: '12px', color: '#92400e' }}>
                    Needs your attention
                  </Text>
                </div>
              </div>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(245, 158, 11, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <ClockCircleOutlined style={{ fontSize: '20px', color: '#b45309' }} />
              </div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} md={6}>
          <Card
            bordered={false}
            style={{
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)',
              height: '100%'
            }}
            bodyStyle={{ padding: '16px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ flex: 1 }}>
                <Text style={{ 
                  fontSize: '14px', 
                  color: '#6d28d9', 
                  fontWeight: '600', 
                  display: 'block', 
                  marginBottom: '8px' 
                }}>
                  COMPLETED
                </Text>
                <Text style={{ 
                  fontSize: '28px', 
                  fontWeight: '700', 
                  color: '#5b21b6', 
                  lineHeight: '1'
                }}>
                  {completedAppointments.length}
                </Text>
                <div style={{ display: 'flex', alignItems: 'center', marginTop: '8px' }}>
                  <Text style={{ fontSize: '12px', color: '#6d28d9' }}>
                    This month
                  </Text>
                </div>
              </div>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(139, 92, 246, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <CheckOutlined style={{ fontSize: '20px', color: '#6d28d9' }} />
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Main Table Card */}
      <Card
        bordered={false}
        style={{
          borderRadius: '16px',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
          marginBottom: '24px'
        }}
        bodyStyle={{ padding: 0 }}
      >
        <div style={{ 
          padding: '24px', 
          borderBottom: '1px solid #f1f5f9',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <Title level={4} style={{ 
              color: '#1e293b', 
              margin: 0,
              fontSize: '18px',
              fontWeight: '600'
            }}>
              All Appointments
            </Title>
            <Text style={{ fontSize: '14px', color: '#64748b' }}>
              {filteredAppointments.length} appointments found
            </Text>
          </div>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            <Input
              placeholder="Search patients or notes..."
              prefix={<SearchOutlined style={{ color: '#94a3b8' }} />}
              style={{ 
                width: '240px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0'
              }}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
            
            <RangePicker
              style={{ 
                width: '240px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0'
              }}
              onChange={(dates) => setDateRange(dates ? dates.map(d => d.format('MM/DD/YYYY')) : [])}
            />
            
            <Select
              placeholder="Filter by status"
              style={{ 
                width: '160px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0'
              }}
              value={statusFilter}
              onChange={setStatusFilter}
              suffixIcon={<FilterOutlined style={{ color: '#94a3b8' }} />}
            >
              <Option value="all">All Status</Option>
              <Option value="scheduled">Scheduled</Option>
              <Option value="confirmed">Confirmed</Option>
              <Option value="pending">Pending</Option>
              <Option value="completed">Completed</Option>
              <Option value="cancelled">Cancelled</Option>
            </Select>
          </div>
        </div>

        <Table
          columns={columns}
          dataSource={filteredAppointments}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => (
              <Text style={{ color: '#64748b' }}>
                Showing {range[0]}-{range[1]} of {total} appointments
              </Text>
            ),
            style: { padding: '0 24px 16px' }
          }}
          style={{ width: '100%' }}
          scroll={{ x: 'max-content' }}
        />
      </Card>

      {/* New Appointment Modal */}
      <NewAppointmentModal
        visible={isModalVisible}
        onClose={handleModalClose}
        onSuccess={handleAppointmentCreated}
        doctorId={id}
      />

      {/* Prescription Modal */}
      <PrescriptionModal
        visible={isPrescriptionModalVisible}
        onClose={handlePrescriptionModalClose}
        patientName={selectedPatient?.patientName}
        appointmentId={selectedPatient?.id}
        userId={selectedPatient?.user_id}
        doctorId={id}
      />

      {/* Medicines Modal */}
      <MedicinesModal
        visible={isMedicinesModalVisible}
        onClose={handleMedicinesModalClose}
        patientName={selectedPatient?.patientName}
        appointmentId={selectedPatient?.id}
        userId={selectedPatient?.user_id}
        doctorId={id}
      />
    </div>
  );
};

export default Appointments;