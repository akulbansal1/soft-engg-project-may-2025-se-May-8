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
import { useNavigate } from "react-router-dom";

interface Medication {
  name: string;
  frequency: string;
  dosage: string;
  duration: string;
}

// Add a start date, end date, notes (dialogue box). remove duration.
// Mic for dictating Prescription.

const MedicinesPage: React.FC = () => {
  const [activeMeds, setActiveMeds] = useState<Medication[]>([
    {
      name: "Atorvastatin",
      frequency: "Once daily",
      dosage: "20mg",
      duration: "3 months",
    },
    {
      name: "Metformin",
      frequency: "Twice daily",
      dosage: "500mg",
      duration: "6 months",
    },
    {
      name: "Amlodipine",
      frequency: "Once daily",
      dosage: "5mg",
      duration: "12 months",
    },
    {
      name: "Aspirin",
      frequency: "Once daily",
      dosage: "81mg",
      duration: "Ongoing",
    },
  ]);

  const [pastMeds] = useState<Medication[]>([
    {
      name: "Lisinopril",
      frequency: "Once daily",
      dosage: "10mg",
      duration: "1 year",
    },
    {
      name: "Omeprazole",
      frequency: "Once daily",
      dosage: "20mg",
      duration: "2 months",
    },
    {
      name: "Ibuprofen",
      frequency: "As needed",
      dosage: "400mg",
      duration: "1 week",
    },
  ]);

  const [newMed, setNewMed] = useState<Medication>({
    name: "",
    frequency: "",
    dosage: "",
    duration: "",
  });
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("active");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setNewMed((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddOrUpdate = () => {
    if (editingIndex !== null) {
      const updated = [...activeMeds];
      updated[editingIndex] = newMed;
      setActiveMeds(updated);
    } else {
      setActiveMeds((prev) => [...prev, newMed]);
    }
    setNewMed({ name: "", frequency: "", dosage: "", duration: "" });
    setEditingIndex(null);
    setDialogOpen(false);
  };

  const handleEdit = (idx: number) => {
    setNewMed(activeMeds[idx]);
    setEditingIndex(idx);
    setDialogOpen(true);
  };

  const handleDelete = (idx: number) => {
    setActiveMeds((prev) => prev.filter((_, i) => i !== idx));
  };

  const filteredActiveMeds = useMemo(() => {
    return activeMeds.filter(
      (med) =>
        med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.dosage.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.frequency.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.duration.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [activeMeds, searchTerm]);

  const filteredPastMeds = useMemo(() => {
    return pastMeds.filter(
      (med) =>
        med.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.dosage.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.frequency.toLowerCase().includes(searchTerm.toLowerCase()) ||
        med.duration.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [pastMeds, searchTerm]);

  const renderMedicationList = (meds: Medication[], isActive = true) => (
    <div className="space-y-3">
      {meds.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No medications found</p>
          {searchTerm && (
            <p className="text-sm">Try adjusting your search terms</p>
          )}
        </div>
      ) : (
        meds.map((med, idx) => (
          <div
            key={idx}
            className="flex justify-between items-center border-b last:border-b-0 pb-3 last:pb-0"
          >
            <div className="flex-1">
              <p className="font-medium text-lg">{med.name}</p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-1 mt-1">
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium">Dosage:</span> {med.dosage}
                </p>
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium">Frequency:</span>{" "}
                  {med.frequency}
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-1 mt-1">
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium">Start Date:</span> 12/03/2025
                </p>
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium">End Date:</span> 15/04/2025
                </p>
              </div>
            </div>
            <div className="flex space-x-2 ml-4">
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
                onClick={() => (isActive ? handleDelete(idx) : null)}
              >
                <Trash2 size={16} />
              </Button>
            </div>
          </div>
        ))
      )}
    </div>
  );

  const navigate = useNavigate();

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      {/* Header & Add Button */}
      <div className="flex justify-between">
        <h2 className="text-2xl font-semibold">
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
                  duration: "",
                });
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
              <Input
                name="name"
                value={newMed.name}
                onChange={handleChange}
                placeholder="Medicine Name"
              />
              <Input
                name="dosage"
                value={newMed.dosage}
                onChange={handleChange}
                placeholder="Dosage (e.g., 20mg)"
              />
              <Input
                name="frequency"
                value={newMed.frequency}
                onChange={handleChange}
                placeholder="Frequency (e.g., Twice daily)"
              />
              <Input
                name="duration"
                value={newMed.duration}
                onChange={handleChange}
                placeholder="Duration (e.g., 3 months)"
              />
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

      {/* Search */}
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

      {/* Tabs and Scrollable Content */}
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
