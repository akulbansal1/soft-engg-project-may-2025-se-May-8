import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Eye, Search, ArrowLeft } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useNavigate } from "react-router-dom";
import { Calendar } from "@/components/ui/calendar";
import { Calendar } from "@/components/ui/calendar";

interface Appointment {
  date: string;
  time: string;
  doctor: string;
  purpose: string;
  location: string;
  prescription?: string;
  comments?: string;
}

const parseLocalDate = (dateStr: string): Date => {
  const [year, month, day] = dateStr.split("-").map(Number);
  return new Date(year, month - 1, day);
};

const AppointmentsPage: React.FC = () => {
  const [appointments] = useState<Appointment[]>([
    {
      date: "2025-06-15",
      time: "10:00",
      doctor: "Dr. Smith",
      purpose: "Routine Checkup",
      location: "Clinic A",
      prescription: "Paracetamol 500mg, Vitamin C",
      comments: "Take rest and drink plenty of water.",
    },
    {
      date: "2025-07-01",
      time: "14:30",
      doctor: "Dr. Lee",
      purpose: "Dental Cleaning",
      location: "Clinic B",
      prescription: "No medication required",
      comments: "Avoid sweets for a few days.",
    },
    {
      date: "2025-08-01",
      time: "11:00",
      doctor: "Dr. Kumar",
      purpose: "Eye Checkup",
      location: "Clinic C",
    },
    {
      date: "2025-08-15",
      time: "09:30",
      doctor: "Dr. Mehra",
      purpose: "ENT Consultation",
      location: "City Hospital",
      prescription: "Antibiotic nasal spray",
      comments: "Follow up in 10 days.",
    },
    {
      date: "2025-09-05",
      time: "16:00",
      doctor: "Dr. Jain",
      purpose: "Physiotherapy",
      location: "Therapy Center",
      prescription: "Stretching exercises",
      comments: "Attend weekly sessions.",
    },
    {
      date: "2025-09-20",
      time: "10:15",
      doctor: "Dr. Chopra",
      purpose: "Cardiology Review",
      location: "Heart Care Clinic",
      prescription: "Aspirin 75mg",
      comments: "Monitor blood pressure daily.",
    },
    {
      date: "2025-10-03",
      time: "13:45",
      doctor: "Dr. Fernandes",
      purpose: "Skin Rash",
      location: "Dermacare",
      prescription: "Antihistamine tablets",
      comments: "Apply cream twice daily.",
    },
  ]);

  const [viewOpen, setViewOpen] = useState(false);
  const [detailIndex, setDetailIndex] = useState<number | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [tab, setTab] = useState("calendar");
  const todayStr = new Date().toISOString().split("T")[0];
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [tab, setTab] = useState("calendar");
  const todayStr = new Date().toISOString().split("T")[0];
  const navigate = useNavigate();

  const appointmentsByDate = useMemo(() => {
    const map = new Map<string, Appointment[]>();
    appointments.forEach((appt) => {
      const key = parseLocalDate(appt.date).toDateString();
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(appt);
    });
    return map;
  }, [appointments]);

  const formattedSelected = selectedDate?.toDateString() || "";
  const dailyAppointments = appointmentsByDate.get(formattedSelected) || [];

  const filteredUpcoming = useMemo(
    () =>
      appointments
        .filter((a) => a.date >= todayStr)
        .filter((a) =>
          [a.date, a.time, a.doctor, a.purpose, a.location].some((f) =>
            f.toLowerCase().includes(searchTerm.toLowerCase())
          )
        )
        .sort((a, b) => a.date.localeCompare(b.date)),
    [appointments, searchTerm]
  );

  const filteredPast = useMemo(
    () =>
      appointments
        .filter((a) => a.date < todayStr)
        .filter((a) =>
          [
            a.date,
            a.time,
            a.doctor,
            a.purpose,
            a.location,
            a.prescription ?? "",
            a.comments ?? "",
          ].some((f) => f.toLowerCase().includes(searchTerm.toLowerCase()))
  const filteredPast = useMemo(
    () =>
      appointments
        .filter((a) => a.date < todayStr)
        .filter((a) =>
          [
            a.date,
            a.time,
            a.doctor,
            a.purpose,
            a.location,
            a.prescription ?? "",
            a.comments ?? "",
          ].some((f) => f.toLowerCase().includes(searchTerm.toLowerCase()))
        )
        .sort((a, b) => b.date.localeCompare(a.date)),
    [appointments, searchTerm]
  );
        .sort((a, b) => b.date.localeCompare(a.date)),
    [appointments, searchTerm]
  );

  const openView = (idx: number) => {
    setDetailIndex(idx);
    setViewOpen(true);
  };

  const renderList = (list: Appointment[], isPast = false) => (
    <div className="space-y-4">
      {list.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>
            {isPast ? "No past appointments." : "No upcoming appointments."}
          </p>
        </div>
      ) : (
        list.map((appt, idx) => (
          <Card key={idx} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold text-lg mb-1">
                  {appt.date} @ {appt.time}
                </p>
                <p className="text-sm text-muted-foreground">
                  {appt.doctor} – {appt.purpose}
                </p>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => openView(appointments.indexOf(appt))}
              >
                <Eye size={16} />
              </Button>
            </div>
            {isPast && (
              <div className="mt-2 space-y-2">
                <div className="p-2 bg-muted rounded text-sm">
                  <strong>Prescription:</strong> {appt.prescription || "None"}
                </div>
                <div className="p-2 bg-muted rounded text-sm">
                  <strong>Comments:</strong> {appt.comments || "None"}
                </div>
              </div>
            )}
          </Card>
        ))
      )}
    </div>
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <h2 className="text-2xl font-semibold flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/home")}
            className="mr-4"
          >
            <ArrowLeft size={20} />
          </Button>
          Appointments
        </h2>
      </div>

      {/* Search */}
      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search appointments..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <Tabs
        value={tab}
        onValueChange={setTab}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="grid grid-cols-3 w-full">
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
        <TabsList className="grid grid-cols-3 w-full">
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
          <TabsTrigger value="upcoming">
            Upcoming ({filteredUpcoming.length})
          </TabsTrigger>
          <TabsTrigger value="past">Past ({filteredPast.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="flex-1 overflow-hidden">
          <div className="flex flex-col md:flex-row h-full gap-6">
            <div className="flex-1 flex justify-center items-center">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                className="w-full h-full min-h-[250px] md:min-h-[350px]"
                modifiers={{
                  hasFutureAppointment: (date) => {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    return (
                      appointmentsByDate.has(date.toDateString()) &&
                      date >= today
                    );
                  },
                  hasPastAppointment: (date) => {
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    return (
                      appointmentsByDate.has(date.toDateString()) &&
                      date < today
                    );
                  },
                }}
                modifiersClassNames={{
                  hasFutureAppointment:
                    "bg-blue-100 dark:bg-blue-900/50 rounded-lg",
                  hasPastAppointment:
                    "bg-green-100 dark:bg-green-900/50 rounded-lg",
                }}
              />
            </div>
            <div className="flex-1 flex flex-col">
              <Card className="flex-1 bg-transparent shadow-none">
                <CardHeader>
                  <CardTitle>{formattedSelected || "Select a date"}</CardTitle>
                </CardHeader>
                <CardContent className="flex-1 overflow-y-auto">
                  {dailyAppointments.length ? (
                    dailyAppointments.map((appt, i) => (
                      <div
                        key={i}
                        className="flex justify-between items-center border-b py-2"
                      >
                        <div>
                          <p className="font-medium">
                            {appt.time} – {appt.purpose}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {appt.doctor}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openView(appointments.indexOf(appt))}
                        >
                          <Eye size={16} />
                        </Button>
                      </div>
                    ))
                  ) : (
                    <p className="text-muted-foreground">No appointments.</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent
          value="upcoming"
          className="flex-1 flex flex-col mt-4 overflow-hidden"
        >
          <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
          <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
            <CardHeader>
              <CardTitle>Upcoming Appointments</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {renderList(filteredUpcoming)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Past Tab */}
        <TabsContent
          value="past"
          className="flex-1 flex flex-col mt-4 overflow-hidden"
        >
          <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
          <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
            <CardHeader>
              <CardTitle>Past Appointments</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {renderList(filteredPast, true)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={viewOpen} onOpenChange={setViewOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Appointment Details</DialogTitle>
            <DialogDescription>
              Detailed view of the selected appointment.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {detailIndex !== null && (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <p>
                    <span className="font-semibold">Date:</span>{" "}
                    {appointments[detailIndex].date}
                  </p>
                  <p>
                    <span className="font-semibold">Time:</span>{" "}
                    {appointments[detailIndex].time}
                  </p>
                  <p>
                    <span className="font-semibold">Doctor:</span>{" "}
                    {appointments[detailIndex].doctor}
                  </p>
                  <p>
                    <span className="font-semibold">Purpose:</span>{" "}
                    {appointments[detailIndex].purpose}
                  </p>
                  <p>
                    <span className="font-semibold">Location:</span>{" "}
                    {appointments[detailIndex].location}
                  </p>
                </div>
                {appointments[detailIndex].date < todayStr && (
                {appointments[detailIndex].date < todayStr && (
                  <>
                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="text-lg font-semibold mb-2">
                        Prescription
                      </h4>
                      <p>
                        {appointments[detailIndex].prescription ||
                          "No prescription provided."}
                      </p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="text-lg font-semibold mb-2">
                        Doctor's Comments
                      </h4>
                      <p>
                        {appointments[detailIndex].comments ||
                          "No comments provided."}
                      </p>
                    </div>
                  </>
                )}
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AppointmentsPage;
