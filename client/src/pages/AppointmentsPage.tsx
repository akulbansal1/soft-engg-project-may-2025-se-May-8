import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Container,
  Card,
  CardContent,
  IconButton,
  Fab,
} from '@mui/material';
import { ArrowBack, Add, CalendarToday } from '@mui/icons-material';

const AppointmentsPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', py: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/home')} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          My Appointments
        </Typography>
      </Box>

      {/* Coming Soon Card */}
      <Card sx={{ textAlign: 'center', py: 8 }}>
        <CardContent>
          <CalendarToday sx={{ fontSize: 80, color: '#2196f3', mb: 3 }} />
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
            My Appointments
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
            This feature is coming soon. You'll be able to view and manage your appointments here.
          </Typography>
        </CardContent>
      </Card>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
      >
        <Add />
      </Fab>
    </Container>
  );
};

export default AppointmentsPage;