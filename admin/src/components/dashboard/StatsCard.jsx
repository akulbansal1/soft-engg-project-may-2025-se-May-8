import React from 'react';
import { Card, Statistic } from 'antd';

const StatsCard = ({ title, value, icon, color, suffix }) => {
  return (
    <Card className="dashboard-card hover:scale-105 transition-transform duration-300">
      <div className="flex items-center justify-between">
        <div>
          <Statistic
            title={<span className="text-gray-600 font-medium">{title}</span>}
            value={value}
            suffix={suffix}
            valueStyle={{ 
              color: color,
              fontSize: '2rem',
              fontWeight: 'bold'
            }}
          />
        </div>
        <div 
          className="text-4xl p-4 rounded-full"
          style={{ backgroundColor: `${color}15`, color: color }}
        >
          {icon}
        </div>
      </div>
    </Card>
  );
};

export default StatsCard;