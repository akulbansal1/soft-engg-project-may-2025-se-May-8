import React, { useEffect, useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  ArrowLeft,
  Calendar as CalendarIcon,
  Clock,
  Stethoscope,
  MapPin,
  FileText,
  MessageSquare,
  HelpCircle,
  ListChecks,
  MousePointerClick,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
  type CarouselApi,
} from "@/components/ui/carousel";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Calendar } from "@/components/ui/calendar";

const BASE_URL = "/api/v1";

interface Doctor {
  id: number;
  name: string;
  location: string;
}

interface Appointment {
  id: number;
  name: string; // Purpose of the appointment
  date: string;
  time: string;
  notes?: string;
  doctor_id: number;
  doctor?: Doctor; // Embed the full doctor object
}

// Helper function for robust date parsing
const parseDate = (dateStr: string) => new Date(dateStr.replace(/\//g, "-"));

const AppointmentsPage: React.FC = () => {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [viewOpen, setViewOpen] = useState(false);
  const [tutorialOpen, setTutorialOpen] = useState(false);
  const [selectedAppointment, setSelectedAppointment] =
    useState<Appointment | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(
    new Date()
  );
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      setIsLoading(true);

      const fetchAppointmentsAndDoctors = async () => {
        try {
          const apptRes = await fetch(
            `${BASE_URL}/appointments/user/${user.id}`
          );
          if (!apptRes.ok) throw new Error("Failed to fetch appointments");
          let appointmentsData: Appointment[] = await apptRes.json();

          if (appointmentsData.length === 0) {
            setAppointments([]);
            setIsLoading(false);
            return;
          }

          const doctorIds = [
            ...new Set(appointmentsData.map((apt) => apt.doctor_id)),
          ];
          const doctorPromises = doctorIds.map((id) =>
            fetch(`${BASE_URL}/doctors/${id}`).then((res) => res.json())
          );
          const doctorsData: Doctor[] = await Promise.all(doctorPromises);
          const doctorsMap = new Map(doctorsData.map((doc) => [doc.id, doc]));

          const enrichedAppointments = appointmentsData.map((apt) => ({
            ...apt,
            doctor: doctorsMap.get(apt.doctor_id),
          }));

          setAppointments(enrichedAppointments);
        } catch (err) {
          console.error("Fetch appointments error:", err);
          toast.error("Could not load your appointments.");
          setAppointments([]); // Set to empty array on error
        } finally {
          setIsLoading(false);
        }
      };

      fetchAppointmentsAndDoctors();
    } else {
      setIsLoading(false); // If there's no user, stop loading
    }
  }, [user]);

  const { upcomingAppointments, pastAppointments, appointmentsByDate } =
    useMemo<{
      upcomingAppointments: Appointment[];
      pastAppointments: Appointment[];
      appointmentsByDate: Map<string, Appointment[]>;
    }>(() => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const upcoming: Appointment[] = [];
      const past: Appointment[] = [];
      const byDate = new Map<string, Appointment[]>();

      appointments.forEach((appt) => {
        const apptDate = parseDate(appt.date);
        apptDate.setHours(0, 0, 0, 0);

        const dateKey = apptDate.toDateString();
        if (!byDate.has(dateKey)) byDate.set(dateKey, []);
        byDate.get(dateKey)!.push(appt);

        if (apptDate >= today) {
          upcoming.push(appt);
        } else {
          past.push(appt);
        }
      });

      upcoming.sort(
        (a, b) => parseDate(a.date).getTime() - parseDate(b.date).getTime()
      );
      past.sort(
        (a, b) => parseDate(b.date).getTime() - parseDate(a.date).getTime()
      );

      return {
        upcomingAppointments: upcoming,
        pastAppointments: past,
        appointmentsByDate: byDate,
      };
    }, [appointments]);

  const filterAppointments = (appts: Appointment[]) => {
    if (!searchTerm) return appts;
    const term = searchTerm.toLowerCase();
    return appts.filter(
      (appt) =>
        appt.name.toLowerCase().includes(term) ||
        (appt.doctor?.name && appt.doctor.name.toLowerCase().includes(term)) ||
        (appt.doctor?.location &&
          appt.doctor.location.toLowerCase().includes(term))
    );
  };

  const filteredUpcoming = filterAppointments(upcomingAppointments);
  const filteredPast = filterAppointments(pastAppointments);
  const dailyAppointments =
    appointmentsByDate.get(selectedDate?.toDateString() || "") || [];

  const openViewDialog = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setViewOpen(true);
  };

  const renderList = (list: Appointment[]) => (
    <div className="space-y-4">
      {list.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No appointments found.</p>
          {searchTerm && <p className="text-xs">Try adjusting your search.</p>}
        </div>
      ) : (
        list.map((appt) => (
          <Card
            key={appt.id}
            className="p-4 cursor-pointer hover:bg-muted/50 transition-colors bg-transparent"
            onClick={() => openViewDialog(appt)}
          >
            <div className="flex items-start gap-4">
              <CalendarIcon className="h-6 w-6 text-primary mt-1 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-lg truncate">{appt.name}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                  <span>with {appt.doctor?.name || "Unknown Doctor"}</span>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-2">
                  <span>
                    {appt.date} at {appt.time}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );

  const SkeletonLoader = () => (
    <div className="space-y-4 pt-4 animate-pulse">
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="p-4 bg-transparent">
          <div className="flex items-start">
            <div className="h-6 w-6 bg-muted rounded-full mr-4 mt-1"></div>
            <div className="w-full">
              <div className="h-6 w-1/2 bg-muted rounded mb-2"></div>
              <div className="h-4 w-3/4 bg-muted rounded mb-2"></div>
              <div className="h-3 w-full bg-muted rounded"></div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/home")}
            className="mr-4"
          >
            <ArrowLeft size={20} />
          </Button>
          My Appointments
          <Button
            variant="ghost"
            size="icon"
            className="ml-2 rounded-full"
            onClick={() => setTutorialOpen(true)}
          >
            <HelpCircle className="h-5 w-5 text-muted-foreground" />
          </Button>
        </h2>
      </div>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search by purpose, doctor..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <Tabs
        defaultValue="upcoming"
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="calendar">Calendar</TabsTrigger>
          <TabsTrigger value="upcoming" className="flex items-center gap-2">
            Upcoming{" "}
            <Badge variant="secondary">{filteredUpcoming.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="past" className="flex items-center gap-2">
            Past <Badge variant="secondary">{filteredPast.length}</Badge>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calendar" className="flex-1 mt-4 overflow-hidden">
          <div className="flex flex-col md:flex-row gap-6 h-full">
            <div className="w-full md:w-auto flex justify-center">
              <Calendar
                mode="single"
                selected={selectedDate}
                onSelect={setSelectedDate}
                modifiers={{
                  hasUpcomingAppointment: (date) => {
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
                  hasUpcomingAppointment: "bg-blue-500/20 text-blue-foreground",
                  hasPastAppointment: "bg-green-500/20 text-green-foreground",
                }}
                className="rounded-md bg-transparent"
              />
            </div>
            <Card className="flex-1 flex flex-col bg-transparent border rounded-lg overflow-hidden">
              <CardHeader>
                <CardTitle>
                  {selectedDate?.toDateString() || "Select a date"}
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 p-4">
                <ScrollArea className="h-full pr-4">
                  {renderList(dailyAppointments)}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="upcoming" className="flex-1 mt-4 overflow-hidden">
          <Card className="h-full bg-transparent border rounded-lg overflow-hidden">
            <CardContent className="h-full p-4">
              <ScrollArea className="h-full pr-4">
                {isLoading ? <SkeletonLoader /> : renderList(filteredUpcoming)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="past" className="flex-1 mt-4 overflow-hidden">
          <Card className="h-full bg-transparent border rounded-lg overflow-hidden">
            <CardContent className="h-full p-4">
              <ScrollArea className="h-full pr-4">
                {isLoading ? <SkeletonLoader /> : renderList(filteredPast)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <TutorialDialog open={tutorialOpen} onOpenChange={setTutorialOpen} />

      <Dialog open={viewOpen} onOpenChange={setViewOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle className="text-2xl">
              {selectedAppointment?.name}
            </DialogTitle>
            <DialogDescription>
              A summary of your appointment with{" "}
              {selectedAppointment?.doctor?.name}.
            </DialogDescription>
          </DialogHeader>
          {selectedAppointment && (
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm p-4 border rounded-lg bg-muted/30">
                <InfoItem
                  icon={CalendarIcon}
                  label="Date"
                  value={selectedAppointment.date}
                />
                <InfoItem
                  icon={Clock}
                  label="Time"
                  value={selectedAppointment.time}
                />
                <InfoItem
                  icon={Stethoscope}
                  label="Doctor"
                  value={selectedAppointment.doctor?.name}
                />
                <InfoItem
                  icon={MapPin}
                  label="Location"
                  value={selectedAppointment.doctor?.location}
                />
              </div>
              <div className="p-4 bg-muted/30 rounded-lg space-y-2">
                <h4 className="font-semibold flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" /> Doctor's Notes
                </h4>
                <p className="text-muted-foreground text-sm pl-6">
                  {selectedAppointment.notes || "No notes provided."}
                </p>
              </div>
            </div>
          )}
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

const InfoItem = ({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value?: string;
}) => (
  <div className="flex items-start gap-3">
    <Icon className="w-4 h-4 mt-1 text-primary" />
    <div>
      <p className="text-muted-foreground">{label}</p>
      <p className="font-semibold">{value || "N/A"}</p>
    </div>
  </div>
);

const TutorialDialog = ({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) => {
  const [api, setApi] = React.useState<CarouselApi>();
  const [current, setCurrent] = React.useState(0);
  const [count, setCount] = React.useState(0);

  React.useEffect(() => {
    if (!api) {
      return;
    }

    setCount(api.scrollSnapList().length);
    setCurrent(api.selectedScrollSnap() + 1);

    api.on("select", () => {
      setCurrent(api.selectedScrollSnap() + 1);
    });
  }, [api]);

  const tutorialSteps = [
    {
      icon: CalendarIcon,
      title: "Calendar View",
      description:
        "Use the calendar to see appointments at a glance. Upcoming dates are blue, and past ones are green.",
    },
    {
      icon: ListChecks,
      title: "List Views",
      description:
        "Switch between 'Upcoming' and 'Past' tabs to see a detailed list of your appointments.",
    },
    {
      icon: Search,
      title: "Quick Search",
      description:
        "Use the search bar to find any appointment by its purpose, doctor's name, or location.",
    },
    {
      icon: MousePointerClick,
      title: "View Details",
      description:
        "Click on any appointment card to open a detailed view with all the information.",
    },
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>How to Use This Page</DialogTitle>
          <DialogDescription>
            A quick guide to managing your appointments.
          </DialogDescription>
        </DialogHeader>
        <Carousel setApi={setApi}>
          <CarouselContent>
            {tutorialSteps.map((step, index) => (
              <CarouselItem key={index}>
                <div className="p-1">
                  <div className="flex flex-col items-center justify-center p-6 text-center space-y-4 h-64">
                    <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                      <step.icon className="w-8 h-8 text-primary" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold">{step.title}</h3>
                      <p className="text-muted-foreground text-balance px-4">
                        {step.description}
                      </p>
                    </div>
                  </div>
                </div>
              </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
        <div className="text-muted-foreground py-2 text-center text-sm">
          Step {current} of {count}
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            className="w-full"
            onClick={() => onOpenChange(false)}
          >
            Got it!
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default AppointmentsPage;
