export const mockPatients = [
    {
      id: 1,
      name: "John Smith",
      age: 45,
      gender: "Male",
      phone: "+1 (555) 123-4567",
      email: "john.smith@email.com",
      lastVisit: "2025-06-25",
      condition: "Hypertension",
      status: "Active",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=John"
    },
    {
      id: 2,
      name: "Sarah Johnson",
      age: 32,
      gender: "Female",
      phone: "+1 (555) 987-6543",
      email: "sarah.johnson@email.com",
      lastVisit: "2025-06-24",
      condition: "Diabetes Type 2",
      status: "Active",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah"
    },
    {
      id: 3,
      name: "Michael Brown",
      age: 58,
      gender: "Male",
      phone: "+1 (555) 456-7890",
      email: "michael.brown@email.com",
      lastVisit: "2025-06-23",
      condition: "Arthritis",
      status: "Inactive",
      avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Michael"
    }
  ];
  
  export const mockAppointments = [
    {
      id: 1,
      patientName: "John Smith",
      patientId: 1,
      date: "2025-06-27",
      time: "09:00 AM",
      type: "Consultation",
      status: "Scheduled",
      duration: "30 mins",
      notes: "Regular checkup for hypertension"
    },
    {
      id: 2,
      patientName: "Sarah Johnson",
      patientId: 2,
      date: "2025-06-27",
      time: "10:30 AM",
      type: "Follow-up",
      status: "Confirmed",
      duration: "20 mins",
      notes: "Diabetes management review"
    },
    {
      id: 3,
      patientName: "Michael Brown",
      patientId: 3,
      date: "2025-06-28",
      time: "02:00 PM",
      type: "Treatment",
      status: "Pending",
      duration: "45 mins",
      notes: "Arthritis treatment session"
    }
  ];
  
  export const mockStats = {
    totalPatients: 156,
    todayAppointments: 8,
    pendingReports: 12,
    revenue: 15420
  };
  
  export const doctorProfile = {
    name: "Dr. Emily Carter",
    specialization: "Internal Medicine",
    experience: "12 years",
    education: "MD from Harvard Medical School",
    phone: "+1 (555) 000-1234",
    email: "dr.carter@hospital.com",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Emily",
    bio: "Dedicated internal medicine physician with over 12 years of experience in patient care, diagnosis, and treatment of various medical conditions."
  };
  