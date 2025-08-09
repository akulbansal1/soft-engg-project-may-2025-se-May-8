import React, { useEffect, useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, ArrowLeft, Pill } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";

const BASE_URL = "/api/v1";

interface Medication {
  id: number;
  name: string;
  frequency: string;
  dosage: string;
  start_date: string; // Assuming snake_case from backend
  end_date: string; // Assuming snake_case from backend
}

const MedicinesPage: React.FC = () => {
  const { user } = useAuth();
  const [medications, setMedications] = useState<Medication[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      setIsLoading(true);
      fetch(`${BASE_URL}/medicines/user/${user.id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch medications");
          return res.json();
        })
        .then((data: Medication[]) => setMedications(data))
        .catch((err) => {
          console.error("Fetch medicines error:", err);
          toast.error("Could not load your medications.");
        })
        .finally(() => setIsLoading(false));
    }
  }, [user]);

  const { activeMeds, pastMeds } = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Set to start of day for accurate comparison

    const active: Medication[] = [];
    const past: Medication[] = [];

    medications.forEach((med) => {
      const endDate = new Date(med.end_date);
      if (endDate >= today) {
        active.push(med);
      } else {
        past.push(med);
      }
    });
    return { activeMeds: active, pastMeds: past };
  }, [medications]);

  const filterMeds = (meds: Medication[]) => {
    if (!searchTerm) return meds;
    const term = searchTerm.toLowerCase();
    return meds.filter(
      (med) =>
        med.name.toLowerCase().includes(term) ||
        med.dosage.toLowerCase().includes(term) ||
        med.frequency.toLowerCase().includes(term)
    );
  };

  const filteredActiveMeds = filterMeds(activeMeds);
  const filteredPastMeds = filterMeds(pastMeds);

  const renderMedicationList = (meds: Medication[]) => (
    <div className="space-y-4">
      {meds.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No medications found.</p>
          {searchTerm && <p className="text-xs">Try adjusting your search.</p>}
        </div>
      ) : (
        meds.map((med) => (
          <Card key={med.id} className="p-4">
            <div className="flex items-start">
              <Pill className="h-6 w-6 text-primary mr-4 mt-1 flex-shrink-0" />
              <div>
                <p className="font-semibold text-lg">{med.name}</p>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground mt-1">
                  <span>Dosage: {med.dosage}</span>
                  <span>Frequency: {med.frequency}</span>
                </div>
                <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground mt-2">
                  <span>Start: {med.start_date}</span>
                  <span>End: {med.end_date}</span>
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
        <Card key={i} className="p-4">
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
          My Medicines
        </h2>
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
        defaultValue="active"
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="active" className="flex items-center gap-2">
            Active{" "}
            <Badge variant="secondary">{filteredActiveMeds.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="past" className="flex items-center gap-2">
            Past <Badge variant="secondary">{filteredPastMeds.length}</Badge>
          </TabsTrigger>
        </TabsList>

        <Card className="flex-1 mt-4 overflow-hidden border bg-transparent rounded-lg">
          <CardContent className="h-full p-4">
            <TabsContent value="active" className="h-full overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {isLoading ? (
                  <SkeletonLoader />
                ) : (
                  renderMedicationList(filteredActiveMeds)
                )}
              </ScrollArea>
            </TabsContent>
            <TabsContent value="past" className="h-full overflow-hidden">
              <ScrollArea className="h-full pr-4">
                {isLoading ? (
                  <SkeletonLoader />
                ) : (
                  renderMedicationList(filteredPastMeds)
                )}
              </ScrollArea>
            </TabsContent>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
};

export default MedicinesPage;
