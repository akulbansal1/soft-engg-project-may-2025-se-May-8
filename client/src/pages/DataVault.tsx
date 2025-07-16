import React, { useRef, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Trash2,
  FileText,
  Eye,
  Upload,
  Pencil,
  Search,
  ArrowLeft,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { useNavigate } from "react-router-dom";
import * as yup from "yup";

interface Document {
  id: number;
  name: string;
  type: string;
  date: string;
  fileUrl: string;
}

const uploadSchema = yup.object().shape({
  name: yup.string().required("Document name is required"),
  file: yup.mixed().required("Please select a file"),
});

const DataVault: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [uploadErrors, setUploadErrors] = useState<{
    name?: string;
    file?: string;
  }>({});
  const [searchTerm, setSearchTerm] = useState("");
  const reuploadRefs = useRef<Record<number, HTMLInputElement | null>>({});
  const navigate = useNavigate();
  


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

  const handleAddDocument = async () => {
    try {
      await uploadSchema.validate(
        { name: uploadName, file: uploadFile },
        { abortEarly: false }
      );
      if (!uploadFile) return;
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
      setUploadErrors({});
    } catch (err: any) {
      if (err.inner) {
        const fieldErrors: { name?: string; file?: string } = {};
        err.inner.forEach((e: any) => {
          if (e.path) fieldErrors[e.path as "name" | "file"] = e.message;
        });
        setUploadErrors(fieldErrors);
      }
    }
  };

  const filteredDocuments = documents.filter(
    (doc) =>
      doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.date.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderDocumentList = (docs: Document[]) => (
    <div className="space-y-4">
      {docs.length === 0 ? (
        <div className="text-center py-8 text-muted-foreground">
          <p>No documents found.</p>
        </div>
      ) : (
        docs.map((doc) => (
          <Card key={doc.id} className="p-4">
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-3">
                <FileText className="h-6 w-6 text-primary" />
                <div>
                  {editingId === doc.id ? (
                    <Input
                      defaultValue={doc.name}
                      onBlur={(e) => handleRename(doc.id, e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter")
                          handleRename(
                            doc.id,
                            (e.target as HTMLInputElement).value
                          );
                      }}
                      autoFocus
                      className="text-base w-48"
                    />
                  ) : (
                    <p className="font-semibold text-lg">{doc.name}</p>
                  )}
                  <p className="text-sm text-muted-foreground">{doc.type}</p>
                  <p className="text-xs text-muted-foreground">{doc.date}</p>
                </div>
              </div>
              <div className="flex space-x-2">
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
              </div>
            </div>
          </Card>
        ))
      )}
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
          Data Vault
        </h2>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <Upload className="mr-2 h-4 w-4" /> Add Document
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Document</DialogTitle>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div>
                <Input
                  placeholder="Document Name"
                  value={uploadName}
                  onChange={(e) => {
                    setUploadName(e.target.value);
                    setUploadErrors((prev) => ({ ...prev, name: "" }));
                  }}
                />
                {uploadErrors.name && (
                  <p className="text-red-500 text-xs mt-1">
                    {uploadErrors.name}
                  </p>
                )}
              </div>
              <div>
                <Input
                  type="file"
                  onChange={(e) => {
                    setUploadFile(e.target.files?.[0] || null);
                    setUploadErrors((prev) => ({ ...prev, file: "" }));
                  }}
                />
                {uploadErrors.file && (
                  <p className="text-red-500 text-xs mt-1">
                    {uploadErrors.file}
                  </p>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddDocument}>Upload</Button>
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
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      <Card className="flex-1 bg-transparent">
        <CardHeader>
          <CardTitle>Documents ({filteredDocuments.length})</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            {renderDocumentList(filteredDocuments)}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default DataVault;
