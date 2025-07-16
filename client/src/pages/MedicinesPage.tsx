import React, { useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PlusCircle, Edit, Trash2, Search, ArrowLeft } from "lucide-react";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

interface Medication {
  name: string;
  frequency: string;
  dosage: string;
  startDate: string;
  endDate: string;
}

const initialActive: Medication[] = [
  {
    name: "Atorvastatin",
    frequency: "Once daily",
    dosage: "20mg",
    startDate: "2025-01-10",
    endDate: "2025-04-10",
  },
  {
    name: "Metformin",
    frequency: "Twice daily",
    dosage: "500mg",
    startDate: "2025-02-01",
    endDate: "2025-08-01",
  },
  {
    name: "Combiflame",
    frequency: "Thrice daily",
    dosage: "30mg",
    startDate: "2025-02-06",
    endDate: "2025-08-08",
  },
];
const initialPast: Medication[] = [
  {
    name: "Lisinopril",
    frequency: "Once daily",
    dosage: "10mg",
    startDate: "2024-03-01",
    endDate: "2025-03-01",
  },
  {
    name: "Omeprazole",
    frequency: "Once daily",
    dosage: "20mg",
    startDate: "2023-06-15",
    endDate: "2023-08-15",
  },
];

const medicationSchema = yup.object().shape({
  name: yup.string().required("Medicine name is required"),
  frequency: yup.string().required("Frequency is required"),
  dosage: yup.string().required("Dosage is required"),
  startDate: yup.string().required("Start date is required"),
  endDate: yup.string().required("End date is required"),
});

const MedicinesPage: React.FC = () => {
  const [activeMeds, setActiveMeds] = useState<Medication[]>(initialActive);
  const [pastMeds] = useState<Medication[]>(initialPast);

  const [newMed, setNewMed] = useState<Medication>({
    name: "",
    frequency: "",
    dosage: "",
    startDate: "",
    endDate: "",
  });
  const [errors, setErrors] = useState<
    Partial<Record<keyof Medication, string>>
  >({});
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("active");

  const [startDateObj, setStartDateObj] = useState<Date | undefined>(undefined);
  const [endDateObj, setEndDateObj] = useState<Date | undefined>(undefined);

  // Clear error for field on change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewMed((prev) => ({ ...prev, [name]: value }));
    if (errors[name as keyof Medication]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name as keyof Medication];
        return next;
      });
    }
  };

  const handleAddOrUpdate = async () => {
    try {
      await medicationSchema.validate(newMed, { abortEarly: false });
      if (editingIndex !== null) {
        const updated = [...activeMeds];
        updated[editingIndex] = newMed;
        setActiveMeds(updated);
      } else {
        setActiveMeds((prev) => [...prev, newMed]);
      }
      // Reset form
      setNewMed({
        name: "",
        frequency: "",
        dosage: "",
        startDate: "",
        endDate: "",
      });
      setStartDateObj(undefined);
      setEndDateObj(undefined);
      setEditingIndex(null);
      setDialogOpen(false);
      setErrors({});
    } catch (err: any) {
      const fieldErrors: Partial<Record<keyof Medication, string>> = {};
      err.inner?.forEach((e: any) => {
        if (e.path) fieldErrors[e.path as keyof Medication] = e.message;
      });
      setErrors(fieldErrors);
    }
  };

  const handleEdit = (idx: number) => {
    const med = activeMeds[idx];
    setNewMed(med);
    setStartDateObj(new Date(med.startDate));
    setEndDateObj(new Date(med.endDate));
    setEditingIndex(idx);
    setDialogOpen(true);
    setErrors({});
  };

  const handleDelete = (idx: number) => {
    setActiveMeds((prev) => prev.filter((_, i) => i !== idx));
  };

  const filteredActiveMeds = useMemo(
    () =>
      activeMeds.filter(
        (med) =>
          med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          med.dosage.toLowerCase().includes(searchTerm.toLowerCase()) ||
          med.frequency.toLowerCase().includes(searchTerm.toLowerCase())
      ),
    [activeMeds, searchTerm]
  );
  const filteredPastMeds = useMemo(
    () =>
      pastMeds.filter(
        (med) =>
          med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          med.dosage.toLowerCase().includes(searchTerm.toLowerCase()) ||
          med.frequency.toLowerCase().includes(searchTerm.toLowerCase())
      ),
    [pastMeds, searchTerm]
  );

  const renderMedicationList = (meds: Medication[], isActive = true) => (
    <div className="space-y-4">
      {meds.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No medications found</p>
          {searchTerm && (
            <p className="text-xs">Try adjusting your search terms</p>
          )}
        </div>
      ) : (
        meds.map((med, idx) => (
          <Card key={idx} className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold text-lg mb-2">{med.name}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="bg-zinc-100 dark:bg-zinc-800 rounded-full px-2 py-1 text-xs">
                    {med.dosage}
                  </span>
                  <span className="bg-zinc-100 dark:bg-zinc-800 rounded-full px-2 py-1 text-xs">
                    {med.frequency}
                  </span>
                  <span className="bg-zinc-100 dark:bg-zinc-800 rounded-full px-2 py-1 text-xs">
                    Start: {med.startDate}
                  </span>
                  <span className="bg-zinc-100 dark:bg-zinc-800 rounded-full px-2 py-1 text-xs">
                    End: {med.endDate}
                  </span>
                </div>
              </div>
              <div className="flex space-x-2">
                {isActive && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEdit(idx)}
                  >
                    <Edit size={16} />
                  </Button>
                )}
                <Button
                  variant="destructive"
                  size="icon"
                  onClick={() => isActive && handleDelete(idx)}
                >
                  <Trash2 size={16} />
                </Button>
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );

  const navigate = useNavigate();

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
          My Medicines
        </h2>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setEditingIndex(null);
                setNewMed({
                  name: "",
                  frequency: "",
                  dosage: "",
                  startDate: "",
                  endDate: "",
                });
                setStartDateObj(undefined);
                setEndDateObj(undefined);
                setErrors({});
              }}
            >
              <PlusCircle className="mr-2" /> Add
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingIndex !== null ? "Edit Medication" : "Add Medication"}
              </DialogTitle>
              <DialogDescription>
                {editingIndex !== null
                  ? "Update the medication details below."
                  : "Enter details of the new medication below."}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div>
                <Input
                  name="name"
                  value={newMed.name}
                  onChange={handleChange}
                  placeholder="Medicine Name"
                />
                {errors.name && (
                  <p className="text-xs text-red-500 mt-1">{errors.name}</p>
                )}
              </div>
              <div>
                <Input
                  name="dosage"
                  value={newMed.dosage}
                  onChange={handleChange}
                  placeholder="Dosage (e.g., 20mg)"
                />
                {errors.dosage && (
                  <p className="text-xs text-red-500 mt-1">{errors.dosage}</p>
                )}
              </div>
              <div>
                <Input
                  name="frequency"
                  value={newMed.frequency}
                  onChange={handleChange}
                  placeholder="Frequency (e.g., Twice daily)"
                />
                {errors.frequency && (
                  <p className="text-xs text-red-500 mt-1">
                    {errors.frequency}
                  </p>
                )}
              </div>
              <div>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full text-left justify-start"
                    >
                      {startDateObj
                        ? format(startDateObj, "yyyy-MM-dd")
                        : "Select Start Date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={startDateObj}
                      onSelect={(d) => {
                        setStartDateObj(d);
                        const str = d ? format(d, "yyyy-MM-dd") : "";
                        setNewMed((prev) => ({ ...prev, startDate: str }));
                        if (errors.startDate)
                          setErrors((prev) => {
                            const next = { ...prev };
                            delete next.startDate;
                            return next;
                          });
                      }}
                      captionLayout="dropdown"
                    />
                  </PopoverContent>
                </Popover>
                {errors.startDate && (
                  <p className="text-xs text-red-500 mt-1">
                    {errors.startDate}
                  </p>
                )}
              </div>
              <div>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full text-left justify-start"
                    >
                      {endDateObj
                        ? format(endDateObj, "yyyy-MM-dd")
                        : "Select End Date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={endDateObj}
                      onSelect={(d) => {
                        setEndDateObj(d);
                        const str = d ? format(d, "yyyy-MM-dd") : "";
                        setNewMed((prev) => ({ ...prev, endDate: str }));
                        if (errors.endDate)
                          setErrors((prev) => {
                            const next = { ...prev };
                            delete next.endDate;
                            return next;
                          });
                      }}
                      captionLayout="dropdown"
                    />
                  </PopoverContent>
                </Popover>
                {errors.endDate && (
                  <p className="text-xs text-red-500 mt-1">{errors.endDate}</p>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddOrUpdate}>
                {editingIndex !== null ? "Save Changes" : "Add"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search medicines..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="active">
            Active Medications ({filteredActiveMeds.length})
          </TabsTrigger>
          <TabsTrigger value="past">
            Past Medications ({filteredPastMeds.length})
          </TabsTrigger>
        </TabsList>
        <TabsContent value="active" className="flex-1 mt-4 overflow-hidden">
          <Card className="flex flex-col h-full bg-transparent">
            <CardHeader>
              <CardTitle>Active Medications</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {renderMedicationList(filteredActiveMeds, true)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="past" className="flex-1 mt-4 overflow-hidden">
          <Card className="flex flex-col h-full bg-transparent">
            <CardHeader>
              <CardTitle>Past Medications</CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {renderMedicationList(filteredPastMeds, false)}
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default MedicinesPage;
