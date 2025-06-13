import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2, FileText, Eye } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from "react-router-dom";

const initialDocuments = [
  {
    id: 1,
    name: "Blood Test Report",
    type: "Lab Report",
    date: "10 June 2025",
  },
  {
    id: 2,
    name: "Prescription May 2025",
    type: "Doctor Prescription",
    date: "05 May 2025",
  },
];

const DataVault: React.FC = () => {
  const [documents, setDocuments] = useState(initialDocuments);

  const handleDelete = (id: number) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  return (
    <div className="h-full min-h-[calc(100dvh-110px)]">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold">Data Vault</h2>
          <p className="text-muted-foreground mb-5 text-sm">
            Your important medical documents
          </p>
        </div>
        <div>
          <Button variant="outline" className="hover:cursor-pointer">
            Add Document
          </Button>
        </div>
      </div>

      <Separator />

      <div className="grid gap-4 grid-cols-1">
        {documents.map((doc) => (
          <Card key={doc.id} className="relative">
            <div className="flex justify-between">
              <CardHeader className="flex w-[90%]">
                <FileText className="h-6 w-6 text-primary mb-2" />
                <CardTitle>
                  {doc.name}
                  <p className="text-sm text-muted-foreground">{doc.type}</p>
                  <p className="text-xs text-muted-foreground">{doc.date}</p>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex gap-3">
                <Button
                  variant="secondary"
                  size="sm"
                  className="bg-transparent hover:cursor-pointer"
                >
                  <Eye />
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  className="hover:cursor-pointer"
                  onClick={() => handleDelete(doc.id)}
                >
                  <Trash2 />
                </Button>
              </CardContent>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default DataVault;
