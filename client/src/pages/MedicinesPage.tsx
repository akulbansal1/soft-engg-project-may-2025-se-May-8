import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { PlusCircle, Edit, Trash2 } from "lucide-react";

import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

interface Medication {
  name: string;
  frequency: string;
  dosage: string;
  duration: string;
}

const MedicinesPage: React.FC = () => {
  const navigate = useNavigate();
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
  ]);
  const [pastMeds] = useState<Medication[]>([
    {
      name: "Lisinopril",
      frequency: "Once daily",
      dosage: "10mg",
      duration: "1 year",
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

  return (
    <div className="h-full min-h-[calc(100dvh-110px)] flex flex-col space-y-6">
      <div className="flex justify-between">
        <h2 className="text-2xl font-semibold">My Medicines</h2>
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
              className="cursor-pointer"
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
                className="cursor-pointer"
              />
              <Input
                name="dosage"
                value={newMed.dosage}
                onChange={handleChange}
                placeholder="Dosage (e.g., 20mg)"
                className="cursor-pointer"
              />
              <Input
                name="frequency"
                value={newMed.frequency}
                onChange={handleChange}
                placeholder="Frequency (e.g., Twice daily)"
                className="cursor-pointer"
              />
              <Input
                name="duration"
                value={newMed.duration}
                onChange={handleChange}
                placeholder="Duration (e.g., 3 months)"
                className="cursor-pointer"
              />
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setDialogOpen(false);
                  setEditingIndex(null);
                  setNewMed({
                    name: "",
                    frequency: "",
                    dosage: "",
                    duration: "",
                  });
                }}
                className="cursor-pointer"
              >
                Cancel
              </Button>
              <Button onClick={handleAddOrUpdate} className="cursor-pointer">
                {editingIndex !== null ? "Save Changes" : "Add"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <ScrollArea className="flex-grow">
        {/* Active Medications */}
        <Card className="mb-4">
          <CardHeader>
            <CardTitle>Active Medications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {activeMeds.map((med, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center border-b last:border-b-0 pb-2"
              >
                <div>
                  <p className="font-medium">{med.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {med.dosage}, {med.frequency}, {med.duration}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleEdit(idx)}
                    className="cursor-pointer"
                  >
                    <Edit size={16} />
                  </Button>
                  <Button
                    variant="destructive"
                    size="icon"
                    onClick={() => handleDelete(idx)}
                    className="cursor-pointer"
                  >
                    <Trash2 size={16} />
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Past Medications */}
        <Card>
          <CardHeader>
            <CardTitle>Past Medications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {pastMeds.map((med, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center border-b last:border-b-0 pb-2"
              >
                <div>
                  <p className="font-medium">{med.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {med.dosage}, {med.frequency}, {med.duration}
                  </p>
                </div>
                <Button
                  variant="destructive"
                  size="icon"
                  className="cursor-pointer"
                >
                  <Trash2 size={16} />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </ScrollArea>
    </div>
  );
};

export default MedicinesPage;
