import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Eye } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

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
  ]);
  const [viewOpen, setViewOpen] = useState<boolean>(false);
  const [detailIndex, setDetailIndex] = useState<number | null>(null);

  const openView = (idx: number) => {
    setDetailIndex(idx);
    setViewOpen(true);
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col space-y-6">
      <h2 className="text-2xl font-semibold">My Appointments</h2>

      <ScrollArea className="flex-grow">
        <Card>
          <CardHeader>
            <CardTitle>Appointments List</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {appointments.map((appt, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center border-b pb-2"
              >
                <div>
                  <p className="font-medium">
                    {appt.date} @ {appt.time}
                  </p>
                  <p className="text-sm text-muted-foreground">{appt.doctor}</p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="hover:cursor-pointer"
                    onClick={() => openView(idx)}
                  >
                    <Eye size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </ScrollArea>

      <Dialog open={viewOpen} onOpenChange={setViewOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Appointment Details</DialogTitle>
            <DialogDescription>
              Details of the selected appointment.
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
                <div className="p-4 bg-muted rounded-lg">
                  <h4 className="text-lg font-semibold mb-2">Prescription</h4>
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
