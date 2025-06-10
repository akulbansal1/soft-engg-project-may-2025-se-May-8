import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  TextField,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';

interface LocationState {
  phone: string;
  isLogin: boolean;
}

const OTPPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { phone, isLogin } = (location.state as LocationState) || {};
  
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [countdown, setCountdown] = useState(30);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    if (!phone) {
      navigate('/');
      return;
    }

    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          setCanResend(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [phone, navigate]);

  const handleOTPChange = (value: string) => {
    if (value.length <= 6 && /^\d*$/.test(value)) {
      setOtp(value);
      setError('');
    }
  };

  const verifyOTP = async () => {
    if (otp.length !== 6) {
      setError('Please enter a 6-digit OTP');
      return;
    }

    setLoading(true);
    try {
      // Mock OTP verification - in real app, this would be an API call
      // For demo purposes, accept any 6-digit OTP
      await new Promise(resolve => setTimeout(resolve, 1500));

      if (isLogin) {
        // For existing users, go directly to face ID
        navigate('/face-id', { state: { phone, isLogin: true } });
      } else {
        // For new users, complete registration first
        const registrationData = localStorage.getItem('registrationData');
        if (registrationData) {
          const userData = JSON.parse(registrationData);
          
          // Create user in mock database
          const response = await fetch('http://localhost:3001/users', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              ...userData,
              isRegistered: true,
              id: Date.now(), // Mock ID generation
            }),
          });

          if (response.ok) {
            localStorage.removeItem('registrationData');
            navigate('/face-id', { state: { phone, isLogin: false } });
          } else {
            throw new Error('Registration failed');
          }
        }
      }
    } catch (err) {
      setError('Invalid OTP. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resendOTP = async () => {
    setCanResend(false);
    setCountdown(30);
    setError('');
    
    // Mock resend OTP
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      // In real app, make API call to resend OTP
    } catch (err) {
      setError('Failed to resend OTP. Please try again.');
    }
  };

  const maskedPhone = phone ? phone.replace(/(\+\d{2})(\d{4})(\d+)/, '$1****$3') : '';

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', py: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={() => navigate(-1)} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h6">Verify Phone</Typography>
      </Box>

      <Card>
        <CardContent sx={{ p: 3, textAlign: 'center' }}>
          <Typography 
            variant="h5" 
            component="h1" 
            gutterBottom 
            sx={{ mb: 3 }}
          >
            Enter OTP
          </Typography>

          <Typography 
            variant="body2" 
            color="textSecondary" 
            sx={{ mb: 4 }}
          >
            We've sent a 6-digit verification code to
            <br />
            <strong>{maskedPhone}</strong>
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <TextField
            value={otp}
            onChange={(e) => handleOTPChange(e.target.value)}
            placeholder="Enter 6-digit OTP"
            inputProps={{
              style: {
                textAlign: 'center',
                fontSize: '1.5rem',
                letterSpacing: '0.5rem',
              },
              maxLength: 6,
            }}
            sx={{
              mb: 3,
              '& .MuiOutlinedInput-root': {
                height: '60px',
              },
            }}
            fullWidth
          />

          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={verifyOTP}
            disabled={loading || otp.length !== 6}
            sx={{ mb: 3 }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : 'Verify OTP'}
          </Button>

          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              Didn't receive the code?{' '}
            </Typography>
            {canResend ? (
              <Button 
                variant="text" 
                onClick={resendOTP}
                sx={{ textTransform: 'none', p: 0, ml: 0.5 }}
              >
                Resend OTP
              </Button>
            ) : (
              <Typography variant="body2" color="primary" sx={{ ml: 0.5 }}>
                Resend in {countdown}s
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default OTPPage;