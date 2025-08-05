import React, { useState, useRef } from 'react';
import { Modal, Button, Typography, Space, message, Card, Descriptions } from 'antd';
import { AudioOutlined, StopOutlined, SoundOutlined, CheckCircleOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const PrescriptionModal = ({ 
  visible, 
  onClose, 
  patientName, 
  appointmentId,
  userId,
  doctorId 
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [hasRecording, setHasRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcriptionData, setTranscriptionData] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isCreatingEntry, setIsCreatingEntry] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

  console.log('User ID:', userId);
console.log('Doctor ID:', doctorId);
console.log('Appointment ID:', appointmentId);


  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Convert webm to mp3-compatible format
        const mp3Blob = await convertToMp3Compatible(audioBlob);
        setAudioBlob(mp3Blob);
        setHasRecording(true);
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(1000); // Record in 1-second chunks
      setIsRecording(true);
      message.success('Recording started');
      
    } catch (error) {
      console.error('Error starting recording:', error);
      message.error('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      message.success('Recording stopped');
    }
  };

  // Convert webm to a more compatible format (we'll send as webm but name it as audio file)
  const convertToMp3Compatible = async (webmBlob) => {
    // For now, we'll send the webm blob as is, but you could implement
    // actual conversion to MP3 using libraries like lamejs if needed
    return webmBlob;
  };

  const createMedicineEntry = async () => {
    if (!transcriptionData) {
      message.error('No prescription data available');
      return;
    }

    setIsCreatingEntry(true);
    
    try {
      const requestBody = {
        name: transcriptionData.name || '',
        dosage: transcriptionData.dosage || '',
        frequency: transcriptionData.frequency || '',
        start_date: transcriptionData.start_date ? transcriptionData.start_date.split('T')[0] : '',
        end_date: transcriptionData.end_date ? transcriptionData.end_date.split('T')[0] : '',
        notes: transcriptionData.notes || '',
        user_id: userId ? parseInt(userId) : '',
        doctor_id: doctorId ? parseInt(doctorId) : '',
        appointment_id: appointmentId ? parseInt(appointmentId) : ''
      };

      // Remove empty values if needed (optional)
      Object.keys(requestBody).forEach(key => {
        if (requestBody[key] === null || requestBody[key] === undefined) {
          requestBody[key] = '';
        }
      });

      const response = await fetch(`${BACKEND_BASE_URL}/api/v1/medicines/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      message.success('Medicine entry created successfully!');
      
      // Close modal after successful creation
      setTimeout(() => {
        handleClose();
      }, 1500);
      
    } catch (error) {
      console.error('Medicine entry creation error:', error);
      message.error('Failed to create medicine entry. Please try again.');
    } finally {
      setIsCreatingEntry(false);
    }
  };

  const handleTranscribe = async () => {
    if (!audioBlob) {
      message.error('No audio recording found');
      return;
    }

    setIsTranscribing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'prescription-audio.webm');

      const response = await fetch(`${BACKEND_BASE_URL}/api/v1/medicines/transcribe`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTranscriptionData(data);
      message.success('Prescription transcribed successfully!');
      
    } catch (error) {
      console.error('Transcription error:', error);
      message.error('Failed to transcribe prescription. Please try again.');
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleClose = () => {
    // Clean up any ongoing recording
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
    
    setIsRecording(false);
    setHasRecording(false);
    setIsTranscribing(false);
    setTranscriptionData(null);
    setAudioBlob(null);
    setIsCreatingEntry(false);
    onClose();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not specified';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={handleClose}
      footer={null}
      width={transcriptionData ? 700 : 500}
      centered
      styles={{
        body: { padding: '32px' }
      }}
    >
      <div style={{ textAlign: 'center' }}>
        {/* Header */}
        <div style={{ marginBottom: '32px' }}>
          <Title level={3} style={{ 
            color: '#1e293b', 
            marginBottom: '8px',
            fontWeight: '600'
          }}>
            Record Prescription
          </Title>
          <Text style={{ 
            fontSize: '16px', 
            color: '#64748b',
            display: 'block'
          }}>
            for {patientName}
          </Text>
        </div>

        {/* Show transcription results if available */}
        {transcriptionData && (
          <div style={{ marginBottom: '32px', textAlign: 'left' }}>
            <Card
              title={
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircleOutlined style={{ color: '#10b981' }} />
                  <span>Prescription Details</span>
                </div>
              }
              style={{ borderRadius: '12px', border: '2px solid #10b981' }}
            >
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="Medicine Name">
                  <Text strong style={{ color: '#1e293b' }}>
                    {transcriptionData.name || 'Not specified'}
                  </Text>
                </Descriptions.Item>
                <Descriptions.Item label="Dosage">
                  {transcriptionData.dosage || 'Not specified'}
                </Descriptions.Item>
                <Descriptions.Item label="Frequency">
                  {transcriptionData.frequency || 'Not specified'}
                </Descriptions.Item>
                <Descriptions.Item label="Start Date">
                  {formatDate(transcriptionData.start_date)}
                </Descriptions.Item>
                <Descriptions.Item label="End Date">
                  {formatDate(transcriptionData.end_date)}
                </Descriptions.Item>
                <Descriptions.Item label="Notes">
                  {transcriptionData.notes || 'No additional notes'}
                </Descriptions.Item>
              </Descriptions>
              
              <div style={{ marginTop: '20px', textAlign: 'center' }}>
                <Button
                  type="primary"
                  size="large"
                  loading={isCreatingEntry}
                  onClick={createMedicineEntry}
                  style={{
                    height: '48px',
                    padding: '0 32px',
                    borderRadius: '24px',
                    fontWeight: '600',
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
                    border: 'none',
                    boxShadow: '0 4px 15px rgba(139, 92, 246, 0.3)',
                    fontSize: '16px'
                  }}
                >
                  {isCreatingEntry ? 'Creating Entry...' : 'Create Medicine Entry'}
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Audio Recording Section */}
        <div style={{
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
          borderRadius: '16px',
          padding: '40px 24px',
          marginBottom: '24px',
          border: '2px dashed #cbd5e1'
        }}>
          {!isRecording && !hasRecording && (
            <div>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)'
              }}>
                <AudioOutlined style={{ 
                  fontSize: '32px', 
                  color: 'white' 
                }} />
              </div>
              <Text style={{ 
                fontSize: '16px', 
                color: '#64748b',
                display: 'block',
                marginBottom: '20px'
              }}>
                Click the button below to start recording
              </Text>
              <Button
                type="primary"
                size="large"
                icon={<AudioOutlined />}
                onClick={startRecording}
                style={{
                  height: '48px',
                  padding: '0 32px',
                  borderRadius: '24px',
                  fontWeight: '600',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                  border: 'none',
                  boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)'
                }}
              >
                Start Recording
              </Button>
            </div>
          )}

          {isRecording && (
            <div>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                boxShadow: '0 8px 25px rgba(239, 68, 68, 0.3)',
                animation: 'pulse 2s infinite'
              }}>
                <SoundOutlined style={{ 
                  fontSize: '32px', 
                  color: 'white' 
                }} />
              </div>
              <Text style={{ 
                fontSize: '18px', 
                color: '#ef4444',
                display: 'block',
                marginBottom: '20px',
                fontWeight: '600'
              }}>
                Recording in progress...
              </Text>
              <Button
                danger
                size="large"
                icon={<StopOutlined />}
                onClick={stopRecording}
                style={{
                  height: '48px',
                  padding: '0 32px',
                  borderRadius: '24px',
                  fontWeight: '600'
                }}
              >
                Stop Recording
              </Button>
            </div>
          )}

          {hasRecording && !isRecording && (
            <div>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                boxShadow: '0 8px 25px rgba(16, 185, 129, 0.3)'
              }}>
                <AudioOutlined style={{ 
                  fontSize: '32px', 
                  color: 'white' 
                }} />
              </div>
              <Text style={{ 
                fontSize: '16px', 
                color: '#059669',
                display: 'block',
                marginBottom: '20px',
                fontWeight: '600'
              }}>
                Recording completed successfully!
              </Text>
              <Space>
                <Button
                  size="large"
                  onClick={startRecording}
                  style={{
                    height: '48px',
                    padding: '0 24px',
                    borderRadius: '24px',
                    fontWeight: '600'
                  }}
                >
                  Record Again
                </Button>
                <Button
                  type="primary"
                  size="large"
                  loading={isTranscribing}
                  onClick={handleTranscribe}
                  style={{
                    height: '48px',
                    padding: '0 24px',
                    borderRadius: '24px',
                    fontWeight: '600',
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    border: 'none',
                    boxShadow: '0 4px 15px rgba(16, 185, 129, 0.3)'
                  }}
                >
                  {isTranscribing ? 'Processing...' : 'Transcribe and Process'}
                </Button>
              </Space>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div style={{
          background: '#f8fafc',
          borderRadius: '12px',
          padding: '16px',
          border: '1px solid #e2e8f0'
        }}>
          <Text style={{ 
            fontSize: '14px', 
            color: '#64748b',
            lineHeight: '1.5'
          }}>
            <strong>Instructions:</strong><br />
            • Speak clearly and at a moderate pace<br />
            • Include patient symptoms, diagnosis, and medication details<br />
            • Review the prescription before finalizing
          </Text>
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0% {
            transform: scale(1);
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
          }
          50% {
            transform: scale(1.05);
            box-shadow: 0 12px 35px rgba(239, 68, 68, 0.5);
          }
          100% {
            transform: scale(1);
            box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3);
          }
        }
      `}</style>
    </Modal>
  );
};

export default PrescriptionModal;