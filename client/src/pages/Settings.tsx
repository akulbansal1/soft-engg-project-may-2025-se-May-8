import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Eye,
  EyeOff,
  User,
  Calendar,
  Phone,
  Mail,
  MapPin,
  Heart,
  ArrowLeft,
  Edit2,
  X,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const Settings: React.FC = () => {
  const [showInfo, setShowInfo] = useState({
    phone: false,
    email: false,
    address: false,
  });

  const [editMode, setEditMode] = useState({
    personal: false,
    contact: false,
    medical: false,
  });

  const [userInfo, setUserInfo] = useState({
    name: "John Doe",
    age: "32",
    phone: "+1 (555) 123-4567",
    email: "john.doe@email.com",
    address: "123 Main St, City, State 12345",
    emergencyContact: "Jane Doe - +1 (555) 987-6543",
    bloodType: "O+",
    allergies: "None",
    conditions: "Hypertension",
  });

  const toggleVisibility = (field: keyof typeof showInfo) => {
    setShowInfo((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const toggleEditMode = (section: keyof typeof editMode) => {
    setEditMode((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleSave = (section: keyof typeof editMode) => {
    setEditMode((prev) => ({ ...prev, [section]: false }));
    // Save changes to backend here
  };

  // Better utilize space
  // Text consistency

  const SimpleField = ({
    label,
    value,
    icon: Icon,
  }: {
    label: string;
    value: string;
    icon: React.ElementType;
  }) => (
    <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700">
      <div className="flex items-center space-x-3">
        <Icon size={20} className="text-zinc-600 dark:text-zinc-400" />
        <div>
          <p className="font-medium text-sm text-zinc-900 dark:text-zinc-100">
            {label}
          </p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">{value}</p>
        </div>
      </div>
    </div>
  );

  const PrivacyField = ({
    label,
    field,
    value,
    icon: Icon,
  }: {
    label: string;
    field: keyof typeof showInfo;
    value: string;
    icon: React.ElementType;
  }) => (
    <div className="flex items-center justify-between p-3 rounded-lg bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700">
      <div className="flex items-center space-x-3">
        <Icon size={20} className="text-zinc-600 dark:text-zinc-400" />
        <div>
          <p className="font-medium text-sm text-zinc-900 dark:text-zinc-100">
            {label}
          </p>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {showInfo[field] ? value : "••••••••"}
          </p>
        </div>
      </div>
      <button
        onClick={() => toggleVisibility(field)}
        className="p-2 rounded-full hover:bg-zinc-200 dark:hover:bg-zinc-700 transition-colors"
      >
        {showInfo[field] ? (
          <EyeOff size={18} className="text-zinc-600 dark:text-zinc-400" />
        ) : (
          <Eye size={18} className="text-zinc-600 dark:text-zinc-400" />
        )}
      </button>
    </div>
  );

  const navigate = useNavigate();

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <Button variant="ghost" size="sm" className="p-2" onClick={() => navigate('/home')}>
              <ArrowLeft size={20} />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100">
                Settings
              </h1>
              <p className="text-sm text-zinc-600 dark:text-zinc-400">
                Manage your profile and privacy
              </p>
            </div>
          </div>
          <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 flex items-center justify-center">
            <User size={24} className="text-white" />
          </div>
        </div>

        {/* Personal Information Card */}
        <Card className="border border-zinc-200 dark:border-zinc-700 shadow-lg">
          <CardHeader className="pb-3 flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <User size={20} className="text-blue-600" />
              <span>Personal Information</span>
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleEditMode("personal")}
              className="text-blue-600 hover:text-blue-700"
            >
              {editMode.personal ? <X size={16} /> : <Edit2 size={16} />}
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <SimpleField label="Full Name" value={userInfo.name} icon={User} />
            <SimpleField label="Age" value={userInfo.age} icon={Calendar} />
          </CardContent>
        </Card>

        {/* Contact Information Card */}
        <Card className="border border-zinc-200 dark:border-zinc-700 shadow-lg">
          <CardHeader className="pb-3 flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Phone size={20} className="text-green-600" />
              <span>Contact Information</span>
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => toggleEditMode("contact")}
              className="text-green-600 hover:text-green-700"
            >
              {editMode.contact ? <X size={16} /> : <Edit2 size={16} />}
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <PrivacyField
              label="Phone Number"
              field="phone"
              value={userInfo.phone}
              icon={Phone}
            />
          </CardContent>
        </Card>

        {/* Emergency Contact Card */}
        <Card className="border border-zinc-200 dark:border-zinc-700 shadow-lg">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <Heart size={20} className="text-red-600" />
              <span>Emergency Contact</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleField
              label="Emergency Contact"
              value={userInfo.emergencyContact}
              icon={Phone}
            />
          </CardContent>
        </Card>

        {/* Medical Information Card */}

        {/* Privacy Notice */}
        <Card className="border border-zinc-200 dark:border-zinc-700 shadow-lg">
          <CardContent className="pt-6">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center flex-shrink-0">
                <Eye size={16} className="text-Blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 mb-1">
                  Privacy Protection
                </h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                  Your sensitive information is hidden by default. Use the eye
                  icons to temporarily view your data.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Settings;
