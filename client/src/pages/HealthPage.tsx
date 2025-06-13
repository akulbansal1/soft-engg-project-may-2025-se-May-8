import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { HeartPulse, Droplets, Activity } from 'lucide-react';

const HealthPage: React.FC = () => {
  return (
    <div className="h-full min-h-[calc(100dvh-110px)] ">
      <div>
        <h2 className="text-xl font-bold mb-5">Health Dashboard</h2>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <Card>
          <CardHeader className="flex flex-col items-center text-center">
            <HeartPulse className="h-6 w-6 text-red-500 mb-2" />
            <CardTitle>Heart Rate</CardTitle>
            <CardDescription>78 bpm</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={78} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-col items-center text-center">
            <Droplets className="h-6 w-6 text-blue-500 mb-2" />
            <CardTitle>Oxygen Level</CardTitle>
            <CardDescription>97%</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={97} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-col items-center text-center">
            <Activity className="h-6 w-6 text-green-600 mb-2" />
            <CardTitle>Blood Pressure</CardTitle>
            <CardDescription>120/80</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={60} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default HealthPage;

