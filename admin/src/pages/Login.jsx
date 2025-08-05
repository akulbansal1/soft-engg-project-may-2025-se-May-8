import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  Checkbox,
  message,
  Spin,
} from "antd";
import {
  UserOutlined,
  LockOutlined,
  EyeInvisibleOutlined,
  EyeTwoTone,
  MedicineBoxOutlined,
  EnvironmentOutlined,
} from "@ant-design/icons";
import axios from "axios";

const { Title, Text, Link } = Typography;

const Login = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [doctors, setDoctors] = useState([]);
  const [fetching, setFetching] = useState(true);
  const navigate = useNavigate();

  const BACKEND_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;
  const ADMIN_TOKEN = import.meta.env.VITE_ADMIN_TOKEN;

  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        const res = await axios.get(`${BACKEND_BASE_URL}/api/v1/doctors/`);
        setDoctors(res.data);
      } catch (error) {
        message.error("Failed to fetch doctors");
      } finally {
        setFetching(false);
      }
    };
    fetchDoctors();
  }, [BACKEND_BASE_URL]);

  const handleDoctorClick = async (doctorId) => {
    const selectedDoctor = doctors.find(doctor => doctor.id === doctorId);

    if (selectedDoctor) {
      localStorage.setItem('activeDoctorDetails', JSON.stringify({
        id: selectedDoctor.id,
        name: selectedDoctor.name,
        location: selectedDoctor.location,
        loginTimestamp: new Date().toISOString()
      }));
    }

    try {
      const header = await fetch(`${BACKEND_BASE_URL}/api/v1/auth/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${ADMIN_TOKEN}` // Ensure ADMIN_TOKEN is defined
        },
        credentials: 'include'
      });

      await new Promise((resolve) => setTimeout(resolve, 1500));
      message.success("Login successful! Redirecting...");

      navigate(`/dashboard/${doctorId}`);
    } catch (err) {
      message.error("Login failed");
      console.error(err);
    }
  };
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 75%, #475569 100%)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Sophisticated Background Pattern */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M40 40c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20zm20-20c0-11.046-8.954-20-20-20s-20 8.954-20 20 8.954 20 20 20 20-8.954 20-20z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          zIndex: 1,
        }}
      />

      {/* Elegant Floating Elements */}
      <div
        style={{
          position: "absolute",
          top: "8%",
          left: "10%",
          width: "150px",
          height: "150px",
          background: "linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(99, 102, 241, 0.05))",
          borderRadius: "50%",
          animation: "gentleFloat 8s ease-in-out infinite",
          zIndex: 1,
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "60%",
          right: "5%",
          width: "100px",
          height: "100px",
          background: "linear-gradient(135deg, rgba(236, 72, 153, 0.06), rgba(168, 85, 247, 0.04))",
          borderRadius: "50%",
          animation: "gentleFloat 12s ease-in-out infinite reverse",
          zIndex: 1,
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "10%",
          left: "20%",
          width: "60px",
          height: "60px",
          background: "linear-gradient(135deg, rgba(34, 197, 94, 0.05), rgba(14, 165, 233, 0.03))",
          borderRadius: "50%",
          animation: "gentleFloat 10s ease-in-out infinite",
          zIndex: 1,
        }}
      />

      <style>
        {`
          @keyframes gentleFloat {
            0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0.4; }
            25% { transform: translateY(-15px) translateX(5px); opacity: 0.6; }
            50% { transform: translateY(-8px) translateX(-3px); opacity: 0.8; }
            75% { transform: translateY(-20px) translateX(8px); opacity: 0.5; }
          }

          .doctor-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            overflow: hidden;
          }

          .doctor-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          }

          .doctor-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.1), transparent);
            transition: left 0.5s;
          }

          .doctor-card:hover::before {
            left: 100%;
          }
        `}
      </style>

      {/* Main Content Container */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          width: "100%",
          maxWidth: "1200px",
          zIndex: 2,
          padding: "20px",
        }}
      >
        <div style={{ width: "100%", maxWidth: "520px" }}>
          <Card
            style={{
              borderRadius: "28px",
              border: "1px solid rgba(255, 255, 255, 0.08)",
              boxShadow: "0 32px 64px -12px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05)",
              background: "linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%)",
              backdropFilter: "blur(24px)",
              WebkitBackdropFilter: "blur(24px)",
            }}
            bodyStyle={{
              padding: "clamp(40px, 6vw, 56px)",
            }}
          >
            {/* Header Section */}
            <div style={{ textAlign: "center", marginBottom: "40px" }}>
              <div
                style={{
                  width: "80px",
                  height: "80px",
                  background: "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)",
                  borderRadius: "20px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 24px",
                  boxShadow: "0 8px 32px rgba(59, 130, 246, 0.3)",
                }}
              >
                <MedicineBoxOutlined style={{ fontSize: "36px", color: "white" }} />
              </div>
              
              <Title
                level={1}
                style={{
                  color: "#0f172a",
                  marginBottom: "8px",
                  fontSize: "clamp(28px, 4vw, 36px)",
                  fontWeight: "700",
                  background: "linear-gradient(135deg, #0f172a 0%, #334155 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                Doctor Admin Portal
              </Title>
              <Text 
                style={{ 
                  fontSize: "16px", 
                  color: "#64748b",
                  fontWeight: "500",
                  letterSpacing: "0.01em"
                }}
              >
                Select your profile to access the professional dashboard
              </Text>
            </div>

            {/* Doctor Profiles Section */}
            <div style={{ marginTop: "32px" }}>
              <div style={{ 
                display: "flex", 
                alignItems: "center", 
                marginBottom: "20px",
                paddingBottom: "12px",
                borderBottom: "2px solid #e2e8f0"
              }}>
                <Title 
                  level={4} 
                  style={{ 
                    margin: 0, 
                    color: "#1e293b",
                    fontWeight: "600",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px"
                  }}
                >
                  <UserOutlined style={{ color: "#3b82f6" }} />
                  Available Medical Professionals
                </Title>
              </div>

              {fetching ? (
                <div 
                  style={{ 
                    textAlign: "center", 
                    padding: "60px 20px",
                    background: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                    borderRadius: "16px",
                    border: "1px solid #e2e8f0"
                  }}
                >
                  <Spin size="large" />
                  <div style={{ marginTop: "16px", color: "#64748b", fontSize: "14px" }}>
                    Loading medical professionals...
                  </div>
                </div>
              ) : doctors.length === 0 ? (
                <div 
                  style={{ 
                    textAlign: "center", 
                    padding: "40px 20px",
                    background: "linear-gradient(135deg, #fef7cd 0%, #fef3c7 100%)",
                    borderRadius: "16px",
                    border: "1px solid #f59e0b"
                  }}
                >
                  <Text style={{ color: "#92400e", fontSize: "16px", fontWeight: "500" }}>
                    No doctors available at the moment
                  </Text>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  {doctors.map((doctor, index) => (
                    <Card
                      key={doctor.id}
                      className="doctor-card"
                      onClick={() => handleDoctorClick(doctor.id)}
                      style={{
                        borderRadius: "16px",
                        background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
                        border: "1px solid #e2e8f0",
                        boxShadow: "0 2px 8px rgba(0, 0, 0, 0.04)",
                        position: "relative",
                      }}
                      bodyStyle={{
                        padding: "20px 24px",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                        <div
                          style={{
                            width: "48px",
                            height: "48px",
                            background: `linear-gradient(135deg, ${
                              index % 3 === 0 
                                ? "#3b82f6, #8b5cf6" 
                                : index % 3 === 1 
                                ? "#10b981, #3b82f6" 
                                : "#f59e0b, #ef4444"
                            })`,
                            borderRadius: "12px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "white",
                            fontSize: "18px",
                            fontWeight: "600",
                            flexShrink: 0,
                          }}
                        >
                          {doctor.name.charAt(0).toUpperCase()}
                        </div>
                        
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <Text 
                            style={{ 
                              fontSize: "18px", 
                              fontWeight: "600", 
                              color: "#0f172a",
                              display: "block",
                              marginBottom: "4px"
                            }}
                          >
                            {doctor.name}
                          </Text>
                          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <EnvironmentOutlined style={{ color: "#64748b", fontSize: "14px" }} />
                            <Text 
                              style={{ 
                                color: "#64748b", 
                                fontSize: "14px",
                                fontWeight: "500"
                              }}
                            >
                              {doctor.location}
                            </Text>
                          </div>
                        </div>

                        <div
                          style={{
                            padding: "6px 12px",
                            background: "linear-gradient(135deg, #dbeafe 0%, #ede9fe 100%)",
                            borderRadius: "8px",
                            border: "1px solid #c7d2fe",
                          }}
                        >
                          <Text style={{ color: "#4338ca", fontSize: "12px", fontWeight: "600" }}>
                            ACTIVE
                          </Text>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Login;