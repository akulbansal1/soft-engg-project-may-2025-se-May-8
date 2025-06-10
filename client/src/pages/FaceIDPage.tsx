import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Container,
  Card,
  CardContent,
  IconButton,
  Alert,
  CircularProgress,
  Avatar,
} from '@mui/material';
import { ArrowBack, FaceRetouchingNatural } from '@mui/icons-material';

interface LocationState {
  phone: string;
  isLogin: boolean;
}

const FaceIDPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { phone, isLogin } = (location.state as LocationState) || {};
  
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState<'ready' | 'scanning' | 'complete'>('ready');

  useEffect(() => {
    if (!phone) {
      navigate('/');
      return;
    }
  }, [phone, navigate]);

  const startFaceScan = async () => {
    setScanning(true);
    setError('');
    setStep('scanning');

    try {
      // Mock face scanning process
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Simulate successful face recognition
      setStep('complete');
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Navigate to home page
      navigate('/home');
    } catch (err) {
      setError('Face recognition failed. Please try again.');
      setStep('ready');
    } finally {
      setScanning(false);
    }
  };

  const getInstructions = () => {
    if (isLogin) {
      return {
        title: 'Verify Your Identity',
        subtitle: 'Look at the camera to verify your face ID',
        buttonText: 'Scan Face'
      };
    } else {
      return {
        title: 'Set Up Face ID',
        subtitle: 'Position your face in the frame to set up secure access',
        buttonText: 'Set Up Face ID'
      };
    }
  };

  const instructions = getInstructions();

  return (
    <Container maxWidth="sm" sx={{ minHeight: '100vh', py: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <IconButton onClick={() => navigate(-1)} sx={{ mr: 1 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h6">Face ID</Typography>
      </Box>

      <Card>
        <CardContent sx={{ p: 3, textAlign: 'center' }}>
          <Typography 
            variant="h5" 
            component="h1" 
            gutterBottom 
            sx={{ mb: 2 }}
          >
            {instructions.title}
          </Typography>

          <Typography 
            variant="body2" 
            color="textSecondary" 
            sx={{ mb: 4 }}
          >
            {instructions.subtitle}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ mb: 4 }}>
            <Box
              sx={{
                width: 200,
                height: 200,
                margin: '0 auto',
                borderRadius: '50%',
                border: step === 'scanning' ? '4px solid #2196f3' : '4px solid #e0e0e0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: step === 'complete' ? '#4caf50' : '#f5f5f5',
                transition: 'all 0.3s ease',
                animation: step === 'scanning' ? 'pulse 2s infinite' : 'none',
                mb: 3,
              }}
            >
              {step === 'complete' ? (
                <Typography variant="h4" sx={{ color: 'white' }}>
                  ✓
                </Typography>
              ) : (
                <Avatar sx={{ 
                  width: 100, 
                  height: 100, 
                  backgroundColor: 'transparent',
                  color: step === 'scanning' ? '#2196f3' : '#666'
                }}>
                  <FaceRetouchingNatural sx={{ fontSize: 60 }} />
                </Avatar>
              )}
            </Box>

            {step === 'scanning' && (
              <Box sx={{ mb: 2 }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography variant="body2" color="textSecondary">
                  Scanning your face...
                </Typography>
              </Box>
            )}

            {step === 'complete' && (
              <Typography variant="body1" color="success.main" sx={{ mb: 2 }}>
                Face ID {isLogin ? 'verified' : 'set up'} successfully!
              </Typography>
            )}
          </Box>

          {step === 'ready' && (
            <>
              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={startFaceScan}
                disabled={scanning}
                sx={{ mb: 3 }}
              >
                {instructions.buttonText}
              </Button>

              <Box sx={{ 
                backgroundColor: '#f5f5f5', 
                borderRadius: 2, 
                p: 2,
                textAlign: 'left'
              }}>
                <Typography variant="body2" color="textSecondary" sx={{ mb: 1, fontWeight: 500 }}>
                  Tips for better recognition:
                </Typography>
                <Typography variant="body2" color="textSecondary" component="div">
                  • Hold your device at eye level
                  <br />
                  • Ensure good lighting
                  <br />
                  • Remove glasses if needed
                  <br />
                  • Keep your face centered
                </Typography>
              </Box>
            </>
          )}
        </CardContent>
      </Card>

      <style>
        {`
          @keyframes pulse {
            0% {
              box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.7);
            }
            70% {
              box-shadow: 0 0 0 10px rgba(33, 150, 243, 0);
            }
            100% {
              box-shadow: 0 0 0 0 rgba(33, 150, 243, 0);
            }
          }
        `}
      </style>
    </Container>
  );
};

export default FaceIDPage;