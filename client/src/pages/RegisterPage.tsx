import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import PhoneInput from 'react-phone-input-2';
import dayjs from 'dayjs';

interface FormData {
  firstName: string;
  middleName: string;
  lastName: string;
  phone: string;
  dateOfBirth: dayjs.Dayjs | null;
  gender: string;
}

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    middleName: '',
    lastName: '',
    phone: '',
    dateOfBirth: null,
    gender: '',
  });
  const [error, setError] = useState('');

  const handleInputChange = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.firstName.trim()) return 'First name is required';
    if (!formData.lastName.trim()) return 'Last name is required';
    if (!formData.phone || formData.phone.length < 10) return 'Valid phone number is required';
    if (!formData.dateOfBirth) return 'Date of birth is required';
    if (!formData.gender) return 'Gender is required';
    return '';
  };

  const handleRegister = async () => {
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      // Check if phone already exists
      const checkResponse = await fetch(`http://localhost:3001/users?phone=%2B${formData.phone}`);
      const existingUsers = await checkResponse.json();
      
      if (existingUsers.length > 0) {
        setError('Phone number already registered. Please sign in instead.');
        return;
      }

      // Store user data temporarily in localStorage for the registration flow
      localStorage.setItem('registrationData', JSON.stringify({
        ...formData,
        phone: `+${formData.phone}`,
        dateOfBirth: formData.dateOfBirth?.format('YYYY-MM-DD'),
      }));

      // Navigate to OTP page
      navigate('/otp', { state: { phone: `+${formData.phone}`, isLogin: false } });
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
        <Typography variant="h6">Create Account</Typography>
      </Box>

      <Card>
        <CardContent sx={{ p: 3 }}>
          <Typography 
            variant="h5" 
            component="h1" 
            gutterBottom 
            sx={{ textAlign: 'center', mb: 3 }}
          >
            Join HealthCare+
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="First Name"
                fullWidth
                value={formData.firstName}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Middle Name (Optional)"
                fullWidth
                value={formData.middleName}
                onChange={(e) => handleInputChange('middleName', e.target.value)}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Last Name"
                fullWidth
                value={formData.lastName}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                Phone Number *
              </Typography>
              <PhoneInput
                country={'in'}
                value={formData.phone}
                onChange={(value) => handleInputChange('phone', value)}
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
            </Grid>

            <Grid item xs={12}>
              <DatePicker
                label="Date of Birth"
                value={formData.dateOfBirth}
                onChange={(date) => handleInputChange('dateOfBirth', date)}
                maxDate={dayjs().subtract(1, 'year')}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    required: true,
                  },
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <FormControl fullWidth required>
                <InputLabel>Gender</InputLabel>
                <Select
                  value={formData.gender}
                  label="Gender"
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                >
                  <MenuItem value="male">Male</MenuItem>
                  <MenuItem value="female">Female</MenuItem>
                  <MenuItem value="other">Other</MenuItem>
                  <MenuItem value="prefer-not-to-say">Prefer not to say</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={handleRegister}
            sx={{ mt: 3, mb: 2 }}
          >
            Continue
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="textSecondary">
              Already have an account?{' '}
              <Button 
                variant="text" 
                onClick={() => navigate('/login')}
                sx={{ textTransform: 'none', p: 0 }}
              >
                Sign in here
              </Button>
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default RegisterPage;