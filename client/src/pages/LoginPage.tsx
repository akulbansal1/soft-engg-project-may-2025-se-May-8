import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  IconButton,
  Alert,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!phone || phone.length < 10) {
      setError('Please enter a valid phone number');
      return;
    }

    try {
      // Mock API call - check if user exists
      const response = await fetch(`http://localhost:3001/users?phone=%2B${phone}`);
      const users = await response.json();
      
      if (users.length === 0) {
        setError('Phone number not registered. Please sign up first.');
        return;
      }

      // Navigate to OTP page with phone number
      navigate('/otp', { state: { phone: `+${phone}`, isLogin: true } });
    } catch (err) {
      setError('Something went wrong. Please try again.');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', py: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={() => navigate('/')} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h6">Sign In</Typography>
      </Box>

      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            component="h1" 
            gutterBottom 
            sx={{ textAlign: 'center', mb: 3 }}
          >
            Welcome Back
          </Typography>

          <Typography 
            variant="body2" 
            color="textSecondary" 
            sx={{ textAlign: 'center', mb: 4 }}
          >
            Enter your registered phone number to continue
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
              Phone Number
            </Typography>
            <PhoneInput
              country={'in'}
              value={phone}
              onChange={(value) => {
                setPhone(value);
                setError('');
              }}
              inputStyle={{
                width: '100%',
                height: '56px',
                fontSize: '16px',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                paddingLeft: '60px',
              }}
              containerStyle={{
                width: '100%',
              }}
              buttonStyle={{
                border: '1px solid #e0e0e0',
                borderRadius: '8px 0 0 8px',
              }}
            />
          </Box>

          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={handleLogin}
            sx={{ mb: 2 }}
          >
            Continue
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              Don't have an account?{' '}
              <Button 
                variant="text" 
                onClick={() => navigate('/register')}
                sx={{ textTransform: 'none', p: 0 }}
              >
                Sign up here
              </Button>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default LoginPage;