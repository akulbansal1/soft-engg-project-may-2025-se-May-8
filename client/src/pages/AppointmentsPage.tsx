import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Eye, Search } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

interface Appointment {
  date: string;
  time: string;
  doctor: string;
  purpose: string;
  location: string;
  prescription?: string;
  comments?: string;
}

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
  const [tab, setTab] = useState("upcoming");

  const today = new Date().toISOString().split("T")[0];

  const filteredUpcoming = useMemo(() => {
    return appointments
      .filter((a) => a.date >= today)
      .filter((a) =>
        [a.date, a.time, a.doctor, a.purpose, a.location].some((field) =>
          field.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [appointments, searchTerm]);

  const filteredPast = useMemo(() => {
    return appointments
      .filter((a) => a.date < today)
      .filter((a) =>
        [
          a.date,
          a.time,
          a.doctor,
          a.purpose,
          a.location,
          a.prescription ?? "",
          a.comments ?? "",
        ].some((field) =>
          field.toLowerCase().includes(searchTerm.toLowerCase())
        )
      )
      .sort((a, b) => b.date.localeCompare(a.date));
  }, [appointments, searchTerm]);

  const openView = (idx: number) => {
    setDetailIndex(idx);
    setViewOpen(true);
  };

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <h2 className="text-2xl font-semibold">My Appointments</h2>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
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
        <TabsList className="grid grid-cols-2 w-full">
          <TabsTrigger value="upcoming">
            Upcoming ({filteredUpcoming.length})
          </TabsTrigger>
          <TabsTrigger value="past">Past ({filteredPast.length})</TabsTrigger>
        </TabsList>

        <TabsContent
          value="upcoming"
          className="flex-1 flex flex-col mt-4 overflow-hidden"
        >
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader>
              <CardTitle>Upcoming Appointments</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {filteredUpcoming.length === 0 ? (
                  <p className="text-muted-foreground text-center py-6">
                    No upcoming appointments.
                  </p>
                ) : (
                  filteredUpcoming.map((appt, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center border-b py-3"
                    >
                      <div>
                        <p className="font-medium">
                          {appt.date} @ {appt.time}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {appt.doctor} – {appt.purpose}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="hover:cursor-pointer"
                        onClick={() => openView(appointments.indexOf(appt))}
                      >
                        <Eye size={16} />
                      </Button>
                    </div>
                  ))
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent
          value="past"
          className="flex-1 flex flex-col mt-4 overflow-hidden"
        >
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader>
              <CardTitle>Past Appointments</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {filteredPast.length === 0 ? (
                  <p className="text-muted-foreground text-center py-6">
                    No past appointments.
                  </p>
                ) : (
                  filteredPast.map((appt, idx) => (
                    <div key={idx} className="border-b py-3">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">
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
                      <div className="mt-2 space-y-2">
                        <div className="p-2 bg-muted rounded text-sm">
                          <strong>Prescription:</strong>{" "}
                          {appt.prescription || "None"}
                        </div>
                        <div className="p-2 bg-muted rounded text-sm">
                          <strong>Doctor's Comments:</strong>{" "}
                          {appt.comments || "None"}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Appointment Details Dialog */}
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

                {/* Only show if appointment is in the past */}
                {appointments[detailIndex].date < today && (
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
