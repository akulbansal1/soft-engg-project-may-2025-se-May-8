import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  Grid,
  Avatar,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Emergency,
  CalendarToday,
  Favorite,
  Medication,
  Person,
  Settings,
  Notifications,
} from '@mui/icons-material';

interface MenuItemProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  onClick: () => void;
  color: string;
}

const MenuItem: React.FC<MenuItemProps> = ({ icon, title, subtitle, onClick, color }) => (
  <Card 
    onClick={onClick}
    sx={{ 
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
      },
      height: '100%',
    }}
  >
    <CardContent sx={{ p: 2.5, textAlign: 'center' }}>
      <Avatar
        sx={{
          width: 56,
          height: 56,
          backgroundColor: color,
          margin: '0 auto',
          mb: 2,
        }}
      >
        {icon}
      </Avatar>
      <Typography variant="h6" component="h3" gutterBottom sx={{ fontWeight: 600 }}>
        {title}
      </Typography>
      <Typography variant="body2" color="textSecondary">
        {subtitle}
      </Typography>
    </CardContent>
  </Card>
);

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const menuItems = [
    {
      icon: <Emergency />,
      title: 'Emergency Contact',
      subtitle: 'Quick access to emergency contacts',
      onClick: () => navigate('/emergency-contacts'),
      color: '#f44336',
    },
    {
      icon: <CalendarToday />,
      title: 'My Appointments',
      subtitle: 'View and manage appointments',
      onClick: () => navigate('/appointments'),
      color: '#2196f3',
    },
    {
      icon: <Favorite />,
      title: 'My Health',
      subtitle: 'Track your health metrics',
      onClick: () => navigate('/health'),
      color: '#4caf50',
    },
    {
      icon: <Medication />,
      title: 'My Medicines',
      subtitle: 'Manage your medications',
      onClick: () => navigate('/medicines'),
      color: '#ff9800',
    },
  ];

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', py: 2 }}>
      {/* Header */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar sx={{ mr: 2, bgcolor: 'rgba(255,255,255,0.2)' }}>
                <Person />
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  Good Morning!
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                  John Doe
                </Typography>
              </Box>
            </Box>
            <Box>
              <IconButton sx={{ color: 'white', mr: 1 }}>
                <Notifications />
              </IconButton>
              <IconButton sx={{ color: 'white' }}>
                <Settings />
              </IconButton>
            </Box>
          </Box>
          
          <Divider sx={{ borderColor: 'rgba(255,255,255,0.2)', mb: 2 }} />
          
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.9)' }}>
            How can we help you today?
          </Typography>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h5" color="primary" sx={{ fontWeight: 600 }}>
              3
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Upcoming
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h5" color="success.main" sx={{ fontWeight: 600 }}>
              2
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Medicines
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card sx={{ textAlign: 'center', p: 2 }}>
            <Typography variant="h5" color="warning.main" sx={{ fontWeight: 600 }}>
              1
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Alert
            </Typography>
          </Card>
        </Grid>
      </Grid>

      {/* Main Menu */}
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Quick Access
      </Typography>
      
      <Grid container spacing={2}>
        {menuItems.map((item, index) => (
          <Grid item xs={6} key={index}>
            <MenuItem
              icon={item.icon}
              title={item.title}
              subtitle={item.subtitle}
              onClick={item.onClick}
              color={item.color}
            />
          </Grid>
        ))}
      </Grid>

      {/* Recent Activity */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
            Recent Activity
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: '#4caf50', mr: 2, width: 32, height: 32 }}>
              <Favorite sx={{ fontSize: 18 }} />
            </Avatar>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Blood pressure recorded
              </Typography>
              <Typography variant="caption" color="textSecondary">
                2 hours ago
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: '#2196f3', mr: 2, width: 32, height: 32 }}>
              <CalendarToday sx={{ fontSize: 18 }} />
            </Avatar>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Appointment scheduled
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Yesterday
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Avatar sx={{ bgcolor: '#ff9800', mr: 2, width: 32, height: 32 }}>
              <Medication sx={{ fontSize: 18 }} />
            </Avatar>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Medicine reminder set
              </Typography>
              <Typography variant="caption" color="textSecondary">
                2 days ago
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default HomePage;