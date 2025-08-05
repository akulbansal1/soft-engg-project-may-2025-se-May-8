import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  DatePicker,
  TimePicker,
  Select,
  Button,
  message,
  Spin,
  Typography,
  Space,
  Avatar
} from 'antd';
import { 
  UserOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import axios from 'axios';
import dayjs from 'dayjs';

const { TextArea } = Input;
const { Option } = Select;
const { Text } = Typography;

const NewAppointmentModal = ({ visible, onClose, onSuccess, doctorId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);

  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

  // Fetch users when modal opens
  useEffect(() => {
    if (visible) {
      fetchUsers();
    }
  }, [visible]);

  const fetchUsers = async () => {
    try {
        setUsersLoading(true);
        const response = await fetch(
        `${BACKEND_BASE_URL}/api/v1/users/`,
        {
            method: 'GET',
            credentials: 'include',
        }
        );

        if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setUsers(data);
    } catch (error) {
        console.error('Error fetching users:', error);
        message.error('Failed to fetch patients list');
    } finally {
        setUsersLoading(false);
    }
    };


  const handleSubmit = async (values) => {
  try {
    setLoading(true);

    const appointmentData = {
      name: values.appointmentType,
      date: values.date.format('YYYY-MM-DD'),
      time: values.time.format('HH:mm:ss'),
      notes: values.notes || '',
      user_id: values.patient,
      doctor_id: parseInt(doctorId)
    };

    const response = await fetch(
      `${BACKEND_BASE_URL}/api/v1/appointments/`,
      {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(appointmentData),
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    form.resetFields();
    onSuccess();
  } catch (error) {
    console.error('Error creating appointment:', error);
    message.error('Failed to create appointment. Please try again.');
  } finally {
    setLoading(false);
  }
};

  const handleCancel = () => {
    form.resetFields();
    onClose();
  };

  const appointmentTypes = [
    'Consultation',
    'Check-up',
    'Follow-up',
    'Emergency',
    'Routine',
    'Specialist Visit',
    'Diagnostic Test',
    'Procedure'
  ];

  // Filter for disabled dates (past dates)
  const disabledDate = (current) => {
    return current && current < dayjs().startOf('day');
  };

  // Filter for disabled time slots (past times for today)
  const disabledTime = (current) => {
    const now = dayjs();
    if (current && current.isSame(now, 'day')) {
      return {
        disabledHours: () => {
          const hours = [];
          for (let i = 0; i < now.hour(); i++) {
            hours.push(i);
          }
          return hours;
        },
        disabledMinutes: (selectedHour) => {
          if (selectedHour === now.hour()) {
            const minutes = [];
            for (let i = 0; i <= now.minute(); i++) {
              minutes.push(i);
            }
            return minutes;
          }
          return [];
        }
      };
    }
    return {};
  };

  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <CalendarOutlined style={{ fontSize: '18px', color: 'white' }} />
          </div>
          <div>
            <Text style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              color: '#1e293b',
              display: 'block'
            }}>
              Schedule New Appointment
            </Text>
            <Text style={{ fontSize: '14px', color: '#64748b' }}>
              Create a new appointment for a patient
            </Text>
          </div>
        </div>
      }
      open={visible}
      onCancel={handleCancel}
      footer={null}
      width={600}
      centered
      style={{ borderRadius: '16px' }}
      bodyStyle={{ padding: '24px' }}
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        style={{ marginTop: '20px' }}
      >
        <Form.Item
          name="patient"
          label={
            <span style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
              <UserOutlined style={{ marginRight: '8px', color: '#6b7280' }} />
              Select Patient
            </span>
          }
          rules={[{ required: true, message: 'Please select a patient' }]}
        >
          <Select
            placeholder="Choose a patient"
            loading={usersLoading}
            showSearch
            optionFilterProp="children"
            style={{ height: '48px' }}
            filterOption={(input, option) =>
              option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
            }
          >
            {users.map(user => (
              <Option key={user.id} value={user.id}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Avatar
                    size={24}
                    style={{
                      background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                      fontSize: '12px'
                    }}
                  >
                    {user.name.split(' ').map(n => n[0]).join('')}
                  </Avatar>
                  <div>
                    <Text style={{ fontSize: '14px', fontWeight: '500' }}>
                      {user.name}
                    </Text>
                    <Text style={{ fontSize: '12px', color: '#64748b', marginLeft: '8px' }}>
                      ID: {user.id}
                    </Text>
                  </div>
                </div>
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="appointmentType"
          label={
            <span style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
              <FileTextOutlined style={{ marginRight: '8px', color: '#6b7280' }} />
              Appointment Type
            </span>
          }
          rules={[{ required: true, message: 'Please select appointment type' }]}
        >
          <Select
            placeholder="Select appointment type"
            style={{ height: '48px' }}
          >
            {appointmentTypes.map(type => (
              <Option key={type} value={type}>
                {type}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <div style={{ display: 'flex', gap: '16px' }}>
          <Form.Item
            name="date"
            label={
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
                <CalendarOutlined style={{ marginRight: '8px', color: '#6b7280' }} />
                Date
              </span>
            }
            rules={[{ required: true, message: 'Please select a date' }]}
            style={{ flex: 1 }}
          >
            <DatePicker
              style={{ width: '100%', height: '48px' }}
              disabledDate={disabledDate}
              format="YYYY-MM-DD"
              placeholder="Select date"
            />
          </Form.Item>

          <Form.Item
            name="time"
            label={
              <span style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
                <ClockCircleOutlined style={{ marginRight: '8px', color: '#6b7280' }} />
                Time
              </span>
            }
            rules={[{ required: true, message: 'Please select a time' }]}
            style={{ flex: 1 }}
          >
            <TimePicker
              style={{ width: '100%', height: '48px' }}
              format="HH:mm"
              placeholder="Select time"
              minuteStep={15}
              disabledTime={disabledTime}
            />
          </Form.Item>
        </div>

        <Form.Item
          name="notes"
          label={
            <span style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>
              <FileTextOutlined style={{ marginRight: '8px', color: '#6b7280' }} />
              Notes (Optional)
            </span>
          }
        >
          <TextArea
            placeholder="Add any additional notes or instructions..."
            rows={4}
            style={{ resize: 'none' }}
          />
        </Form.Item>

        <div style={{ 
          display: 'flex', 
          justifyContent: 'flex-end', 
          gap: '12px',
          marginTop: '32px',
          paddingTop: '20px',
          borderTop: '1px solid #f1f5f9'
        }}>
          <Button 
            onClick={handleCancel}
            style={{
              height: '40px',
              padding: '0 20px',
              borderRadius: '8px',
              fontWeight: '500'
            }}
          >
            Cancel
          </Button>
          <Button 
            type="primary" 
            htmlType="submit"
            loading={loading}
            style={{
              height: '40px',
              padding: '0 20px',
              borderRadius: '8px',
              fontWeight: '600',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              border: 'none',
              boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.3)'
            }}
          >
            {loading ? 'Creating...' : 'Create Appointment'}
          </Button>
        </div>
      </Form>
    </Modal>
  );
};

export default NewAppointmentModal;