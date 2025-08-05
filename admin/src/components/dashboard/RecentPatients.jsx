import React from 'react';
import { Card, List, Avatar, Tag, Typography } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { mockPatients } from '../../data/mockData';

const { Text } = Typography;

const RecentPatients = () => {
  const recentPatients = mockPatients.slice(0, 5);

  return (
    <Card 
      title="Recent Patients" 
      className="dashboard-card"
      extra={<Text className="text-blue-500 cursor-pointer hover:underline">View All</Text>}
    >
      <List
        itemLayout="horizontal"
        dataSource={recentPatients}
        renderItem={(patient) => (
          <List.Item className="hover:bg-gray-50 rounded-lg px-2 transition-colors">
            <List.Item.Meta
              avatar={
                <Avatar
                  size="large"
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#f0f0f0', color: '#555' }}
                />
              }
              title={
                <div className="flex justify-between items-center">
                  <Text strong>{patient.name}</Text>
                  <Tag color={patient.status === 'Active' ? 'green' : 'orange'}>
                    {patient.status}
                  </Tag>
                </div>
              }
              description={
                <div>
                  <Text type="secondary">{patient.condition}</Text>
                  <br />
                  <Text type="secondary" className="text-xs">
                    Last visit: {patient.lastVisit}
                  </Text>
                </div>
              }
            />
          </List.Item>
        )}
      />
    </Card>
  );
};

export default RecentPatients;
