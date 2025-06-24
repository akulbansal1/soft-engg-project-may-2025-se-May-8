import React, { useRef, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Trash2, FileText, Eye, Upload, Pencil, Search } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

interface Document {
  id: number;
  name: string;
  type: string;
  date: string;
  fileUrl: string;
}

const DataVault: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const reuploadRefs = useRef<Record<number, HTMLInputElement | null>>({});

  const handleDelete = (id: number) => {
    setDocuments((prev) => prev.filter((doc) => doc.id !== id));
  };

  const handleReupload = (
    e: React.ChangeEvent<HTMLInputElement>,
    id: number
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const fileUrl = URL.createObjectURL(file);
    setDocuments((prev) =>
      prev.map((doc) =>
        doc.id === id
          ? { ...doc, name: file.name, type: file.type, fileUrl }
          : doc
      )
    );
    e.target.value = "";
  };

  const handleRename = (id: number, newName: string) => {
    setDocuments((prev) =>
      prev.map((doc) => (doc.id === id ? { ...doc, name: newName } : doc))
    );
    setEditingId(null);
  };

  const handleAddDocument = () => {
    if (!uploadFile || !uploadName) return;
    const newDoc: Document = {
      id: Date.now(),
      name: uploadName,
      type: uploadFile.type || "Unknown",
      date: new Date().toLocaleDateString(),
      fileUrl: URL.createObjectURL(uploadFile),
    };
    setDocuments((prev) => [...prev, newDoc]);
    setUploadFile(null);
    setUploadName("");
    setDialogOpen(false);
  };

  const filteredDocuments = documents.filter(
    (doc) =>
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.date.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-semibold">Data Vault</h2>
          <p className="text-sm text-muted-foreground">
            Your important medical documents
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <Button variant="outline" onClick={() => setDialogOpen(true)}>
            <Upload className="mr-2 h-4 w-4" /> Add Document
          </Button>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Document</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <Input
                placeholder="Document Name"
                value={uploadName}
                onChange={(e) => setUploadName(e.target.value)}
              />
              <Input
                type="file"
                onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
              />
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleAddDocument}
                disabled={!uploadFile || !uploadName}
              >
                Upload
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          size={16}
        />
        <Input
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <ScrollArea className="flex-1 pr-4">
        {filteredDocuments.length === 0 ? (
          <div className="text-center py-10 text-muted-foreground">
            No documents found.
          </div>
        ) : (
          <div className="grid gap-4 grid-cols-1">
            {filteredDocuments.map((doc) => (
              <Card key={doc.id}>
                <div className="flex justify-between items-start">
                  <CardHeader className="flex w-[90%] space-x-2">
                    <FileText className="h-6 w-6 text-primary mt-1" />
                    <CardTitle className="space-y-1">
                      {editingId === doc.id ? (
                        <Input
                          defaultValue={doc.name}
                          onBlur={(e) => handleRename(doc.id, e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              handleRename(
                                doc.id,
                                (e.target as HTMLInputElement).value
                              );
                            }
                          }}
                          autoFocus
                          className="text-base"
                        />
                      ) : (
                        <>
                          <p className="text-base">{doc.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {doc.type}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {doc.date}
                          </p>
                        </>
                      )}
                    </CardTitle>
                  </CardHeader>

                  <CardContent className="flex gap-2 items-center">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => window.open(doc.fileUrl, "_blank")}
                    >
                      <Eye size={16} />
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setEditingId(doc.id)}
                    >
                      <Pencil size={16} />
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => reuploadRefs.current[doc.id]?.click()}
                    >
                      <Upload size={16} />
                    </Button>
                    <input
                      type="file"
                      ref={(ref) => (reuploadRefs.current[doc.id] = ref)}
                      onChange={(e) => handleReupload(e, doc.id)}
                      className="hidden"
                    />

                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => handleDelete(doc.id)}
                    >
                      <Trash2 size={16} />
                    </Button>
                  </CardContent>
                </div>
              </Card>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default DataVault;
