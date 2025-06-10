import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Avatar,
} from '@mui/material';
import MedicalServicesIcon from '@mui/icons-material/MedicalServices';

const WelcomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ 
      minHeight: '100vh',
      width: '100vw',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%)',
        pointerEvents: 'none'
      }
    }}>
      <Box sx={{ 
        textAlign: 'center',
        maxWidth: '600px',
        px: 4,
        position: 'relative',
        zIndex: 1
      }}>
        <Box sx={{ mb: 4 }}>
          <Typography 
            variant="h2" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontWeight: 700, 
              mb: 3,
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            Welcome to HealthCare+
          </Typography>
          
          <Typography 
            variant="h6" 
            sx={{ 
              mb: 4, 
              opacity: 0.9,
              fontSize: { xs: '1.1rem', md: '1.3rem' },
              lineHeight: 1.6,
              maxWidth: '500px',
              margin: '0 auto 2rem auto',
              textShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}
          >
            Your personal health companion. Manage appointments, 
            track medications, and stay connected with your healthcare providers.
          </Typography>
        </Box>

        <Box sx={{ mb: 4 }}>
          <Avatar
            sx={{
              width: 140,
              height: 140,
              margin: '0 auto',
              background: 'rgba(255,255,255,0.15)',
              backdropFilter: 'blur(20px)',
              border: '2px solid rgba(255,255,255,0.2)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              transition: 'transform 0.3s ease',
              '&:hover': {
                transform: 'scale(1.05)'
              }
            }}
          >
            <MedicalServicesIcon sx={{ fontSize: 70, color: 'white' }} />
          </Avatar>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 3,
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/login')}
            sx={{
              backgroundColor: 'rgba(255,255,255,0.2)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255,255,255,0.3)',
              color: 'white',
              minWidth: '200px',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.3)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
              },
              py: 2,
              px: 4,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: '50px',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 15px rgba(0,0,0,0.1)'
            }}
          >
            I'm Already a User
          </Button>
          
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate('/register')}
            sx={{
              borderColor: 'rgba(255,255,255,0.6)',
              color: 'white',
              minWidth: '200px',
              '&:hover': {
                borderColor: 'white',
                backgroundColor: 'rgba(255,255,255,0.1)',
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
                borderWidth: '2px'
              },
              py: 2,
              px: 4,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: '50px',
              transition: 'all 0.3s ease',
              borderWidth: '2px'
            }}
          >
            I'm a New User
          </Button>
        </Box>

        {/* Decorative elements */}
        <Box sx={{
          position: 'absolute',
          top: '10%',
          left: '5%',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.1)',
          backdropFilter: 'blur(10px)',
          animation: 'float 6s ease-in-out infinite',
          '@keyframes float': {
            '0%, 100%': { transform: 'translateY(0px)' },
            '50%': { transform: 'translateY(-20px)' }
          }
        }} />
        
        <Box sx={{
          position: 'absolute',
          top: '60%',
          right: '10%',
          width: '40px',
          height: '40px',
          borderRadius: '50%',
          background: 'rgba(255,255,255,0.08)',
          backdropFilter: 'blur(10px)',
          animation: 'float 4s ease-in-out infinite 2s',
          '@keyframes float': {
            '0%, 100%': { transform: 'translateY(0px)' },
            '50%': { transform: 'translateY(-15px)' }
          }
        }} />
      </Box>
    </Box>
  );
};

export default WelcomePage;